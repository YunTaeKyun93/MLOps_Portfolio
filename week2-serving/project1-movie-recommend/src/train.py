import os
import pickle
from tqdm import tqdm
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "ml-1m", "ratings.dat")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


def load_data(data_path: str) -> pd.DataFrame:
    df = pd.read_csv(
        data_path,
        sep="::",
        engine="python",
        names=["user_id", "movie_id", "user_rating", "timestamp"],
    )
    df = df[["user_id", "movie_id", "user_rating"]]
    print(
        f"✅ 로딩 완료: {len(df):,}건 | 사용자 {df['user_id'].nunique():,}명 | 영화 {df['movie_id'].nunique():,}개"
    )
    return df


def build_matrix(df: pd.DataFrame):
    matrix = df.pivot_table(index="user_id", columns="movie_id", values="user_rating")
    print(
        f"✅ Matrix shape: {matrix.shape} | NaN 비율: {matrix.isna().mean().mean() * 100:.1f}%"
    )
    return matrix


def compute_similarity(matrix):
    sparse = csr_matrix(matrix.fillna(0))

    sim = cosine_similarity(sparse)
    sim_df = pd.DataFrame(sim, index=matrix.index, columns=matrix.index)

    print(f"✅ Similarity Matrix shape: {sim_df.shape}")
    return sim_df


def predict_rating(user_id, movie_id, matrix, sim_df):
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
        return (valid_ratings * valid_sims).sum() / valid_sims.sum()

    return movie_ratings.mean()


def evaluate(test_df, matrix, sim_df):
    predictions = []
    true_ratings = []

    for _, row in tqdm(test_df.iterrows(), total=len(test_df), desc="예측중"):
        pred = predict_rating(row["user_id"], row["movie_id"], matrix, sim_df)
        predictions.append(pred)
        true_ratings.append(row["user_rating"])

    rounded = [round(x) for x in predictions]
    acc = accuracy_score(true_ratings, rounded)
    print(f"✅ Accuracy: {acc * 100:.1f}%")
    return acc


def save_model(matrix, sim_df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "user_item_matrix.pkl"), "wb") as f:
        pickle.dump(matrix, f)
    with open(os.path.join(OUTPUT_DIR, "user_similarity.pkl"), "wb") as f:
        pickle.dump(sim_df, f)
    print("💾 저장 완료!")


df = load_data(data_path=DATA_PATH)
train_df, test_df = train_test_split(df, test_size=0.02, random_state=42)
matrix = build_matrix(train_df)
sim_df = compute_similarity(matrix=matrix)


result = predict_rating(1, 1193, matrix, sim_df)
print(f"유저 1의 영화 1193 예측 평점: {result:.2f}")


acc = evaluate(test_df, matrix, sim_df)
save_model(matrix, sim_df)
