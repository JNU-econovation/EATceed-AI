import logging
import os
import pytz 
from datetime import datetime 
from core.config import settings

# 로그 디렉토리 설정
os.makedirs(settings.LOG_PATH, exist_ok=True)

# Formatter 클래스
class KSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # 한국 시간대 설정
        kst = pytz.timezone("Asia/Seoul")
        dt = datetime.fromtimestamp(record.created, tz=kst)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()
        
# Uvicorn 및 APScheduler 로거 설정
def configure_uvicorn_logger():
    uvicorn_logger = logging.getLogger("uvicorn")
    access_logger = logging.getLogger("uvicorn.access")
    error_logger = logging.getLogger("uvicorn.error")
    apscheduler_logger = logging.getLogger("apscheduler")  # APScheduler 로거 추가

    # Formatter 설정
    formatter = KSTFormatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    for logger in [uvicorn_logger, access_logger, error_logger, apscheduler_logger]:
        for handler in logger.handlers:
            handler.setFormatter(formatter)


# 공용 로거 생성(INFO, ERROR)
def get_logger():
    logger = logging.getLogger("app_logger")
    # 중복 핸들러 방지
    if not logger.handlers:  
        logger.setLevel(logging.INFO)  

         # 포매터 설정
        formatter = KSTFormatter(
            '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # INFO 로그 핸들러
        info_handler = logging.FileHandler(os.path.join(settings.LOG_PATH, "info.log"))
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        # INFO 필터 추가
        class InfoFilter(logging.Filter):
            def filter(self, record):
                return record.levelno == logging.INFO

        info_handler.addFilter(InfoFilter())
        logger.addHandler(info_handler)

        # ERROR 로그 핸들러
        error_handler = logging.FileHandler(os.path.join(settings.LOG_PATH, "error.log"))
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # ERROR 필터 추가 
        class ErrorFilter(logging.Filter):
            def filter(self, record):
                return record.levelno == logging.ERROR

        error_handler.addFilter(ErrorFilter())
        logger.addHandler(error_handler)

        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)  

    return logger
