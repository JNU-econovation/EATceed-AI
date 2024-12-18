import os
import base64
import redis
from datetime import datetime, timedelta
from openai import OpenAI
from pinecone.grpc import PineconeGRPC as Pinecone
from errors.business_exception import RateLimitExceeded, ImageAnalysisError, ImageProcessingError
from errors.server_exception import FileAccessError, ServiceConnectionError, ExternalAPIError
from logs.logger_config import get_logger
import time

# 환경에 따른 설정 파일 로드
if os.getenv("APP_ENV") == "prod":
    from core.config_prod import settings
else:
    from core.config import settings

# 환경에 따른 설정 파일 로드
if os.getenv("APP_ENV") == "prod":

    # 운영: Redis 클라이언트 설정
    redis_client = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
else:
    # 개발: Redis 클라이언트 설정
    redis_client = redis.StrictRedis(
        host=settings.REDIS_LOCAL_HOST,  
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )

# 요청 제한 설정
RATE_LIMIT = settings.RATE_LIMIT  # 하루 최대 요청 가능 횟수

# 공용 로거
logger = get_logger()

# Chatgpt API 사용
client = OpenAI(api_key = settings.OPENAI_API_KEY)

# Pinecone 설정
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(host=settings.INDEX_HOST)


# Redis 기반 요청 제한 함수
def rate_limit_user(user_id: int, increment=False):
    redis_key = f"rate_limit:{user_id}"
    current_count = redis_client.get(redis_key)

    # 요청 횟수 확인
    if current_count:
        if int(current_count) >= RATE_LIMIT:
            logger.info(f"음식 이미지 분석 기능 횟수 제한: {user_id}")
            # 기능 횟수 제한 예외처리
            raise RateLimitExceeded()
    
    # 요청 성공시에만 증가
    if increment:
        redis_client.incr(redis_key)
        if current_count is None:
            # 매일 자정 횟수 리셋
            next_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            redis_client.expireat(redis_key, int(next_time.timestamp()))
    
    remaining_requests = RATE_LIMIT - int(current_count or 0) - (1 if increment else 0)

    return remaining_requests


# Multi-part 방식 이미지 처리 및 Base64 인코딩
async def process_image_to_base64(file):
    try:
        # 파일 읽기
        file_content = await file.read()

        # Base64 인코딩
        image_base64 = base64.b64encode(file_content).decode("utf-8")
        
        return image_base64
    except Exception as e:
        logger.error(f"이미지 파일 처리 및 Base64 인코딩 실패: {e}")
        raise ImageProcessingError()


# prompt를 불러오기
def read_prompt(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        prompt = file.read().strip()
    return prompt


# 음식 이미지 분석 API: prompt_type은 함수명과 동일
def food_image_analyze(image_base64: str):

    # prompt 타입 설정
    prompt_file = os.path.join(settings.PROMPT_PATH, "food_image_analyze.txt")
    prompt = read_prompt(prompt_file)

    # prompt 내용 없을 경우
    if not prompt:
        logger.error("food_image_analyze.txt에 prompt 내용 미존재")
        raise FileAccessError()

    # OpenAI API 호출
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                            # 성능이 좋아지지만, token 소모 큼(tradeoff): 검증 필요
                            # "detail": "high"
                        }
                    }
                ]
            }
        ],
        temperature=0.0,
        max_tokens=300
    )
    
    result = response.choices[0].message.content

    # 음식명(반환값)이 존재하지 않을 경우
    if not result:
        logger.error("OpenAI API 음식명 얻기 실패")
        raise ImageAnalysisError()

    # 음식 이미지 분석 
    return result


# 제공받은 음식의 벡터 임베딩 값 변환 작업 수행
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    embedding = client.embeddings.create(input=[text], model=model).data[0].embedding
    return embedding


# 벡터 임베딩을 통한 유사도 분석 진행(Pinecone)
def search_similar_food(query_name, top_k=3, score_threshold=0.7):
    
    try:
        query_vector = get_embedding(query_name)
    except Exception as e:
        logger.error(f"OpenAI API 텍스트 임베딩 실패: {e}")
        raise ExternalAPIError()

    # Pinecone에서 유사도 검색
    results = index.query(
        vector=query_vector,
        # 결과값 갯수 설정
        top_k=top_k,
        # 메타데이터 포함 유무
        include_metadata=True
    )

    # 결과 처리 (점수 필터링 적용)
    similar_foods = [
        {
            'food_pk': match['id'],
            'food_name': match['metadata']['food_name'],
            'score': match['score']
        }
        for match in results['matches'] if match['score'] >= score_threshold
    ]

    # null로 채워서 항상 top_k 크기로 반환
    while len(similar_foods) < top_k:
        similar_foods.append({'food_name': None, 'food_pk': None})

    return similar_foods[:top_k]


# Redis의 정의된 잔여 기능 횟수 확인
def get_remaining_requests(member_id: int):

    try:
        # Redis 키 생성
        redis_key = f"rate_limit:{member_id}"

        # Redis에서 사용자의 요청 횟수 조회
        current_count = redis_client.get(redis_key)

        # 요청 횟수가 없다면 기본값 반환(RATE_LIMIT)
        if current_count is None:
            return RATE_LIMIT

        # 남은 요청 횟수
        remaining_requests = max(RATE_LIMIT - int(current_count), 0)
        return remaining_requests

    except Exception as e:
        logger.error(f"잔여 기능 횟수 확인 중 에러가 발생했습니다: {e}")
        raise ServiceConnectionError()