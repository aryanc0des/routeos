import os 
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import httpx

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI): # function to create the client lifespan

    async_client = httpx.AsyncClient()
    app.state.async_client = async_client

    # anything above this 'yield ' must be loaded before the server runs
    yield 
    # anything below this 'yield' must run after the application is finished

    await async_client.aclose()

def get_async_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.async_client