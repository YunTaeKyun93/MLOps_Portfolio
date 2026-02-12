import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'titanic', 'train.csv')
MODEL_DIR = os.path.join(BASE_DIR, '..', 'outputs')

df= pd.read_csv(DATA_PATH)


df["Age"] = df["Age"].fillna(df["Age"].mean())
df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

df = df.drop(['Cabin', 'Ticket', 'Name', 'PassengerId'], axis=1)

print(df.info())
df = pd.get_dummies(df, columns=['Sex', 'Embarked'], dtype=int)

print(df.head())

X = df.drop('Survived', axis=1)
y = df["Survived"]
print(df.info())

print("✅ 데이터 준비 완료")
print(f"   X shape: {X.shape}")
print(f"   y shape: {y.shape}")


X_train, X_test , y_train, y_test = train_test_split(
  X,y,
  random_state=42,
  test_size=0.2,
  stratify=y
)

print(f"\n✅ Train/Test 분리 완료")
print(f"   Train: {X_train.shape[0]}개")
print(f"   Test:  {X_test.shape[0]}개")


model  = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"   Accuracy: {accuracy:.4f}")
print(classification_report(y_test, y_pred,
                             target_names=['Not Survived', 'Survived']))


# os.makedirs(MODEL_DIR, exist_ok= True)
# model_path = os.path.join(MODEL_DIR, 'titanic_model.pkl')
# joblib.dump(model, model_path)

# print(f"\n💾 모델 저장 완료: {model_path}")


# 다른 코드는 다 이해가 가고 하는데 target_names=['Not Survived', 'Survived'])) 해당 부분 잘못햇다가는 진짜 반대의 결과가 나올거같아서 찾아보니 
#   labels=[0, 1],   target_names=['Not Survived', 'Survived'] 요런식으로 하는게 안전할듯 


#    Train: 712개
#    Test:  179개
#    Accuracy: 0.8268
#               precision    recall  f1-score   support

# Not Survived       0.83      0.90      0.86       110
#     Survived       0.82      0.71      0.76        69

#     accuracy                           0.83       179
#    macro avg       0.82      0.81      0.81       179
# weighted avg       0.83      0.83      0.82       179

# 결과인데 타이타닉처럼 이미 사고가 난뒤 의 결과보고 면 뭘 중요하게 봐야할까?
# 사망처리가 되었는데 살아있는 사람?
# 살아있는데 죽었다고 판정된사람? 

# 이건 잘모르겟네 