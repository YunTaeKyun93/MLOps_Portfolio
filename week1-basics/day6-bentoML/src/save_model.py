import bentoml
import joblib

# best_model.pkl 로드
model  = joblib.load('outputs/best_model.pkl')

# BentoML에 등록
saved_model = bentoml.sklearn.save_model('titanic_model', model)
print(f"모델 저장 완료: {saved_model}")

