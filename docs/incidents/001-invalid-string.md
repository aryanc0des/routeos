# Incident 001: Invalid string error on ChatResponse

## What happened

Early version of the code took the raw Groq response and did
`raw_response.get("choices")[0]` directly, then tried to parse that
straight into the `ChatResponse` Pydantic model. But that value is still
the whole `choices[0]` object (a dict containing `message`, `finish_reason`,
etc.), not the actual reply text. Pydantic expected a plain string for the
`reply` field and got a list/dict instead, raising an "invalid string"
validation error.

## Suspected cause

Didn't drill down far enough into the response structure before handing
it to the model. Needed `.get("message").get("content")` to actually reach
the string, not just the top-level `choices[0]` object.

## What I'd do differently next time

Print or inspect the raw response structure once before writing the
parsing code, instead of guessing the shape and letting Pydantic's error
tell me it's wrong.