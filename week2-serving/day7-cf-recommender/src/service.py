import pickle
import os
import numpy as np
import bentoml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


with open(os.path.join(OUTPUT_DIR, "user_item_matrix.pkl"), "rb") as f:
    matrix = pickle.load(f)

with open(os.path.join(OUTPUT_DIR, "user_similarity.pkl"), "rb") as f:
    sim_df = pickle.load(f)


print("✅ 모델 로딩 완료!")
print(f"  Matrix: {matrix.shape}")
print(f"  Similarity: {sim_df.shape}")


def predict_rating(user_id, movie_id):
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
        return (valid_sims * valid_ratings).sum() / valid_sims.sum()

    return movie_ratings.mean()


svc = bentoml.Service("cf_recommender")


@bentoml.service
class CFRecommender:

    @bentoml.api
    def predict(self, request: dict) -> dict:
        user_id = request["user_id"]
        movie_id = request["movie_id"]

        pred = predict_rating(user_id, movie_id)

        return {
            "user_id": user_id,
            "movie_id": movie_id,
            "predicted_rating": round(pred, 2),
            "rounded_rating": round(pred),
        }
