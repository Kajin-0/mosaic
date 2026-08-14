# ADR 0007 — Operational controls are part of scientific reproducibility

## Status

Accepted for Phase 7.

## Context

By the end of Phase 6, Mosaic could reconstruct raw calibration, measurement, and synthetic-calibration evidence from PostgreSQL. That is necessary but insufficient for a system intended to support scientific inference.

A historically interpretable experiment can still be lost or made ambiguous if:

- CI does not consistently exercise the security and replay boundary;
- an operational log exposes account identity or omits the model/policy version that produced a request;
- an exception bypasses request-completion telemetry;
- API latency silently regresses until the experimental interface changes user behavior;
- credentials enter repository history;
- a database migration destroys evidence without a tested recovery path; or
- a backup exists but has never been restored.

Phase-specific workflows were useful while the architecture was being built vertically. They are not the desired permanent operational model because they duplicate setup, use path filters, and can allow a new class of repository change to miss the strongest gate.

## Decision

### 1. One repository-wide pull-request gate becomes authoritative

After the Phase 7 dependency bootstrap, Mosaic uses one read-only repository-wide quality gate for every pull request. It must cover:

- JavaScript/TypeScript dependency installation from the committed lockfile;
- mobile typecheck, lint, and tests;
- Python dependency installation from the committed lockfile;
- Python lint, static typecheck, and tests;
- OpenAPI regeneration and TypeScript-contract generation;
- generated-contract and dependency zero-drift checks;
- database recreation from migrations and deterministic seed data;
- authentication ownership and RLS tests;
- all-platform Expo export;
- the Phase 4, Phase 5, and Phase 6 live replay protocols;
- synthetic-session provenance immutability;
- secret scanning of repository history;
- the Phase 7 latency regression protocol; and
- the Phase 7 destructive science-evidence recovery drill.

The older phase-specific workflows are retired only after the consolidated gate proves those same invariants on the replacement head.

### 2. Request observability is pseudonymous and versioned

Every Mosaic HTTP completion/failure event carries:

- a bounded request ID;
- method and path;
- HTTP status;
- elapsed milliseconds;
- engine version;
- API version;
- contract version;
- route-relevant policy or model version when applicable; and
- a stable one-way `subject_ref` after a science subject has been resolved.

`subject_ref` is derived from the pseudonymous science UUID and is not the raw UUID itself. Logs do not contain authentication user IDs, bearer tokens, request bodies, synthetic image bytes, email addresses, or raw experimental answers.

A malformed or unbounded client request ID is replaced server-side rather than copied into logs/headers unchanged.

Unexpected exceptions emit the same request envelope plus an exception class before propagation. Expected HTTP failures remain structured completion events with their actual status.

### 3. Latency is treated as an experimental-interface regression

The Phase 7 CI latency gate is deliberately narrow. After warm-up, it measures 20 sequential requests for each of five ordinary local operations:

- health;
- version;
- deterministic mock ranking;
- server-authoritative cached/pending calibration `next`; and
- server-authoritative cached/pending measurement `next`.

The per-operation p95 and aggregate p95 must remain below 500 ms on the GitHub internal-alpha runner.

This is a regression budget for non-generation control-plane behavior. It is **not** a production throughput benchmark, concurrency claim, Internet latency guarantee, or synthetic-image generation target. A later load model must define concurrency, geographic network conditions, database scale, and hosted infrastructure before production capacity claims are made.

### 4. Recovery has two intentionally different layers

#### Hosted platform recovery

The authoritative full-database/account recovery mechanism is the hosted Supabase backup/restore capability appropriate to the deployed plan, supplemented by documented logical exports when required. This layer is responsible for managed schemas and account linkage.

#### Detached science-evidence recovery

Mosaic additionally maintains a provider-independent recovery representation for the pseudonymous experimental graph. The CI recovery snapshot includes:

- science subjects by `subject_id` and creation time, but intentionally excludes `science_subjects.user_id`;
- Phase 4 sessions, presentations/trials, and responses;
- Phase 5 sessions, presentations, responses, and score runs; and
- Phase 6 sessions, stimulus specifications, assets, QC events, pairs, and responses.

The omission of `science_subjects.user_id` is deliberate. Experimental evidence must remain recoverable even when the authentication linkage cannot or should not be restored. Re-linking a recovered subject to an account is a separate privileged identity operation and must never be inferred from experimental data.

The CI drill computes a canonical SHA-256 fingerprint, destroys/rebuilds the local database from migrations, verifies the experimental tables are empty, restores the detached graph in dependency order, and requires the post-restore fingerprint and every table row count to match exactly.

### 5. Migrations are forward-owned after merge

A merged migration is historical evidence about database evolution and is not edited in place.

For deployed environments:

1. take/verify an appropriate backup before a migration that can affect persistent user or science state;
2. prefer additive schema changes;
3. backfill or dual-read/write when a representation must change;
4. cut over only after validation;
5. repair defects with a new forward migration rather than rewriting an already-applied migration; and
6. use platform restore/PITR or a verified logical recovery path when data itself must be rolled back.

A SQL `DOWN` script is not assumed to be safe for immutable evidence. Dropping a new column may be syntactically reversible while the information written into it is not.

### 6. Secret detection is prevention, not remediation

Repository-history scanning is mandatory on pull requests. If a real secret is committed, passing a later scan after deleting the text does not make that credential safe. The credential must be revoked/rotated; history rewriting is an optional cleanup step after rotation, not the security response itself.

## Consequences

- Operational regressions become review-blocking rather than informal observations.
- Logs become more diagnostically useful without introducing raw account identity into science-service telemetry.
- Recovery is demonstrated by restore, not inferred from the existence of a backup command.
- Authentication recovery and scientific-evidence recovery are explicitly decoupled.
- The 500 ms target has a precise, limited interpretation and cannot honestly be cited as production scalability evidence.
- Database changes become more deliberate because immutable evidence cannot rely on casual rollback semantics.
- CI is longer, but there is one authoritative gate instead of overlapping phase workflows once Phase 7 is complete.
