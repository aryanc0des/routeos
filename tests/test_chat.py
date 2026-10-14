import pytest
import respx
import httpx
from app.main import app
from app.model import *
from app.providers import *

from fastapi.testclient import TestClient

@respx.mock
def test_chat_mock_reply():
    respx.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={
            "choices": [{"message": {"content": "fake reply"}}],
            "model": "qwen/qwen3.8-27b"
        })
    )

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json()["reply"] == "fake reply"