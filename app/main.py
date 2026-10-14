from fastapi import FastAPI, Request, HTTPException
from app.model import ChatRequest, ChatResponse
from starlette import status
from contextlib import asynccontextmanager
import httpx
import os
from dotenv import load_dotenv
from app.providers import *
import time

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

groq_url = GROQ

@asynccontextmanager
async def lifespan(app: FastAPI): # function to create the client lifespan

    async_client = httpx.AsyncClient()
    app.state.async_client = async_client

    # anything above this 'yield ' must be loaded before the server runs
    yield 
    # anything below this 'yield' must run after the application is finished

    await async_client.aclose()

app = FastAPI(lifespan=lifespan) # boot up the fastapi application with the lifespan function created so it can references it

@app.get("/")
def home():
    return {"message": "ok, working"}

def get_async_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.async_client

@app.post("/chat", response_model=ChatResponse)
async def send_msg(body: ChatRequest, request: Request):
    client = get_async_client(request) # start a async client instance

    try:
        start = time.perf_counter() # calculates the start time of the api call
        response = await client.post(url=f"{groq_url}", 
                                    headers={"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"}, 
                                    json={"model": "qwen/qwen3.8-27b", "messages": [{"role": "user", "content": body.message}]},
                                    timeout=25.0
                                    )
        duration = time.perf_counter() - start # calculates the final full latency from call to final response

        raw_response = response.json()

        #breakpoint() #breakpoint was used to debug the variables

        formatted_response = ChatResponse( # formatting the response in accordance to the created custom response model
            reply = raw_response.get("choices")[0].get("message").get("content"),
            model = raw_response.get("model"),
            latency_ms = duration
        )

        return formatted_response
    except httpx.TimeoutException: #timeout exception call
        raise HTTPException(status_code = status.HTTP_504_GATEWAY_TIMEOUT, detail="Provider Timeout")