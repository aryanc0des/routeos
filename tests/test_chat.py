import pytest
import respx
import httpx
from app.main import app
from app.model import *
from app.providers import *

from fastapi.testclient import TestClient

@respx.mock # respx decorator initialization to create a mock reply for testing
def test_groq_chat_mock_reply():
    respx.post(GROQ).mock(
        return_value=httpx.Response(200, json={
            "choices": [{"message": {"content": "fake test reply"}}],
            "model": "qwen/qwen3.8-27b"
        })
    )

    with TestClient(app) as client: # test client to call endpoints, not actual server running but self contained test environment
        response = client.post("/chat/groq", json={"message": "hello groq"})

    assert response.status_code == 200 # anything other than this will fail the test
    assert response.json()["reply"] == "fake test reply"


@respx.mock
def test_gemini_chat_mock_reply():
    respx.post(GEMINI).mock(
        return_value=httpx.Response(200, json={"modelVersion": "gemini-3.5-flash-lite",
                                               "candidates": [{"content": {"parts": [{"text": "fake test reply"}]}}]
                                               })
    )
    with TestClient(app) as client:
        response = client.post("/chat/gemini", json={"message": "hello gemini"})

    assert response.status_code == 200 # anything other than this will fail the test
    assert response.json()["reply"] == "fake test reply"