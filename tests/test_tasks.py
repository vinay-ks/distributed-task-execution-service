from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_task():
    response = client.post("/tasks", json={"name": "test task"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING"


def test_list_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
