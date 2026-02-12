import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import joblib


BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'titanic', 'train.csv')
MODEL_DIR = os.path.join(BASE_DIR, '..', 'outputs')


df = pd.read_csv(DATA_PATH)
df['Age'] = df['Age'].fillna(df['Age'].mean())
df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0])
df = df.drop(['Cabin', 'Ticket', 'Name', 'PassengerId'], axis=1)
df = pd.get_dummies(df, columns=['Sex', 'Embarked'], dtype=int)

X = df.drop('Survived', axis=1)
y = df['Survived']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

models = {
    'Logistic Regression': LogisticRegression(random_state=42),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42),
}



print("모델 성능 비교")
print("-" * 45)
print(f"{'모델':<25} {'Accuracy':>8} {'F1-Score':>8}")
print("-" * 45)

best_model = None
best_score = 0

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1  = f1_score(y_test, y_pred)

    print(f"{name:<25} {acc:>8.4f} {f1:>8.4f}")

    if f1 > best_score:
        best_score = f1
        best_model = (name, model)
  
if best_model is not None:
  print("-" * 45)
  print(f"\n🏆 최고 성능 모델: {best_model[0]} (F1: {best_score:.4f})")


  os.makedirs(MODEL_DIR, exist_ok=True)
  best_path = os.path.join(MODEL_DIR, 'best_model.pkl')
  joblib.dump(best_model[1], best_path)
  print(f" 최고 모델 저장: {best_path}")
else :
   print('모델이 없음')

# Logistic Regression         0.7933   0.7132
# Decision Tree               0.8045   0.7407
# Random Forest               0.8268   0.7597
# ---------------------------------------------

# 🏆 최고 성능 모델: Random Forest (F1: 0.7597)


# Logistic Regression 은 선형이라 연속된 수치가 아니라 약하게 나온건가??
# 그렇다면 이제 여러트리로 판단해서 하는게 잘 나오는데 Decision 도 잘나오지만, Random Forest가  여러명이서 투표하는거라 더 잘나온느낌??

