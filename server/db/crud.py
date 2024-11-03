# DB CRUD 함수 정의
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from db.models import EatHabits, Member, Food, Meal, MealFood, AnalysisStatus

import logging
from errors.custom_exceptions import InvalidUserId, UserDataError, AnalysisError

# 로그 메시지
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# DB 연결 Test CRUD 
def crud_test(db: Session, member_id: int, flag: bool, weight_prediction: str, advice_carbo: str,
              advice_protein: str, advice_fat: str, synthesis_advice: str):
    try:
        created_date = datetime.now()
        logger.debug(f"Attemping to insert Eathabits record for member_id : {member_id}")
        eat_habits = EatHabits(
            CREATED_DATE=created_date,
            FLAG = flag,
            WEIGHT_PREDICTION = weight_prediction,
            ADVICE_CARBO = advice_carbo,
            ADVICE_PROTEIN = advice_protein,
            ADVICE_FAT = advice_fat,
            SYNTHESIS_ADVICE = synthesis_advice,
            MEMBER_FK = member_id
        )
        db.add(eat_habits)
        db.commit()
        db.refresh(eat_habits)
        logger.info(f"Successfully inserted EatHabits record for member_id: {member_id}")
        return eat_habits
    except Exception as e:
        logger.error(f"Error inserting EatHabits record for member_id: {member_id} - {e}")
        db.rollback()
        

# 식습관 분석 결과값 db에 저장
def create_eat_habits(db: Session, member_id: int, weight_prediction: str, advice_carbo: str,
                             advice_protein: str, advice_fat: str, synthesis_advice: str, avg_calorie: float, flag: bool = True):
    try:
        created_date = datetime.now()
        logger.debug(f"Attempting to insert EatHabits record for member_id: {member_id}")
        
        eat_habits = EatHabits(
            CREATED_DATE=created_date,
            FLAG=flag,
            WEIGHT_PREDICTION=weight_prediction,
            ADVICE_CARBO=advice_carbo,
            ADVICE_PROTEIN=advice_protein,
            ADVICE_FAT=advice_fat,
            SYNTHESIS_ADVICE=synthesis_advice,
            MEMBER_FK=member_id,
            AVG_CALORIE=avg_calorie
        )
        
        db.add(eat_habits)
        db.commit()
        db.refresh(eat_habits)
        
        logger.info(f"Successfully inserted EatHabits record for member_id: {member_id}")
        return eat_habits
    except Exception as e:
        logger.error(f"Error inserting EatHabits record for member_id: {member_id} - {e}")
        db.rollback()
        raise AnalysisError("식습관 분석을 실행할 수 없습니다")

# FLAG 활성/비활성 
def update_flag(db: Session):
    try:
        # FLAG 비활성화 
        db.query(EatHabits).filter(EatHabits.FLAG == True).update({EatHabits.FLAG: False})
        db.commit()
        logger.info("Updated existing flag to False")
    except Exception as e:
        logger.error(f"Error updating flag: {e}")
        db.rollback()
        

# Background에서 실행할 때 모든 사용자의 분석 결과 도출 필요
def get_all_member_id(db: Session):
    try:
        return [member.MEMBER_PK for member in db.query(Member).all()]
    except Exception as e:
        logger.error(f"Error fetching member id: {e}")



# 최신 분석 결과 조회(FLAG == True)
def get_latest_eat_habits(db: Session, member_id: int):
    try:
        result = db.query(EatHabits).filter(EatHabits.MEMBER_FK == member_id, EatHabits.FLAG == True).first()
        if not result:
            raise UserDataError("유저 데이터 에러입니다.")
        return result
    except Exception as e:
        logger.error(f"Error fetching latest eat habits: {e}")


# member_id에 해당하는 사용자 정보 조회
def get_member_info(db: Session, member_id: int):
    logger.debug(f"member info for member_id : {member_id}")
    member = db.query(Member).filter(Member.MEMBER_PK == member_id).first()

    if member:
        logger.debug(f"Member found: {member}")
    else:
        logger.debug(f"Member not found for member_id: {member_id}")
    return member

    
# 일주일간 MEAL_TYPE 조회
def get_last_weekend_meals(db: Session, member_id: int):
    try:
        now = datetime.now()
        # 지난 주 월요일 0시
        start_of_this_week = now - timedelta(days=now.weekday(), weeks=1)  
        # 이번 주 월요일 0시
        start_of_next_week = start_of_this_week + timedelta(weeks=1)  
        meals = db.query(Meal).filter(
            Meal.MEMBER_FK == member_id, 
            Meal.CREATED_DATE >= start_of_this_week,
            Meal.CREATED_DATE < start_of_next_week
            ).all()
        logger.debug(f"Meals found: {meals}")
        return meals
    except Exception as e:
        logger.error(f"Error fetching last weekend meals: {e}")



# MEAL_FK에 해당하는 음식 조회
def get_meal_foods(db: Session, meal_id: int):
    try:
        meal_foods = db.query(MealFood).filter(MealFood.MEAL_FK == meal_id).all()
        logger.debug(f"Meal foods found: {meal_foods}")
        return meal_foods
    except Exception as e:
        logger.error(f"Error fetching meal foods: {e}")
        

# FOOD_FK에 해당하는 음식 정보 조회
def get_food_info(db: Session, food_id: int):
    try:
        food = db.query(Food).filter(Food.FOOD_PK == food_id).first()
        logger.debug(f"Food found: {food}")
        return food
    except Exception as e:
        logger.error(f"Error fetching food info: {e}")
        



# 최종적으로 얻고자하는 사용자에 따른 7일간의 영양성분의 평균값 얻기
def get_member_meals_avg(db: Session, member_id: int):
    try:
        member = get_member_info(db, member_id)
        if not member:
            raise InvalidUserId("멤버가 존재하지 않습니다")

        meals = get_last_weekend_meals(db, member_id)
        total_nutrition = {
            "calorie": 0,
            "carbohydrate": 0,
            "fat": 0,
            "protein": 0,
            "serving_size": 0,
            "sugars": 0,
            "dietary_fiber": 0,
            "sodium": 0,
        }
        total_foods = 0

        for meal in meals:
            meal_foods = get_meal_foods(db, meal.MEAL_PK)
            for meal_food in meal_foods:
                food_info = get_food_info(db, meal_food.FOOD_FK)

                # 사용자가 먹은 양 설정(단위: multiple or g)
                if food_info:
                    multiplier = 1
                    if meal_food.MEAL_FOOD_MULTIPLE is not None:
                        multiplier = meal_food.MEAL_FOOD_MULTIPLE
                    elif meal_food.MEAL_FOOD_G is not None:
                        multiplier = meal_food.MEAL_FOOD_G / food_info.FOOD_SERVING_SIZE

                    # 최종 양 설정
                    total_nutrition["calorie"] += food_info.FOOD_CALORIE * multiplier
                    total_nutrition["carbohydrate"] += food_info.FOOD_CARBOHYDRATE * multiplier
                    total_nutrition["fat"] += food_info.FOOD_FAT * multiplier
                    total_nutrition["protein"] += food_info.FOOD_PROTEIN * multiplier
                    total_nutrition["serving_size"] += food_info.FOOD_SERVING_SIZE * multiplier
                    total_nutrition["sugars"] += food_info.FOOD_SUGARS * multiplier
                    total_nutrition["dietary_fiber"] += food_info.FOOD_DIETARY_FIBER * multiplier
                    total_nutrition["sodium"] += food_info.FOOD_SODIUM * multiplier
                    total_foods += 1

        if total_foods > 0:
            avg_nutrition = {key: value / total_foods for key, value in total_nutrition.items()}
        else:
            avg_nutrition = total_nutrition

        return avg_nutrition
    except Exception as e:
        logger.error(f"Error calculating member meals average: {e}")
        raise UserDataError("유저 데이터 에러입니다")


# activity 값 변환을 위한 딕셔너리
activity_mapping = {
    'NOT_ACTIVE': 1.2,
    'LIGHTLY_ACTIVE': 1.3,
    'NORMAL_ACTIVE': 1.5,
    'VERY_ACTIVE': 1.7,
    'EXTREMELY_ACTIVE': 1.9
}

# TDEE 수식을 구하기 위한 사용자 신체정보 조회
def get_member_body_info(db: Session, member_id: int):
    try:
        member = get_member_info(db, member_id)

        if member:
            activity_value = activity_mapping.get(member.MEMBER_ACTIVITY, 1.2)  # 기본값은 1.2
            body_info = {
                'gender': member.MEMBER_GENDER,
                'age': member.MEMBER_AGE,
                'height': member.MEMBER_HEIGHT,
                'weight': member.MEMBER_WEIGHT,
                'physical_activity_index': activity_value
            }
            return body_info
        else:
            raise InvalidUserId("멤버가 존재하지 않습니다")
    except Exception as e:
        logger.error(f"Error fetching member body info: {e}")
        raise UserDataError("유저 데이터 에러입니다")

# BMR 구하기
def get_bmr(gender: int, weight: float, height: float, age: int) -> float:
   # 남자
    if gender == 0: 
      # 남자일 경우의 bmr 수식
      bmr = 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
    # 여자
    else:
       # 여자일 경우의 bmr 수식
       bmr = 655 + (9.6 * weight) + (1.7 * height) - (4.7 * age)
    return bmr


# TDEE 구하기
def get_tdee(bmr: float, activity: float) -> float:
   # tdee 수식
   tdee = bmr * activity
   return tdee


# prompt에 넣을 사용자 데이터 구성
def get_user_data(db: Session, member_id: int):
    # try:
        member_info = get_member_body_info(db, member_id)
        if not member_info:
            raise Exception("Member not found")
    
        avg_nutrition = get_member_meals_avg(db, member_id)
        bmr = get_bmr(
            gender=member_info['gender'],
            weight=member_info['weight'],
            height=member_info['height'],
            age=member_info['age']
        )
        tdee = get_tdee(bmr, member_info['physical_activity_index'])

        user_data = {
            "user": [
                {"gender": 'Male' if member_info['gender'] == 0 else 'Female'},
                {"age": member_info['age']},
                {"height": member_info['height']},
                {"weight": member_info['weight']},
                {"serving_size": avg_nutrition["serving_size"]},
                {"calorie": avg_nutrition["calorie"]},
                {"protein": avg_nutrition["protein"]},
                {"fat": avg_nutrition["fat"]},
                {"carbohydrate": avg_nutrition["carbohydrate"]},
                {"dietary_fiber": avg_nutrition["dietary_fiber"]},
                {"sugars": avg_nutrition["sugars"]},
                {"sodium": avg_nutrition["sodium"]},
                {"physical_activity_index": member_info['physical_activity_index']},
                {"tdee": tdee}
            ]
        }

        # 영양 성분 값 모두 0인지 확인
        nutrition_values = [
            avg_nutrition["serving_size"],
            avg_nutrition["calorie"],
            avg_nutrition["protein"],
            avg_nutrition["fat"],
            avg_nutrition["carbohydrate"],
            avg_nutrition["dietary_fiber"],
            avg_nutrition["sugars"],
            avg_nutrition["sodium"]
        ]
        if all(value == 0 for value in nutrition_values):
            raise UserDataError("유저 데이터 에러입니다")

        return user_data, avg_nutrition["calorie"]
    # except Exception as e:
    #     logger.error(f"Error fetching user data: {e}")
    #     raise UserDataError("")


# 식습관 분석 알림: 분석 상태 업데이트
def update_analysis_status(db: Session, member_id: int):
    try:
        analysis_status = db.query(AnalysisStatus).filter(
            AnalysisStatus.MEMBER_FK == member_id
        ).first()

        # 기록이 이미 존재
        if analysis_status:
            analysis_status.IS_ANALYZED = True
            analysis_status.ANALYSIS_DATE = datetime.now()
        
        # 기록이 존재하지 않을 경우
        else:
            analysis_status = AnalysisStatus(
                MEMBER_FK=member_id,
                IS_ANALYZED=True,
                ANALYSIS_DATE=datetime.now()
            )
            db.add(analysis_status)
        db.commit()
    except Exception as e:
        raise AnalysisError("식습관 분석 상태 업데이트 중 오류가 발생했습니다.")

# 식습관 분석 알림: 분석 상태 조회
def get_analysis_status(db: Session, member_id: int):
    
    result = db.query(AnalysisStatus).filter(
        AnalysisStatus.MEMBER_FK == member_id
    ).first()

    return result