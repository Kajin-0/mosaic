# Phase 5 Measurement Infrastructure Protocol

## Purpose
Prove that Mosaic can run a versioned, resumable heterogeneous measurement instrument and rescore historical evidence without mutating it.

## Mock instrument
The Phase 5 fixture contains exactly 20 items:
- 5 hard-constraint items;
- 5 rating/adaptive-question items;
- 5 scenario items;
- 5 forced-choice items.

These are deterministic infrastructure fixtures only. No psychometric or matchmaking validity is claimed.

## End-to-end protocol
1. Create a Supabase-authenticated test account.
2. Request the first server-authored measurement item.
3. Repeat the request and prove the same unanswered presentation is returned.
4. Submit a typed raw answer with a client idempotency UUID.
5. Repeat the exact submission and prove it is idempotent.
6. Complete items 1–10.
7. Re-authenticate and prove the server resumes the same session at item 11.
8. Complete all 20 items and verify all four renderer/item kinds appeared exactly five times.
9. Reconstruct the 20 presentations and 20 raw responses from PostgreSQL.
10. Score the session with `mock-measurement-p5-score-1.0.0`.
11. Score the same session with `mock-measurement-p5-score-2.0.0`.
12. Prove both score runs use the same evidence fingerprint while producing distinct versioned derived outputs.
13. Re-read all raw responses and prove the serialized evidence is unchanged.
14. Prove an authenticated mobile credential cannot write the science tables directly.
15. Probe UPDATE/DELETE of presentations, responses, and score provenance and require database rejection.

## Exit condition
Phase 5 is complete only when this protocol passes from a clean database migration rebuild in permanent read-only CI and the mobile renderer typechecks/bundles for all Expo targets.
