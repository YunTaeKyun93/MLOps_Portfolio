"""
service.py - FastAPI 기반 추천 API 서버

[BentoML vs FastAPI]
BentoML  → ML 모델 패키징/배포 특화, 자동 문서화
FastAPI  → 범용 API 서버, 더 유연한 라우팅, 실무에서 많이 씀

[백엔드 관점]
NestJS랑 거의 동일한 구조야:
- @app.get()    = @Get()
- @app.post()   = @Post()
- BaseModel     = DTO (class CreateUserDto)
- Depends()     = @Injectable() 의존성 주입
"""

import pickle
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


model_store = {}


# ─────────────────────────────────────────────
# lifespan - 서버 시작/종료 시 실행
#
# [백엔드 관점]
# NestJS의 onModuleInit() 과 동일!
# 서버 시작할 때 pkl 로드해두고
# 이후 요청들은 메모리에서 바로 참조
# ─────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("모델 로딩중,,,")
    with open(os.path.join(OUTPUT_DIR, "user_item_matrix.pkl"), "rb") as f:
        model_store["matrix"] = pickle.load(f)

    with open(os.path.join(OUTPUT_DIR, "user_similarity.pkl"), "rb") as f:
        model_store["sim_df"] = pickle.load(f)

    print("모델 로딩 완료!")
    print(f"  Matrix: {model_store['matrix'].shape}")
    print(f"  Similarity: {model_store['sim_df'].shape}")

    yield  # 여기서 서버가 실행됨

    model_store.clear()
    print("모델 언로드 완료~~")


# ─────────────────────────────────────────────
# FastAPI 앱 생성
# ─────────────────────────────────────────────


app = FastAPI(
    title="CF Recommendar API",
    description="Collaborative Filtering 기반 영화 추천 API",
    version="1.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────
# DTO 정의 (Pydantic BaseModel)
#
# [백엔드 관점]
# NestJS의 DTO와 완전히 동일한 개념
# class PredictDto { user_id: number; movie_id: number }
# ───


class PredictRequest(BaseModel):
    user_id: int
    movie_id: int


class PredictResponse(BaseModel):
    user_id: int
    movie_id: int
    predicted_rating: float
    rounded_rating: int


class RecommendResponse(BaseModel):
    user_id: int
    recommendations: list[dict]


# ─────────────────────────────────────────────
# 핵심 로직
# ─────────────────────────────────────────────


def predict_rating(user_id: int, movie_id: int) -> float:
    matrix = model_store["matrix"]
    sim_df = model_store["sim_df"]

    if user_id not in sim_df.index:
        return 3.0
    if movie_id not in matrix.columns:
        return 3.0

    movie_ratings = matrix[movie_id]
    user_sim = sim_df.loc[user_id]
    valid_mask = movie_ratings.notna()
    valid_sims = user_sim[valid_mask]
    valid_ratings = movie_ratings[valid_mask]

    if valid_sims.sum() > 0:
        return float((valid_sims * valid_ratings).sum() / valid_sims.sum())

    return float(movie_ratings.mean())


# ─────────────────────────────────────────────
# API 엔드포인트
# ─────────────────────────────────────────────


@app.get("/health")
def health():
    return {
        "status": "OK",
        "model_loaded": len(model_store) > 0,
    }


"""
    POST /predict
    특정 사용자가 특정 영화에 줄 평점 예측

    Request: { "user_id": 1, "movie_id": 1193 }
    """


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    pred = predict_rating(request.user_id, request.movie_id)

    return PredictResponse(
        user_id=request.user_id,
        movie_id=request.movie_id,
        predicted_rating=round(pred, 2),
        rounded_rating=round(pred),
    )


"""
GET /recommend/{user_id}?top_k=5
사용자에게 영화 top_k개 추천

[백엔드 관점]
Path Parameter  = /recommend/1
Query Parameter = ?top_k=10
NestJS의 @Param() / @Query() 와 동일!
"""


@app.get("/recommend/{user_id}", response_model=RecommendResponse)
def recommend(user_id: int, top_k: int = 5):
    matrix = model_store["matrix"]
    sim_df = model_store["sim_df"]

    if user_id not in sim_df.index:
        raise HTTPException(
            status_code=404, detail=f"user_id {user_id}를 찾을 수 없습니다."
        )
    watched = set(matrix.loc[user_id].dropna().index.tolist())
    # 특정 유저 한 행 가져오고, 비어있는거 없앰(안본거) 해당 아이디만 가져오는데 해당 형태는 현재 pandas index형태라 python list 로 변환(당연히 리스트인줄;;) set으로 중복제거 및 체크가 빠름
    candidates = [mid for mid in matrix.columns if mid not in watched]

    # 영화에서 이미 유저가 본 영화는 제외

    # 예측 평점 계산
    scored = []
    for movie_id in candidates:
        pred = predict_rating(user_id, movie_id)
        scored.append({"movie_id": int(movie_id), "predicted_rating": round(pred, 2)})

    scored.sort(key=lambda x: x["predicted_rating"], reverse=True)
    return RecommendResponse(
        user_id=user_id,
        recommendations=scored[:top_k],
    )
