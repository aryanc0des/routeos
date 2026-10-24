import pytest
import respx
import httpx

from main import app
from model import *
from providers import *

from fastapi.testclient import TestClient

@respx.mock
def test_groq_chat_timeout_error():
    respx.post(GROQ).mock(
        side_effect=httpx.TimeoutException("Request timed out") # side_effect is used when testing exceptions
    )

    with TestClient(app) as client:
        response = client.post("/chat/groq", json={"message": "hello groq"})

    assert response.status_code == 504
    assert response.json()["detail"] == "Provider Timeout"


@respx.mock
def test_gemini_chat_timeout_error():
    respx.post(GEMINI).mock(
        side_effect=httpx.TimeoutException("Request timed out") # side_effect is used when testing exceptions
    )

    with TestClient(app) as client:
        response = client.post("/chat/gemini", json={"message": "hello gemini"})

    assert response.status_code == 504
    assert response.json()["detail"] == "Provider Timeout"