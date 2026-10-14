# Concept: pytest, respx, and mocking

## What assert actually does

`assert` tells the code what is supposed to happen for a given value. If
the actual result doesn't match, the test fails right there. If it does
match, the test passes. That simple.

If even one `assert` in a test fails, that test fails immediately, it
doesn't keep going past the failure.

## Why we mock Groq instead of calling it for real

- As a codebase gets larger, manually testing every function and feature
  every time something changes becomes very hard. Writing a test per
  function/feature makes that much easier and repeatable.
- We don't want to waste resources, real API calls cost real tokens and
  money, every time we run the test suite.
- Mocking lets us reproduce errors and exceptions we couldn't otherwise
  trigger on demand, like the 504 timeout, which isn't something you can
  reliably force the real Groq API to do.

`respx` is the Python library used to mock HTTP requests during testing.

## Why return_value didn't test the timeout path, and side_effect did

`return_value` is used to return a specific response (an actual
`httpx.Response`, status code and JSON body included). `side_effect` is
used for raising an exception instead, like the timeout, so the call
actually fails the way it would in production, rather than coming back
as a normal (if oddly-coded) response.