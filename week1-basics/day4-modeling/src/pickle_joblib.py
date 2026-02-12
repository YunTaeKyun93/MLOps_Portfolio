import numpy as np
import pickle
import joblib
import time
import os

#pickle vs  joblib
#pickle, joblib의 용도 
# 처음 이런 주제에 앞서 둘다 처음 들어보는 거라 우선 뭐를 비교해야하는지를 찾아봄
# 파이썬 객체를 파일로 저장했다가 나중에 다시 불러오기 위한 도구 
# 우리가 만든 모델은 선언했는데 해당 모델은 RAM안에만 존재하니까 결국 컴퓨터가 
# 껐다 켜지면 사라지니까 메모리에 있는 객체를 파일로 저장 -> 나중에 다시 로드 
# joblib.dump(model, "model.joblib") -> model = joblib.load("model.joblib")

# pickle은 파이썬 기본내장
# 어떤 객체든 대부분 저장가능

# import pickle
# data = {"name": "taegyun", "score": 95}
# with open("data.pkl", "wb") as f:
#     pickle.dump(data, f)

# joblib
# 특히 numpy 배열이 많은 객체 저장에 최적화
# scikit-learn에서 관행적으로 많이 사용

#  둘의 차이를 아주 쉽게
# 항목	pickle	joblib
# 기본 제공:	O	X (설치 필요)
# 범용성:	매우 넓음	ML 중심
# 대용량 numpy: 처리	보통	더 효율적
# ML 관행:	사용 가능	더 많이 사용

# 1) 대용량 데이터(예: 10,000,000 float) 생성
X = np.random.rand(10_000_000).astype(np.float32)  # 약 40MB

# 2) pickle 저장
t0 = time.time()
with open("X.pkl", "wb") as f:
    pickle.dump(X, f, protocol=pickle.HIGHEST_PROTOCOL)
pickle_save = time.time() - t0

# 3) pickle 로드
t0 = time.time()
with open("X.pkl", "rb") as f:
    X1 = pickle.load(f)
pickle_load = time.time() - t0

# joblib.dump(X, "X_c0.joblib", compress=0)  # 압축 없음
# joblib.dump(X, "X_c3.joblib", compress=3)  # 중간 압축
# joblib.dump(X, "X_c9.joblib", compress=9)  # 최대 압축


# 4) joblib 저장 (압축 없음)
t0 = time.time()
joblib.dump(X, "X.joblib", compress=0)
joblib_save = time.time() - t0

# 5) joblib 로드
t0 = time.time()
X2 = joblib.load("X.joblib")
joblib_load = time.time() - t0

# 6) 파일 크기 비교
pkl_size = os.path.getsize("X.pkl") / (1024**2)
job_size = os.path.getsize("X.joblib") / (1024**2)

print(f"[pickle] save: {pickle_save:.3f}s, load: {pickle_load:.3f}s, size: {pkl_size:.1f}MB")
print(f"[joblib] save: {joblib_save:.3f}s, load: {joblib_load:.3f}s, size: {job_size:.1f}MB")

print("same?", np.allclose(X1, X2))


# [pickle] save: 0.009s, load: 0.006s, size: 38.1MB
# [joblib] save: 0.013s, load: 0.011s, size: 38.1MB
# same? True
# 지금 차이가 별로 안나는데 numpy배열 하나짜리라서?? 