import pytest
import respx
import httpx

from app.main import app
from app.model import *
from app.providers import *
from fastapi import HTTPException
from starlette import status

from fastapi.testclient import TestClient

@respx.mock
def test_chat_timeout_error():
    respx.post("https://api.groq.com/openai/v1/chat/completions").mock(
        side_effect=httpx.TimeoutException("Request timed out") # side_effect is used when testing exceptions
    )

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello groq"})

    assert response.status_code == 504
    assert response.json()["detail"] == "Provider Timeout"