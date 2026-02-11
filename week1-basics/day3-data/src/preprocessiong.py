import os 
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, 'titanic', 'train.csv')



df = pd.read_csv(file_path)
print(df.info())
df["Age"]= df["Age"].fillna(df["Age"].mean())
#나이 결측치 평균값으로 채우기
df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0])
# Embarked값 최빈값으로 채우기 [0] 하는 이유 시리즈를 배출하는걸 확인 해봄 
# 그리고 pandas3.0 에서 claude가 제공해준 코드 작동을 안할수도 있다고 경고 문구를 띄움
# chained assignment df["Age"].fillna(..., inplace=True)
# 원본이 아니라 복사본에 적용할수도 있다라는 경고를 띄워 위와같이 적용함
# 통계값으로 할떄는 그냥 위와 같은 방식도 괜찮아보이는데 이것도 chained assignment이슈가 터지려나
# df.fillna({
#     "Age": df["Age"].mean(),
#     "Embarked": df["Embarked"].mode()[0]
# }, inplace=True)



df = df.drop(['Cabin', 'Ticket', 'Name'], axis = 1)
# 불필요한 컬럼 3개 삭제 열 방향으로 삭제

print(df['Embarked'].mode())
print(type(df['Embarked'].mode()))

print(df.info())

print("✅ 결측치 처리 완료")
print(df.isnull().sum())


df = pd.get_dummies(df, columns=["Sex", "Embarked"], drop_first=True)
# get_dummies로 카테고리컬한걸 수치형으로 변환하는데 drop_first는 첫번째거를 기준점으로 삼기위해 삭제한다는 의미라고함
# 여기서 궁금했던점 sklearn OneHotEncoder 과의 차이점 물론 fit/trainsform 유무도 있겠지만
# 만약 학습 데이터가 아닌 테스트데이터에서 새로운 컬럼이 생긴다면 get_dummies는 새로운 컬럼 생성
# 모델 입력 차원이 달라져 에러발생하지만 OneHotEncoder는 즉시 에러 발생하니 실무에서는 이거를 쓸듯 

print("\n✅ 범주형 변환 완료")
print(df.head())


# ✅ 범주형 변환 완료
#    PassengerId  Survived  Pclass   Age  SibSp  Parch     Fare  Sex_male  Embarked_Q  Embarked_S
# 0            1         0       3  22.0      1      0   7.2500      True       False        True
# 1            2         1       1  38.0      1      0  71.2833     False       False       False
# 2            3         1       3  26.0      0      0   7.9250     False       False        True
# 3            4         1       1  35.0      1      0  53.1000     False       False        True
# 4            5         0       3  35.0      0      0   8.0500      True       False        True
# 예상과 달리 boolean 타입이 되어버림 뭐 결론적으로 0도 bool으로 되긴하지만 이게 문제가 되진않을까 라고해서 찾아봄
# 보통은 모델 입력은 numeric 타입으로 통일 한다고 함 

df[['Sex_male', 'Embarked_Q', 'Embarked_S']] =   df[['Sex_male', 'Embarked_Q', 'Embarked_S']].astype(int)
# 해당 처리를 하는게 좋아보임 

# 왜 타입을 통일해야하는가?? 파이프라인의 안정성때문이라고함 
#  전처리 → 학습 → 서빙 → 재학습 동일 구조
#  디버깅 쉬움
#  모델 입력 스펙 명확
#  CI/CD 자동화 안정성
# 근데  bool은 1byte라서 EDA단계에서는 충분히 ok 라고도함 결론: 알아서 잘써라;; 


scaler = StandardScaler()
numeric_cols = ["Age", "Fare"]
df[numeric_cols]= scaler.fit_transform(df[numeric_cols])

# 값의 범위가 일정치 않으면 중요도가 달라보일수도 있음 그래서 평균 0 표준편차 1로 맞춘다 

print("\n✅ 정규화 완료")
print(df[numeric_cols].describe())


df.to_csv('train_preprocessed.csv', index=False)
print("\n💾 전처리된 데이터 저장 완료!")