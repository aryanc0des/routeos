# Concept: FastAPI lifespan + shared client

## What it does

`lifespan` controls what happens at the start and end of the app's life,
using an async context manager (`@asynccontextmanager`) with `yield`.
Everything above the `yield` runs once, before the app starts serving
requests. Everything after the `yield` runs once, when the app shuts down.

In RouteOS, the `httpx.AsyncClient` is created above the `yield`, so it's
ready and warmed up before any request comes in, instead of being created
on demand per request.

## Why we need one shared client instead of one per request

Creating a new client per request doesn't scale, it puts a heavier load on
the server. A shared client is reused across all requests through a
connection pool, instead of every request queuing up its own separate
connection.

The provider calls (Groq, OpenAI, etc.) are external API calls, which can
sometimes take longer than expected. Using `async`/`await` means the app
doesn't block while waiting on that response, it can keep handling other
work in the meantime, rather than every request stalling the whole server.

## What breaks if you get this wrong

- No `lifespan` → no `yield`, and the client can't be created upfront. It
  ends up booting later than it should, adding latency for whoever's using
  the app at that moment.
- A new client per request → a fresh TLS handshake every single time,
  instead of reusing a warm connection, adding real delay and heavier load
  on the server.