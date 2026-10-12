# 001: The /chat proxy endpoint

## Problem
Forward a user's message to an LLM provider and return the reply, without
using the provider's SDK, so every part of the call is visible and ours.

## Request / response

Request:
```json
{"message": "why is a german shepherd named that"}
```

Success response:
```json
{"reply": "...", "model": "...", "latency_ms": 142}
```

Error response:
```json
{"error": "provider_timeout"}
```

## Approach
- `POST /chat`, calls the provider over raw `httpx`, no SDK.
- SDKs hide the exact mechanics (the HTTP call, headers, retries) this
  project exists to learn, and lock us into whatever interface the vendor
  chose.
- One shared `httpx.AsyncClient` for the whole app's lifetime (created in
  FastAPI's `lifespan`, closed on shutdown), not one per request.
  A new client per request opens a fresh TCP connection and does a new TLS
  handshake every time; a shared client reuses a warm connection pool.
  Async already lets concurrent requests share that client without
  blocking each other, so there's no bottleneck from sharing it.

## Alternative rejected
One `AsyncClient` per request. Rejected: wasteful (new connection + TLS
handshake per call) for no benefit, since the shared client already
handles concurrency safely.

## Failure handling
- Timeout set explicitly on the `httpx` call (25s), rather than relying on
  the caller's own timeout.
- On `httpx.TimeoutException`: return **504 Gateway Timeout**, not 429.
  429 means "too many requests" (our own rate limiter will use it later,
  in week 4) and doesn't apply here. 504 is correct because we're acting
  as a gateway that didn't get a response from the upstream in time.

## Measurement
Prediction: proxy overhead vs. calling the provider directly is small,
roughly 10-25ms (network + serialization), under light load. To be
measured once the endpoint works and logged in the README's Results table.