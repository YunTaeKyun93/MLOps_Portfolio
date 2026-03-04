import pickle
import os
from fastapi import HTTPException

model_store ={}


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

def load_models():
  with open(os.path.join(OUTPUT_DIR, "user_item_matrix.pkl"), "rb") as f:
    model_store["matrix"]=pickle.load(f)
  
  with open(os.path.join(OUTPUT_DIR, "user_similarity.pkl"), "rb") as f:
    model_store["sim_df"]=pickle.load(f)
  print("모델 로드 완료")


def predict_rating(user_id:int, movie_id:int)->float:
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
  


def get_recommendations(user_id:int, top_k:int):
    matrix = model_store["matrix"]
    sim_df = model_store["sim_df"]
    
    
    if user_id not in sim_df.index:
        raise HTTPException(
            status_code=404, detail=f"user_id {user_id}를 찾을 수 없습니다."
        )
    watched = set(matrix.loc[user_id].dropna().index.tolist())
    candicates =  [mid for mid in matrix.columns if mid not in watched]

    scored = []

    for movie_id in candicates:
       pred = predict_rating(user_id, movie_id)
       scored.append({"movie_id": int(movie_id), "predicted_rating":round(pred,2)})
    
    scored.sort(key=lambda x: x["predicted_rating"], reverse=True )
    return scored[:top_k]

