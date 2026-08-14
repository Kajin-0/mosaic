# ADR 0004 — Server-authoritative calibration persistence

## Status
Accepted for Phase 4.

## Context
Phase 4 must prove an authenticated mobile user can complete a persistent, reconstructable calibration session through the FastAPI boundary. Raw experimental evidence must remain immutable, mobile retries must be idempotent, and privileged database credentials must never enter the client.

Direct authenticated-client writes to experimental tables would make the mobile application part of the scientific authority boundary and would permit a modified client to forge authored trials or raw evidence.

## Decision
- The mobile client sends its Supabase access token only to the Mosaic engine.
- The engine validates that token with Supabase Auth.
- The engine maps the account to a separate pseudonymous `science_subjects.subject_id`.
- Calibration sessions, authored trials, and responses are written only by the engine using a server-only elevated Supabase key.
- `anon` and `authenticated` receive no table privileges on the Phase 4 science tables.
- Trial and response rows are append-only; database triggers reject UPDATE and DELETE even through the privileged server role.
- A `client_response_id` UUID is the ingestion idempotency key. Reusing it with the same immutable payload returns the original logical acceptance as a duplicate; reusing it with different evidence is a conflict.
- `/v1/calibration/next` accepts no client-owned progress counter. Persisted server evidence determines the next ordinal and repeated calls return the same unanswered experiment.
- One session exists per subject/instrument/policy version. Once complete, `/next` reports completion rather than silently creating a new session.

## Consequences
This is intentionally stricter than the Phase 3 mock boundary. The client can render and submit experiments but cannot author scientific state. Restart/resume requires no locally authoritative session counter. Later policies can create a new session by changing the versioned instrument or policy rather than mutating historical evidence.

The current text pairs remain deterministic infrastructure stimuli only. This ADR does not claim psychometric, attraction, or matchmaking validity.
