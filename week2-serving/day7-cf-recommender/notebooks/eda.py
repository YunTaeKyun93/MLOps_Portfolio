import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm 
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, '..', 'data', 'ml-1m', 'ratings.dat')
output_path = os.path.join(base_dir, '..', 'outputs')
os.makedirs(output_path, exist_ok=True)
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False



ratings = pd.read_csv(
  file_path,
  sep="::",
  engine="python",
  names=["user_id", "movie_id", "rating", "timestamp"]
)


print(f"총 평점 수: {len(ratings):,}")
print(f"총 유저 수: {ratings['user_id'].nunique():,}")
print(f"총 영화 수: {ratings['movie_id'].nunique():,}")
print(ratings.head())

plt.figure(figsize=(8,5))
ratings['rating'].value_counts().sort_index().plot(kind='bar', color='steelblue')
plt.title("평점 분포")
plt.xlabel('평점')
plt.ylabel("개수")
plt.tight_layout()
plt.savefig(os.path.join(output_path, 'rating_distribution.png'))
print("평점 분포 저장 완료")
plt.show()



top10 = ratings.groupby("movie_id")['rating'].count().sort_values(ascending=False).head()

plt.figure(figsize=(10, 6))
top10.plot(kind='bar', color='coral')
plt.title('인기 영화 Top 10 (평점 수 기준)')
plt.xlabel('영화 ID')
plt.ylabel('평점 수')
plt.tight_layout()
plt.savefig(os.path.join(output_path, 'top10_movies.png'))
print("인기 영화 Top 10 저장 완료")
plt.show()



user_rating_count = ratings.groupby('user_id')['rating'].count()

plt.figure(figsize=(10, 5))
plt.hist(user_rating_count, bins=50, color='mediumseagreen', edgecolor='white')
plt.title('유저별 평점 개수 분포')
plt.xlabel('평점 개수')
plt.ylabel('유저 수')
plt.tight_layout()
plt.savefig(os.path.join(output_path, 'user_rating_distribution.png'))
print("유저별 평점 분포 저장 완료")
plt.show()
