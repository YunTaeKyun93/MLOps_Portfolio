from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.recommend import load_models, model_store
from app.routers.recommend import router

@asynccontextmanager
async def lifespan(app:FastAPI):
  load_models()
  if model_store :
    print(f"  Matrix: {model_store['matrix'].shape}")
    print(f"  Similarity: {model_store['sim_df'].shape}")
 
  yield
  model_store.clear()


app = FastAPI(
  title="CF Recommender API",
  description="Collaborative Filtering 기반 영화 추천 AP",
  version="1.0.0",
  lifespan=lifespan
)



app.include_router(router)
