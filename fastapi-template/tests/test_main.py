import pytest
from fastapi.testclient import TestClient
from main import app
import os
import json


# Sample data for testing
SAMPLE_DB_CONTENT = [
    {"id": 1, "name": "Test Product 1", "price": 10.0, "quantity": 100},
    {"id": 2, "name": "Test Product 2", "price": 20.0, "quantity": 50},
]


@pytest.fixture
def client():
    # Use a temporary db file for tests
    db_path = "app/db.json"
    original_content = None

    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            original_content = f.read()

    with open(db_path, "w") as f:
        json.dump(SAMPLE_DB_CONTENT, f, indent=2)

    with TestClient(app) as client:
        yield client

    # Restore original db file
    if original_content:
        with open(db_path, "w") as f:
            f.write(original_content)
    else:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Tech Store API"}


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_products(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Test Product 1"


def test_create_product(client):
    new_product = {"name": "New Gadget", "price": 99.99, "quantity": 10}
    response = client.post("/products", json=new_product)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == new_product["name"]
    assert "id" in data

    # Check if it was actually added
    response = client.get("/products")
    assert len(response.json()) == 3
