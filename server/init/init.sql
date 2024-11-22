use gaebaljip;

CREATE TABLE MEMBER_TB
(
    MEMBER_PK       bigint(20)   NOT NULL AUTO_INCREMENT,
    CREATED_DATE    datetime(6)  NOT NULL,
    UPDATED_DATE    datetime(6)  NOT NULL,
    MEMBER_ACTIVITY varchar(255) DEFAULT NULL,
    MEMBER_AGE      int(11)      DEFAULT NULL,
    MEMBER_ETC      varchar(255) DEFAULT NULL,
    MEMBER_GENDER   tinyint      DEFAULT NULL,
    MEMBER_HEIGHT   double       DEFAULT NULL,
    MEMBER_EMAIL    varchar(255) NOT NULL UNIQUE,
    MEMBER_PASSWORD varchar(255) NOT NULL,
    MEMBER_ROLE     varchar(255) NOT NULL DEFAULT 'MEMBER',
    MEMBER_WEIGHT   double       DEFAULT NULL,
    MEMBER_TARGET_WEIGHT   double       DEFAULT NULL,
    MEMBER_CHECKED  bit(1)       NOT NULL DEFAULT 0,
    PRIMARY KEY (MEMBER_PK)
) ENGINE=InnoDB;

CREATE TABLE FOOD_TB 
(
    FOOD_PK            bigint(20)   NOT NULL AUTO_INCREMENT,
    FOOD_CODE          bigint(20)   DEFAULT NULL,
    FOOD_NAME          varchar(255)  NOT NULL,
    FOOD_CATEGORY_CODE  tinyint      DEFAULT NULL,
    FOOD_SERVING_SIZE  double        NOT NULL,
    FOOD_CALORIE       double        NOT NULL,
    FOOD_CARBOHYDRATE  double        NOT NULL,
    FOOD_PROTEIN       double        NOT NULL,
    FOOD_FAT           double        NOT NULL,
    FOOD_SUGARS        double        NOT NULL,
    FOOD_DIETARY_FIBER double        NOT NULL,
    FOOD_SODIUM        double        NOT NULL,
    MEMBER_FK          bigint(20)    DEFAULT NULL,
    PRIMARY KEY (FOOD_PK),
    FOREIGN KEY (MEMBER_FK) REFERENCES MEMBER_TB (MEMBER_PK) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE MEAL_TB
(
    MEAL_PK            bigint(20)   NOT NULL AUTO_INCREMENT,
    CREATED_DATE       datetime(6)  NOT NULL,
    UPDATED_DATE       datetime(6)  NOT NULL,
    MEAL_TYPE          varchar(255) NOT NULL,
    MEMBER_FK          bigint(20) DEFAULT NULL,
    PRIMARY KEY (MEAL_PK),
    FOREIGN KEY (MEMBER_FK) REFERENCES MEMBER_TB (MEMBER_PK) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE MEAL_FOOD_TB
(
    MEAL_FOOD_PK bigint(20)  NOT NULL AUTO_INCREMENT,
    CREATED_DATE datetime(6) NOT NULL,
    UPDATED_DATE datetime(6) NOT NULL,
    FOOD_FK      bigint(20) DEFAULT NULL,
    MEAL_FK      bigint(20) DEFAULT NULL,
    MEAL_FOOD_MULTIPLE double DEFAULT NULL,
    MEAL_FOOD_G int DEFAULT NULL,
    PRIMARY KEY (MEAL_FOOD_PK),
    FOREIGN KEY  (FOOD_FK) REFERENCES FOOD_TB (FOOD_PK) ON DELETE CASCADE,
    FOREIGN KEY  (MEAL_FK) REFERENCES MEAL_TB (MEAL_PK) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE ANALYSIS_STATUS_TB
(
    STATUS_PK bigint(20) NOT NULL AUTO_INCREMENT,
    ANALYSIS_DATE datetime(6) NOT NULL,
    IS_ANALYZED tinyint(1) NOT NULL DEFAULT 0,
    IS_PENDING tinyint(1) NOT NULL DEFAULT 1,
    MEMBER_FK bigint(20) DEFAULT NULL,
    PRIMARY KEY (STATUS_PK),
    FOREIGN KEY (MEMBER_FK) REFERENCES MEMBER_TB (MEMBER_PK) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE EAT_HABITS_TB
(
    EAT_HABITS_PK bigint(20) NOT NULL AUTO_INCREMENT,
    ANALYSIS_STATUS_FK bigint(20) DEFAULT NULL,
    WEIGHT_PREDICTION text NOT NULL,
    ADVICE_CARBO text NOT NULL,
    ADVICE_PROTEIN text NOT NULL,
    ADVICE_FAT text NOT NULL,
    SYNTHESIS_ADVICE text NOT NULL,
    AVG_CALORIE double NOT NULL,
    PRIMARY KEY (EAT_HABITS_PK),
    FOREIGN KEY (ANALYSIS_STATUS_FK) REFERENCES ANALYSIS_STATUS_TB (STATUS_PK) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE HISTORY_TB
(
    HISTORY_PK bigint(20) NOT NULL AUTO_INCREMENT,
    CREATED_DATE      datetime(6)  NOT NULL,
    UPDATED_DATE       datetime(6)  NOT NULL,
    HISTORY_ACTIVITY varchar(255) NOT NULL ,
    HISTORY_AGE      int(11)      NOT NULL,
    HISTORY_GENDER   tinyint      NOT NULL,
    HISTORY_HEIGHT   double       NOT NULL,
    HISTORY_WEIGHT   double       NOT NULL,
    HISTORY_TARGET_WEIGHT   double       NOT NULL,
    MEMBER_FK bigint(20) DEFAULT NULL,
    PRIMARY KEY (HISTORY_PK),
    FOREIGN KEY (MEMBER_FK) REFERENCES MEMBER_TB (MEMBER_PK) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE NOTIFY_TB
(
    NOTIFY_PK bigint(20) NOT NULL AUTO_INCREMENT,
    CREATED_DATE datetime(6) NOT NULL,
    UPDATED_DATE datetime(6) NOT NULL,
    NOTIFY_URL varchar(255) NOT NULL,
    NOTIFY_IS_READ bit(1) NOT NULL,
    NOTIFY_CONTENT varchar(255) NOT NULL,
    NOTIFY_TYPE varchar(255) NOT NULL,
    MEMBER_FK bigint(20) DEFAULT NULL,
    PRIMARY KEY (NOTIFY_PK),
    FOREIGN KEY (MEMBER_FK) REFERENCES MEMBER_TB (MEMBER_PK) ON DELETE CASCADE
) ENGINE=InnoDB;


-- FOOD_TB는 이미 적재되어있는 상태
-- MEMBER_TB 데이터 적재
INSERT INTO MEMBER_TB (MEMBER_PK, CREATED_DATE, UPDATED_DATE, MEMBER_ACTIVITY, MEMBER_AGE, MEMBER_ETC, MEMBER_GENDER,
                       MEMBER_HEIGHT, MEMBER_WEIGHT, MEMBER_TARGET_WEIGHT, MEMBER_EMAIL, MEMBER_PASSWORD, MEMBER_ROLE, MEMBER_CHECKED)
VALUES
(2, '2023-12-01 08:00:00', '2023-12-01 08:00:00', 'NOT_ACTIVE', 30, '비고 없음', 1, 175.0, 61.0, 66.0, 'abcd234@@gmail.com',
        '$2a$10$pljAKl0Ad3LnjQyQei.Yz.0Cfcn3Zv/xeBMDwUHDaUrfG8Wm57c56', 'MEMBER', true),
(3, '2024-05-14 08:00:00', '2024-05-14 08:00:00', 'NOT_ACTIVE', 24, '비고 없음', 1, 175.0, 67.0, 70.0, 'wwns1411@naver.com',
        '$2a$10$yCTgvLMTXsLepju7jXYKu.O9bYEe.7G5FJNfNkdin8HiYYvCq82.6', 'MEMBER', true),
(4, '2023-12-01 08:00:00', '2023-12-01 08:00:00', 'NOT_ACTIVE', 30, '비고 없음', 1, 175.0, 61.0, 66.0, 'abcd123!@gmail.com',
        '$2a$10$pljAKl0Ad3LnjQyQei.Yz.0Cfcn3Zv/xeBMDwUHDaUrfG8Wm57c56', 'MEMBER', true),
(5, '2023-12-01 08:00:00', '2023-12-01 08:00:00', 'NOT_ACTIVE', 30, '비고 없음', 1, 175.0, 61.0, 66.0, 'abc13!@gmail.com',
        '$2a$10$pljAKl0Ad3LnjQyQei.Yz.0Cfcn3Zv/xeBMDwUHDaUrfG8Wm57c56', 'MEMBER', true);
        
-- MEAL_TB 데이터 적재
INSERT INTO MEAL_TB (MEAL_PK, CREATED_DATE, UPDATED_DATE, MEAL_TYPE, MEMBER_FK)
VALUES 
(1, '2024-11-03 08:00:00', '2024-11-03 08:00:00', 'BREAKFAST', 4),
(2, '2024-11-03 08:30:00', '2024-11-03 08:30:00', 'BREAKFAST', 3),
(3, '2024-11-03 09:00:00', '2024-11-03 09:00:00', 'BREAKFAST', 2),
(4, '2024-11-03 12:00:00', '2024-11-03 12:00:00', 'LUNCH', 4),
(5, '2024-11-03 12:30:00', '2024-11-03 12:30:00', 'LUNCH', 3),
(6, '2024-11-03 13:00:00', '2024-11-03 13:00:00', 'LUNCH', 2),
(7, '2024-11-03 18:00:00', '2024-11-03 18:00:00', 'DINNER', 4),
(8, '2024-11-03 18:30:00', '2024-11-03 18:30:00', 'DINNER', 3),
(9, '2024-11-03 19:00:00', '2024-11-03 19:00:00', 'DINNER', 2),
(10, '2024-11-03 20:00:00', '2024-11-03 20:00:00', 'SNACK', 4),
(11, '2024-11-03 20:30:00', '2024-11-03 20:30:00', 'SNACK', 3);

-- FOOD_TB 데이터 적재
INSERT INTO FOOD_TB (FOOD_PK, FOOD_CODE, FOOD_NAME, FOOD_CATEGORY_CODE, FOOD_SERVING_SIZE, FOOD_CALORIE, FOOD_CARBOHYDRATE, FOOD_PROTEIN, FOOD_FAT, FOOD_SUGARS, FOOD_DIETARY_FIBER, FOOD_SODIUM)
VALUES 
(1, 1001, 'Food 1', 1, 100, 200, 50, 30, 20, 10, 5, 2),
(2, 1002, 'Food 2', 2, 150, 300, 70, 40, 30, 15, 8, 3),
(3, 1003, 'Food 3', 3, 200, 250, 60, 35, 25, 12, 6, 4);


-- MEAL_FOOD_TB 데이터 적재
INSERT INTO MEAL_FOOD_TB (MEAL_FOOD_PK, CREATED_DATE, UPDATED_DATE, FOOD_FK, MEAL_FK, MEAL_FOOD_MULTIPLE, MEAL_FOOD_G)
VALUES 
(1, '2024-11-03 08:00:00', '2024-11-03 08:00:00', 1, 1, 1.0, 200),  
(2, '2024-11-03 08:30:00', '2024-11-03 08:30:00', 2, 2, 1.5, 150),  
(3, '2024-11-03 09:00:00', '2024-11-03 09:00:00', 3, 3, 1.0, 100),  
(4, '2024-11-03 12:00:00', '2024-11-03 12:00:00', 1, 4, 2.0, 250),  
(5, '2024-11-03 12:30:00', '2024-11-03 12:30:00', 2, 5, 1.0, 200),  
(6, '2024-11-03 13:00:00', '2024-11-03 13:00:00', 3, 6, 1.2, 220),  
(7, '2024-11-03 18:00:00', '2024-11-03 18:00:00', 1, 7, 1.3, 180),  
(8, '2024-11-03 18:30:00', '2024-11-03 18:30:00', 2, 8, 1.1, 130),  
(9, '2024-11-03 19:00:00', '2024-11-03 19:00:00', 3, 9, 0.8, 100), 
(10, '2024-11-03 20:00:00', '2024-11-03 20:00:00', 1, 10, 1.0, 50),  
(11, '2024-11-03 20:30:00', '2024-11-03 20:30:00', 2, 11, 0.5, 75); 

-- ANALYSIS_STATUS_TB 데이터 적재
INSERT INTO ANALYSIS_STATUS_TB (STATUS_PK, ANALYSIS_DATE, IS_ANALYZED, IS_PENDING, MEMBER_FK)
VALUES 
(1, '2024-11-04 00:00:30', 1, 0, 4),  
(2, '2024-11-04 00:00:30', 1, 0, 2),  
(3, '2024-11-04 00:00:30', 1, 0, 3);  

-- EAT_HABITS_TB 데이터 적재
INSERT INTO EAT_HABITS_TB (EAT_HABITS_PK, ANALYSIS_STATUS_FK, WEIGHT_PREDICTION, ADVICE_CARBO, ADVICE_PROTEIN, ADVICE_FAT, SYNTHESIS_ADVICE)
VALUES 
(1, 1, '유지', '탄수화물 섭취 증가 권장', '단백질 섭취 증가 권장', '지방 섭취 줄이기 권장', '균형 잡힌 식단 유지 권장'),
(2, 2, '감량', '탄수화물 섭취 줄이기 권장', '단백질 유지', '지방 섭취 증가 권장', '체중 감량을 위한 식단 조정 필요'),
(3, 3, '증가', '탄수화물 섭취 증가 권장', '단백질 섭취 증가 권장', '지방 섭취 증가 권장', '칼로리 흡수 증대를 권장');
