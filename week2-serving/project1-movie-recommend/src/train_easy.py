import os
import pickle
import numpy as np
from tqdm import tqdm
from datasets import load_dataset
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "ml-1m", "ratings.dat")
# 현재 온라인 에서 불러오니까 지원하지 않는 버전인지 그냥 다운받아서 사용하기로함

df = pd.read_csv(
    DATA_PATH,
    sep="::",
    engine="python",
    names=["user_id", "movie_id", "user_rating", "timestamp"],
)

# sep은  dat가 기본적으로 , 가 아닌  ::  으로 해서 명시적으로 하기 위해
# 기본적으로  컬럼명이 없기에 names로 컬럼명 작성

df = df[["user_id", "movie_id", "user_rating"]]
# 배열로 감싼 이유 시리즈로 나오기에 데이터프레임으로 하기위해

print(df.head())
print(df.shape)
# shape
# (1000209, 3)


print("---" * 6)

print(df["user_id"].nunique())
print(df["movie_id"].nunique())

# unique 갯수
# 6040
# 3706
#  유저의 수와 영화의 갯수 확인

print("-" * 60)
train_df = df.copy()
matrix = train_df.pivot_table(index="user_id", columns="movie_id", values="user_rating")


print(matrix.shape)
print(matrix.isna().mean().mean())
print(matrix.head())
# (6040, 3706)
# 0.9553163743776871
# mean()이 2개인 이유 첫번째 mean이 평가 하지 않은 영화의 열을 구함 두번째 mean이 그 모든 값의 평균이라
# 얼마나 비어잇냐
# 현재 95퍼가 비어있어서 sparse 한 자료가 나옴


sparse = csr_matrix(matrix.fillna(0))
sim = cosine_similarity(sparse)

print("-" * 60)
print(sim.shape)

# csr_matrix 현재 95퍼가 비어잇는 sparse한 자료이다 보니 효율적으로 저장하는 자료구조
# 우리가 모두가 행렬을 만들면 쓸모없는 공간도 차지 하게됨(대부분 0 또는 nan이기 때문에)
# 그렇기에 0 아닌 값만 저장하면 효율적으로 사용가능
# 왜 fillna로 0으로 바꾸는가??
# cosine_similarity 에서는 NAN을 지원안하기도 하고 nan 또한 계산 불가능해서
# 임의적으로 0은 안본 영화다 라고 생각
# 그리고 해당 sim이 유저 값이 된 건 현재 구하고 잇는게 유저 관계도 이기때문에
# 첫번째 행의 값의 유사도가 나옴 heatmap 과 유사하다고 생각하면됨
# (6040, 6040)
user_id = matrix.index[0]
print("-" * 60)
print(user_id)


user_ratings = matrix.loc[user_id]
unseen_movies = user_ratings[user_ratings.isna()].index
print(len(unseen_movies))
# 테스트용으로 한명의 유저를 기준 안본영화 갯수 구하기

sim_df = pd.DataFrame(sim, index=matrix.index, columns=matrix.index)
user_sim = sim_df.loc[user_id]
# matrix는 아이디 시작이 1부터인데 이제
# sim 은  np 배열인데 배열의 시작은 0부터라
# 보정이 필요한데 sim[user_id -1] 이런식의 방법은 위험하다고함
# 항상 연속이라는 보장이 없다면 꺠질 위험잇음 그래서 df방식으로 변경


movie_id = unseen_movies[0]

movie_ratings = matrix[movie_id]
print("*" * 60)
print("user_sim", user_sim)
print("movie_ratings", movie_ratings)
valid_mask = movie_ratings.notna()
# notna를 사용해서  결측치가 아닌 값을 찾는데 해당 영화를 본사람만 평점에 쓰여야해서

print(valid_mask)
valid_ratings = movie_ratings[valid_mask]
valid_sims = user_sim[valid_mask]


# movie_ratings  = 모드 사용자들의 해당 영화 평점
# user_sim  = 현재 사용자와 모든 사용자의 유사도
# valid_mask = 해당 영화를 본 사용자 만 필터
# valid_ratings = 영화 i를 본 사용자들의 평점
# valid_sims = 그 사용자들과의 유사도


pred = (valid_sims * valid_ratings).sum() / valid_sims.sum()
print("-" * 30, "result", "-" * 30)
print(pred)


predictions = {}


for movie_id in unseen_movies:
    movie_ratings = matrix[movie_id]
    valid_mask = movie_ratings.notna()

    valid_ratings = movie_ratings[valid_mask]
    valid_sims = user_sim[valid_mask]

    if valid_sims.sum() > 0:
        pred = (valid_sims * valid_ratings).sum() / valid_sims.sum()
        predictions[movie_id] = pred


# 예측 평점 높은 순으로 상위 10개 추천
top10 = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:10]
print(top10)


train_df, test_df = train_test_split(df, test_size=0.02, random_state=10)
print(f"Train: {len(train_df):,}건 | Test: {len(test_df):,}건")
