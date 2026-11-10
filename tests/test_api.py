
from fastapi.testclient import TestClient

from src.food11 import serve


class FakeModel:
    def predict(self, x):
        # Simulated model scores: Bread has the highest score.
        return [[0.90] + [0.01] * 10]


def test_health(monkeypatch):
    monkeypatch.setenv("SKIP_MODEL", "1")

    with TestClient(serve.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_returns_valid_json(monkeypatch):
    monkeypatch.setenv("SKIP_MODEL", "1")

    with TestClient(serve.app) as client:
        # Replace the real model with a fake model.
        monkeypatch.setattr(serve, "model", FakeModel())

        with open("tests/fixtures/bread.jpg", "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("bread.jpg", f, "image/jpeg")},
            )

    assert response.status_code == 200

    body = response.json()

    assert body["category"] == "Bread"
    assert 0.0 <= body["confidence"] <= 1.0
