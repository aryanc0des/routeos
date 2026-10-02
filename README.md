# routeos
RouteOS is a self-hosted LLM gateway sitting between applications and model providers (OpenAI, Gemini, and others). It handles rate limiting, retries with backoff, circuit breakers on provider failure, request fallback, and exact + semantic caching, with full observability via request logs and metrics. Built from scratch to understand every part
