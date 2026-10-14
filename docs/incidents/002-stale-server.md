# Incident 002: NoneType error that resolved after breakpoint()

## What happened

After fixing the Incident 001 parsing bug, got a `NoneType` error on the
next run. Suspected the Groq response might be coming back empty. Used
`breakpoint()` to drop into `pdb` and inspect the variables directly,
confirmed the response was actually fine, full content, no `None`
anywhere. After exiting the debugger, the error was gone and the endpoint
worked normally, with no further code changes made.

## Suspected cause

Best guess: the server was running a stale version of the code despite
`--reload` being on, the reload hadn't fully picked up the latest fix yet.
Adding and then removing `breakpoint()` likely forced something closer to
a hard restart, which is what actually picked up the already-correct code.

Found the general term for this while searching: a "Heisenbug", a bug that
seems to change or disappear depending on how you try to observe it.

## What I'd do differently next time

Watch the terminal for the `Reloading...` / `Application startup complete`
message after every save, before testing, to confirm the server is
actually running the code I think it's running, rather than assuming.