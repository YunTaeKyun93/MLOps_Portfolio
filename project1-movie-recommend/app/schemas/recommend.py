from pydantic import BaseModel

class PredictRequest(BaseModel):
  user_id: int
  movie_id : int


class PredictResponse(BaseModel):
  user_id: int
  movie_id:int
  predicted_rating:float
  rounded_rating:int


class RecommendResponse(BaseModel):
  user_id:int
  recommendations : list[dict]






  # ─────────────────────────────────────────────
# DTO 정의 (Pydantic BaseModel)
#
# [백엔드 관점]
# NestJS의 DTO와 완전히 동일한 개념
# class PredictDto { user_id: number; movie_id: number }
# ───
