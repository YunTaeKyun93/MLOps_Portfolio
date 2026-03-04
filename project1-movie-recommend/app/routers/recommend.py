
from app.services.recommend import model_store, predict_rating,get_recommendations
from app.schemas.recommend import PredictRequest, PredictResponse, RecommendResponse
from fastapi import APIRouter

router = APIRouter()

@router.get('/health')
def health():
  return {
    "status" :"OK",
     "model_loaded": len(model_store) > 0
  }


@router.post('/predict', response_model=PredictResponse)
def predict(request: PredictRequest):
  pred = predict_rating(request.user_id, request.movie_id)

  return PredictResponse(
    user_id=request.user_id,
    movie_id=request.movie_id,
    predicted_rating=round(pred,2),
    rounded_rating=round(pred)
  )


@router.get("/recommend/{user_id}", response_model=RecommendResponse)
def recommend(user_id:int, top_k:int =5):
  recommendations = get_recommendations(user_id, top_k)
  return RecommendResponse(
    user_id=user_id,
    recommendations= recommendations
  )
 
