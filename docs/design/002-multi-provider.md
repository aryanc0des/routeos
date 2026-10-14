# Design Note: Multi-Provider Routing (Week 2)

## Goal

Add Gemini as a second provider alongside Groq, selectable per-request via a
path param, without hardcoding either provider's response shape into the
route handler.

## Why this is needed

The current `/chat` endpoint has Groq's response shape built directly into
the handler: `raw_response.get("choices")[0].get("message").get("content")`.
That only works because there's one provider. Gemini's response is shaped
completely differently:

```json
{
  "candidates": [
    {
      "content": {
        "parts": [{ "text": "..." }],
        "role": "model"
      }
    }
  ]
}
```

Reply lives at `candidates[0].content.parts[0].text`, not
`choices[0].message.content`. Any code that assumes one shape breaks the
moment a second provider is added. This has to be solved at the boundary,
not patched over with more `if` branches inside the route.

## Interface

Every provider gets its own function in `providers.py`, same signature,
same return contract:

```python
async def call_groq(message: str, client: httpx.AsyncClient) -> dict:
    ...
    return {"reply": ..., "model": ..., "latency_ms": ...}

async def call_gemini(message: str, client: httpx.AsyncClient) -> dict:
    ...
    return {"reply": ..., "model": ..., "latency_ms": ...}
```

Each function absorbs its own provider's response shape internally. Whatever
Groq or Gemini actually return, by the time the function returns, it's
always `{"reply": str, "model": str, "latency_ms": float}`. `main.py` never
needs to know that the two providers disagree about where the reply text
lives.

## Routing

Provider selected via path param: `POST /chat/{provider}`.

```python
@app.post("/chat/{provider}")
async def send_msg(provider: str, body: ChatRequest, request: Request):
    if provider == "groq":
        result = await call_groq(body.message, client)
    elif provider == "gemini":
        result = await call_gemini(body.message, client)
    else:
        raise HTTPException(status_code=400, detail="unknown provider")
    return ChatResponse(**result)
```

URLs, API keys, and the calling function for each provider stay together in
`providers.py`, one block per provider. Not split into separate
config/functions files — a URL and the function that uses it aren't
independent facts, and splitting them buys nothing at 2 providers.

## Explicitly out of scope for this milestone

- **Circuit breakers / fallback chains** — need multiple providers actually
  working first; this is weeks 6-7 per the roadmap.
- **Streaming** — changes the response contract and the latency measurement
  entirely; tackled only after routing is solid, as its own milestone.
- **Dict-based provider dispatch** (`PROVIDERS = {"groq": call_groq, ...}`)
  — the `if/elif` chain is fine at 2 providers. Switch to a dict when a
  3rd or 4th provider makes the chain actually painful, not before.

## Known risk

Gemini's error responses, rate-limit behavior, and timeout behavior haven't
been checked yet — only the happy-path shape above has been confirmed.
Error handling for `call_gemini` needs the same timeout/504 treatment Groq
already has, adapted to however Gemini actually fails (that's unconfirmed,
not assumed).

## Reproduce

```bash
curl -X POST http://localhost:8000/chat/gemini \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```