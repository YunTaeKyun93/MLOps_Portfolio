import os
import pandas as pd
import joblib

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, '..', 'outputs', 'titanic_model.pkl')


model = joblib.load(MODEL_PATH)
print(" 모델 로드 완료")


expected_cols = model.feature_names_in_
print("모델이 기대하는 컬럼:", expected_cols)

new_passenger = pd.DataFrame([{
 'Pclass': 1,
'Sex_female': 1,
'Sex_male': 0,
'Fare': 100.0,
'Embarked_C': 1,
'Embarked_Q': 0,
'Embarked_S': 0
}])

for col in expected_cols:
    if col not in new_passenger.columns:
        new_passenger[col] = 0

new_passenger = new_passenger[expected_cols]
print("처리 후 컬럼:", new_passenger.columns.tolist())


prediction = model.predict(new_passenger)
probability = model.predict_proba(new_passenger)


print(f"\n🎯 예측 결과:")
print(f"   생존 여부: {'생존 ✅' if prediction[0] == 1 else '사망 ❌'}")
print(f"   생존 확률: {probability[0][1]:.2%}")
print(f"   사망 확률: {probability[0][0]:.2%}")

#  #   Column    Non-Null Count  Dtype  
# ---  ------    --------------  -----  
#  0   Survived  891 non-null    int64  
#  1   Pclass    891 non-null    int64  
#  2   Sex       891 non-null    object 
#  3   Age       891 non-null    float64
#  4   SibSp     891 non-null    int64  
#  5   Parch     891 non-null    int64  
#  6   Fare      891 non-null    float64
#  7   Embarked  891 non-null    object 



#  #   Column      Non-Null Count  Dtype  
# ---  ------      --------------  -----  
#  0   Survived    891 non-null    int64  
#  1   Pclass      891 non-null    int64  
#  2   Age         891 non-null    float64
#  3   SibSp       891 non-null    int64  
#  4   Parch       891 non-null    int64  
#  5   Fare        891 non-null    float64
#  6   Sex_female  891 non-null    int64  
#  7   Sex_male    891 non-null    int64  
#  8   Embarked_C  891 non-null    int64  
#  9   Embarked_Q  891 non-null    int64  
#  10  Embarked_S  891 non-null    int64  