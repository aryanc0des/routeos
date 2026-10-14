import pytest
import respx
import httpx
from app.main import app
from app.model import *
from app.providers import *

from fastapi.testclient import TestClient

@respx.mock # respx decorator initialization to create a mock reply for testing
def test_chat_mock_reply():
    respx.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={
            "choices": [{"message": {"content": "fake reply"}}],
            "model": "qwen/qwen3.8-27b"
        })
    )

    with TestClient(app) as client: # test client to call endpoints, not actual server running but self contained test environment
        response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200 #anything other than this will fail the test
    assert response.json()["reply"] == "fake reply"