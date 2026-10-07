import os
import tempfile
from pathlib import Path

import pytest

os.environ["DATABASE_PATH"] = str(Path(tempfile.gettempdir()) / "ksc-test-orders.db")
os.environ["KSC_SECRET_KEY"] = "test-secret"

from app import app, init_db


@pytest.fixture()
def client():
    app.config.update(TESTING=True, SECRET_KEY="test-secret")
    init_db()

    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"KSC Wholesale Chicken" in response.data


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_place_order(client):
    response = client.post(
        "/order",
        data={
            "name": "Test Customer",
            "phone": "9999999999",
            "cut": "Whole Chicken",
            "quantity": "2 kg",
            "notes": "Test order",
        },
    )
    assert response.status_code == 302
