# RouteOS

**A reliability layer for LLM APIs.**

RouteOS is a self-hosted gateway that sits between applications and LLM providers (OpenAI, Gemini, and others). It handles rate limiting, retries with backoff, circuit breakers on provider failure, request fallback, and exact + semantic caching, with full observability through request logs and metrics.

Built from scratch, one piece at a time, to understand every moving part rather than to compete with production gateways like [LiteLLM](https://github.com/BerriAI/litellm) or [Portkey](https://github.com/Portkey-AI/gateway).

> **Status: early build.** This README documents the target architecture. The Results table below fills in as each piece ships — see [Roadmap](#roadmap).

---

## Why

Every app that calls an LLM provider eventually needs the same things: don't blow through rate limits, don't fail when a provider has an outage, don't pay twice for the same question, and know what it's costing you. Most teams bolt this on late, badly, per-app. RouteOS is that layer, built once, in front of everything.

## Architecture

```
Apps → Auth → Rate limiter → Cache → Router → Providers
                   │            │        │
                 Redis    Postgres+   Redis +
               (counters)  pgvector   circuit
                           (log, embeds) breakers
```

Request path: a call is authenticated, checked against the per-client rate limit, looked up in cache (exact match, then semantic), and — on a miss — sent to a provider through the router, which handles timeouts, retries, and fallback to the next provider if one is down.

## Features

- [ ] Async proxy to provider APIs (no SDKs, raw `httpx`)
- [ ] Per-client API keys
- [ ] Token-bucket rate limiting (requests/min and tokens/min), backed by Redis for correctness across workers
- [ ] Timeouts, retries with exponential backoff + jitter
- [ ] Circuit breaker per provider, with fallback chains
- [ ] Exact-match caching
- [ ] Semantic caching (embeddings + pgvector)
- [ ] Request logging: tokens, latency, cost per client/provider
- [ ] Prometheus metrics + Grafana dashboard
- [ ] Load tested with k6, overhead measured at p50/p95/p99

## Quickstart

```bash
git clone https://github.com/<you>/routeos.git
cd routeos
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your provider API keys
uvicorn app.main:app --reload
```

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer <your-client-key>" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

## Results

Filled in as each milestone ships, with the number, the prediction made beforehand, and the command to reproduce it.

| Milestone | Metric | Predicted | Measured | Reproduce |
| --- | --- | --- | --- | --- |
| Proxy (wk 1) | Overhead vs. direct call | — | — | — |
| Rate limiter v2 (wk 5) | Over-admission at 200 concurrent clients | 0 | — | — |
| Circuit breaker (wk 6-7) | Success rate with vs. without fallback | — | — | — |
| Cache (wk 8-9) | Semantic cache false-hit rate | — | — | — |
| Load test (wk 11) | Gateway overhead p50/p95/p99 | — | — | — |

## Roadmap

See [docs/design/](docs/design/) for the design note behind each piece and [docs/incidents/](docs/incidents/) for what broke along the way. Built in public, three posts planned as the project lands: Redis-backed rate limiting, the circuit breaker and cache, and the final numbers with what broke.

## Design philosophy

- Every milestone ships with a test and a measured number, not just working code.
- Complexity is added only when a test shows the simple version failing (in-memory before Redis, exact cache before semantic).
- The reference gateways are read *after* each piece works, not before — the goal is to arrive at the same design independently, then compare.

## Tech

Python, FastAPI, `httpx`, Redis, PostgreSQL + pgvector, Docker, Prometheus/Grafana, pytest + `respx`, k6.

## License

MIT
