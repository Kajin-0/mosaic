# Phase 4 Calibration Vertical Slice Protocol

## Purpose
Prove the Mosaic mobile/auth/API/database architecture before introducing validated questionnaires, synthetic images, or matching inference.

## Trial protocol
The Phase 4 instrument is deliberately non-scientific infrastructure scaffolding:

- instrument key: `p4-text-pair`
- instrument version: `p4-text-pair-1.0.0`
- policy version: `mock-calibration-p4-0.2.0`
- target: 10 trials
- response set: `left`, `right`, `both`, `neither`
- stimuli: deterministic text pairs embedded in the engine

Every presented experiment persists:

- immutable experiment UUID
- pseudonymous subject UUID
- session UUID
- ordinal
- stimulus ID and stimulus version
- exact stimulus JSON presented to the user
- response option set
- policy version
- server-authored timestamp

Every accepted response persists:

- experiment/session/subject references
- client idempotency UUID
- raw response
- optional client timestamp
- authoritative server timestamp
- policy version

## Required behavior
1. An unauthenticated calibration request is rejected.
2. The first authenticated `/next` call creates the pseudonymous subject mapping, session, and first trial.
3. Repeating `/next` before answering returns the same experiment.
4. The accepted response is immutable raw evidence.
5. Repeating the exact submission with the same `client_response_id` is accepted as a duplicate without adding evidence.
6. Reusing an idempotency key with different evidence is a conflict.
7. Restarting/signing in again resumes from persisted evidence; the client does not supply an authoritative completed-trial count.
8. After 10 responses, the session becomes complete and `/next` reports completion.
9. The database history alone reconstructs all 10 presentations and responses.
10. Direct authenticated-client writes to the science tables fail.

## Scope boundary
Passing this protocol proves infrastructure behavior only. It does not validate any relationship construct, preference model, attraction model, or matching algorithm.
