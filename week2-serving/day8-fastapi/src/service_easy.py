import pickle
import os
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "day7-cf-recommender", "outputs")
print("-" * 60)
print(OUTPUT_DIR)
print("-" * 60)
model_store = {}


@asynccontextmanager
# 서버 시작전 / 서버 종류 후 실행되는 코드를 정의하는 도구
async def lifespan(app: FastAPI):
    print("모델 로딩중!!")

    with open(os.path.join(OUTPUT_DIR, "user_item_matrix.pkl"), "rb") as f:
        model_store["matrix"] = pickle.load(f)

    with open(os.path.join(OUTPUT_DIR, "user_similarity.pkl"), "rb") as f:
        model_store["sim_df"] = pickle.load(f)

    print("✅ 모델 로딩 완료!")
    print(model_store["matrix"].shape)
    print(model_store["sim_df"].shape)

    yield
    # 서버 구조를 나누는 시점
    model_store.clear()
    print("모델 언로드 완료!")


app = FastAPI(title="CF Recommender API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


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
    valid_ratings = movie_ratings[valid_mask]
    valid_sims = user_sim[valid_mask]

    if valid_sims.sum() > 0:
        return float((valid_ratings * valid_sims).sum() / valid_sims.sum())

    return float(movie_ratings.mean())


# 유사 사용찾기 및 해당 영화만 평가한 사용자만 필터링 similarity 가중평균

# DTO생성 나중에 분리 필요해 보이고


class PredictRequest(BaseModel):
    user_id: int
    movie_id: int


class PredictResponse(BaseModel):
    user_id: int
    movie_id: int
    predicted_rating: float
    rounded_rating: int


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    pred = predict_rating(request.user_id, request.movie_id)

    return PredictResponse(
        user_id=request.user_id,
        movie_id=request.movie_id,
        predicted_rating=round(pred, 2),
        rounded_rating=round(pred),
    )
