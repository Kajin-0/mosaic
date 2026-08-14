# ADR 0005 — Separate Immutable Measurement Evidence from Versioned Derived Scores

## Status
Accepted for Phase 5.

## Context
Mosaic's later relationship models will change. If raw questionnaire/onboarding responses are overwritten by current scores, historical evidence becomes scientifically uninterpretable and model improvements cannot be evaluated against the same observations.

Phase 5 therefore needs a measurement substrate that survives future changes in item selection, scoring, and inference.

## Decision
Raw measurement evidence and derived scoring outputs are different persistence classes.

### Raw evidence
`measurement_presentations` and `measurement_responses` are immutable. Every accepted response retains:
- pseudonymous subject;
- server-owned session;
- presentation ID and ordinal;
- item ID, item version, item kind, and exact item payload;
- instrument version;
- selection-policy version;
- raw typed answer;
- client idempotency key;
- client timestamp when supplied;
- server timestamp.

Neither mobile clients nor later scoring code may rewrite this evidence.

### Derived state
`measurement_score_runs` is append-only and stores:
- scoring implementation version;
- SHA-256 fingerprint of the immutable evidence used;
- number of responses scored;
- derived score payload;
- computation timestamp.

A new scoring implementation creates a new score run over the same evidence. It never updates the response rows.

## Consequences
- Historical responses can be rescored under later models.
- Two scoring implementations can be compared on exactly the same evidence fingerprint.
- Score drift is attributable to scoring code/version rather than silent data mutation.
- The current Phase 5 score functions remain explicitly mock infrastructure fixtures; this architecture does not grant them psychometric validity.
