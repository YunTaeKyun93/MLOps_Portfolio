Day 7 - Collaborative Filtering Recommender

목표: MovieLens 1M 데이터로 CF 추천 시스템 구현 + BentoML API 서빙
핵심: ML 알고리즘 이해 → 함수형 리팩토링 → API 서빙 파이프라인


학습 목표

 Collaborative Filtering 개념 이해
 User-Item Matrix 생성 및 코사인 유사도 계산
 train/test split + 정확도 평가
 pickle로 모델 저장
 BentoML 2.0으로 API 서빙
 Matrix Factorization 개념 이해 (Ch2)


왜 이렇게 설계했는가
1. pickle을 쓴 이유 (joblib 아님)
picklejoblib용도일반 Python 객체 (DataFrame, dict)numpy 배열, sklearn 모델우리 데이터pandas DataFrame 2개해당 없음결론✅ 적합오버스펙
joblib이 빠른 이유는 numpy 배열을 메모리 매핑으로 처리해서인데, pandas DataFrame은 그 이점이 크지 않음.
2. BentoML Runner를 안 쓴 이유
Runner 필요   → BentoML Model Store에 등록된 모델 (Day 6 Titanic)
Runner 불필요 → pickle, 직접 만든 함수 등 BentoML 밖에서 관리하는 것 (Day 7)
Day 7의 핵심 데이터는 직접 저장한 pickle 파일이기 때문에 Runner 없이 직접 로드해서 사용.
3. train_easy.py → train.py 순서로 짠 이유
train_easy.py (절차형) → 데이터 흐름 눈으로 확인, 이해 완료
train.py (함수형)      → 이해한 로직을 함수로 묶기, service.py에서 재사용
처음부터 함수형으로 짜면 "왜 이렇게 동작하는지" 모르고 넘어가기 쉬움.
4. csr_matrix를 쓴 이유
User-Item Matrix: 6040 × 3706 = 22,376,240개 칸 중 95.5%가 비어있음
csr_matrix → 0이 아닌 값만 저장 → 메모리 대폭 절약 + 속도 향상
cosine_similarity는 NaN 지원 안 함 → fillna(0) 후 압축
5. train_df로만 matrix를 만든 이유 (Data Leakage 방지)
test 데이터가 matrix에 포함되면 "답지 미리 보고 시험 치는 것" = 정확도 뻥튀기.
실제로 train_df로만 만들면 영화가 3706 → 3705개로 줄어듦 (test에만 있는 영화 1개 = Cold Start 축소판).

BentoML 1.x vs 2.0 문법 변화
python# 1.x 방식
svc = bentoml.Service("cf_recommender")
@svc.api(input=JSON(), output=JSON())
def predict(request: dict) -> dict: ...

# 2.0 방식
@bentoml.service
class CFRecommender:
    @bentoml.api
    def predict(self, request: dict) -> dict: ...
2.0에서 from bentoml.io import JSON import 불필요.
Request body는 {"request": {...}} 형태로 감싸야 함.

실행 방법
bash# 1. 패키지 설치
pip install bentoml scikit-learn pandas numpy matplotlib tqdm

# 2. 모델 학습 (최초 1회, 수분 소요)
python src/train.py

# 3. API 서버 시작
bentoml serve src.service:CFRecommender --reload
API 테스트 (Windows)
bashcurl -X POST http://localhost:3000/predict \
     -H "Content-Type: application/json" \
     -d "{\"request\": {\"user_id\": 1, \"movie_id\": 1193}}"

# 응답
# {"user_id": 1, "movie_id": 1193, "predicted_rating": 4.41, "rounded_rating": 4}

성능 결과
방법Accuracy랜덤 예측~20%전체 평균~28%CF (구현)38.2%MF / SVD5565%NCF~70%+

파일 구조
day7-cf-recommender/
├── notes/
│   ├── lecture_notes.md    # Ch1 CF 강의 정리
│   ├── lecture_notes2.md   # Ch2 MF/KNN 강의 정리
│   └── practice_notes.md   # 실습 기록
├── src/
│   ├── train_easy.py       # 절차형 탐색 코드 (이해용)
│   ├── train.py            # 함수형 학습 코드
│   └── service.py          # BentoML API 서버
├── data/
│   └── ml-1m/
│       └── ratings.dat     # MovieLens 1M (git 제외)
└── outputs/
    ├── user_item_matrix.pkl # 학습된 평점 행렬 (git 제외)
    └── user_similarity.pkl  # 유사도 캐시 (git 제외)

참고

Day 6: BentoML 기초 (Titanic 모델 서빙)
Day 8: Docker 컨테이너화 + 클라우드 배포 예정
데이터셋: MovieLens 1M