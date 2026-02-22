import pytest
from fastapi.testclient import TestClient
from src.service import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["model_loaded"] is True


def test_predict_valid(client):
    response = client.post("/predict", json={"user_id": 1, "movie_id": 1193})
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert 0 <= data["predicted_rating"] <= 5


def test_predict_unknown_user(client):
    response = client.post("/predict", json={"user_id": 999999, "movie_id": 1193})
    assert response.status_code == 200
    assert response.json()["predicted_rating"] == 3.0


def test_predict_unknown_movie(client):
    response = client.post("/predict", json={"user_id": 1, "movie_id": 999999})
    assert response.status_code == 200
    assert response.json()["predicted_rating"] == 3.0


def test_predict_invalid_body(client):
    response = client.post(
        "/predict", json={"user_id": "not_a_number", "movie_id": 1193}
    )
    assert response.status_code == 422


def test_recommend_valid(client):
    response = client.get("/recommend/1")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert len(data["recommendations"]) == 5


def test_recommend_top_k(client):
    response = client.get("/recommend/1?top_k=3")
    assert response.status_code == 200
    assert len(response.json()["recommendations"]) == 3


def test_recommend_sorted(client):
    response = client.get("/recommend/1?top_k=5")
    ratings = [r["predicted_rating"] for r in response.json()["recommendations"]]
    assert ratings == sorted(ratings, reverse=True)


def test_recommend_unknown_user(client):
    response = client.get("/recommend/999999")
    assert response.status_code == 404
