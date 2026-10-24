import respx
import httpx
import pytest
from main import app
from model import *
from providers import *
from fastapi.testclient import TestClient

@respx.mock
def test_unknown_provider():
    respx.post(GROQ).mock(
        return_value=httpx.Response(400)
    )

    with TestClient(app) as client:
        response = client.post("/chat/garbage", json={"message": "hello"})


    assert response.status_code == 400