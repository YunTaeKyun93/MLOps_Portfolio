import bentoml
import pandas as pd
from bentoml.io import JSON


# Runner  = 모델 실행 엔진
#           (NestJS의 Service 클래스)

# Service = API 서버
#           (NestJS의 Controller)

# Bento   = 모델 + 코드 + 환경 묶음
#           (Docker 이미지라고 생각하면 됨)


runner = bentoml.sklearn.get('titanic_model:latest').to_runner()
# ModelStore에서 모델 로드 → Runner 생성
# bentoml.sklearn.get('titanic_model:latest') ModelStore에서 최시버전을 가져오고
#.to_runner 해당 모델을 Runner로 감싼다 (추론을 수행하는 실행단위)

EXPECTED_COLUMNS = [
    'Pclass',
    'Age',
    'SibSp',
    'Parch',
    'Fare',
    'Sex_female',
    'Sex_male',
    'Embarked_C',
    'Embarked_Q',
    'Embarked_S'
]

# Service 정의
svc = bentoml.Service('titanic_service', runners=[runner])
# titanic_service라는 서비스를 만든다 이 서비스가 사용할 runner들을 등록한다
@svc.api(input=JSON(), output=JSON())
# API로 외부에 공개하는데 입출력 형태는 Json형식
async def predict(input_data)-> dict:
  # 입력 데이터 → DataFrame 변환
  features = pd.DataFrame([input_data])
  # 모델은 보통 DataFrame 입력을 기대하거나 최소한 2차원 형태를 기대해서  
  # [input_data] 감싸서 DataFrame으로 하면 최소 행1개짜리 테이블 이됨
  features = features[EXPECTED_COLUMNS] #강제정렬
  result = await runner.predict.async_run(features)
  #여기서 비동기가 가능하구나 
  return {
    "survived" : int(result[0]),
    "message" :" 1= 생존,  0 = 사망"
  }
# sklearn predict 결과는 보통 배열/리스트 형태로 나온다.
# 예: array([1])
# 그래서 첫 번째 값 result[0]을 꺼내고 JSON에 담기게 int()로 캐스팅 



# ['Pclass',
#  'Age',
#  'SibSp',
#  'Parch',
#  'Fare',
#  'Sex_female',
#  'Sex_male',
#  'Embarked_C',
#  'Embarked_Q',
#  'Embarked_S']


# curl -X POST http://localhost:3000/predict \
#   -H "Content-Type: application/json" \
#   -d '{
#     "Pclass": 1,
#     "Sex_female": 1,
#     "Sex_male": 0,
#     "Age": 30,
#     "SibSp": 0,
#     "Parch": 0,
#     "Fare": 100,
#     "Embarked_C": 1,
#     "Embarked_Q": 0,
#     "Embarked_S": 0
#   }'