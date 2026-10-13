from fastapi import FastAPI, Request, HTTPException
from model import ChatRequest, ChatResponse
from starlette import status
from contextlib import asynccontextmanager
import httpx
import os
from dotenv import load_dotenv
from providers import *
import time

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

groq_url = GROQ

@asynccontextmanager
async def lifespan(app: FastAPI):

    async_client = httpx.AsyncClient()
    app.state.async_client = async_client

    yield

    await async_client.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "ok, working"}

def get_async_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.async_client

@app.post("/chat")
async def send_msg(body: ChatRequest, response_model: ChatResponse, request: Request):
    client = get_async_client(request)

    try:
        start = time.perf_counter()
        response = await client.post(url=f"{groq_url}", 
                                    headers={"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"}, 
                                    json={"model": "qwen/qwen3.8-27b", "messages": [{"role": "user", "content": body.message}]},
                                    timeout=25.0
                                    )
        duration = time.perf_counter() - start

        raw_response = response.json()
        #breakpoint()
        formatted_response = ChatResponse(
            reply = raw_response.get("choices")[0].get("message").get("content"),
            model = raw_response.get("model"),
            latency_ms = duration
        )

        return formatted_response
    except httpx.TimeoutException:
        raise HTTPException(status_code = status.HTTP_504_GATEWAY_TIMEOUT, detail="Provider Timeout")