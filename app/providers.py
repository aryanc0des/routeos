import httpx
from configs import get_async_client, groq_api_key, gemini_api_key
from starlette import status
import time
from fastapi import Request, HTTPException
from model import ChatRequest, ChatResponse

GROQ = "https://api.groq.com/openai/v1/chat/completions"

GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"

async def call_groq(message: str, request: Request):
    client = get_async_client(request) # start a async client instance

    try:
        start = time.perf_counter() # calculates the start time of the api call

        response = await client.post(url=f"{GROQ}",
                                     headers={"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"},
                                     json={"model": "qwen/qwen3.8-27b", "messages": [{"role": "user", "content": message}]},
                                     timeout=25.0
                                     )

        duration = time.perf_counter() - start # calculates the final full latency from call to final response

        raw_response = response.json()

        formatted_response = ChatResponse( # formatting the response in accordance to the created custom response model
            reply = raw_response.get("choices")[0].get("message").get("content"),
            model = raw_response.get("model"),
            latency_ms= duration
        )

        return formatted_response
    
    except httpx.TimeoutException: #timeout exception call
        raise HTTPException(status_code = status.HTTP_504_GATEWAY_TIMEOUT, detail="Provider Timeout")


async def call_gemini(message: str, request: Request):
    client = get_async_client(request)

    try:

        start = time.perf_counter()

        response = await client.post(url=GEMINI,
                            headers={"x-goog-api-key": f"{gemini_api_key}", "Content-Type": "application/json"},
                            # json={"model": "gemini-2.5-flash-lite", "messages": [{"role": "user", "content": message}]},
                            json={"model": "gemini-3.5-flash-lite",
                                    "contents": {
                                    "parts": [{
                                        "text": message
                                        }],
                                    "role": "user"
                                }},
                            timeout=25.0
                            )
        
        duration = time.perf_counter() - start

        raw_response = response.json()

        #breakpoint()

        formatted_response = ChatResponse(
            reply = raw_response.get("candidates")[0].get("content").get("parts")[0].get("text"),
            model = raw_response.get("modelVersion"),
            latency_ms = duration
        )

        return formatted_response

    except httpx.TimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Provider Timeout")