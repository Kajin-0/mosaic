# ADR 0008 — Persisted ranking is versioned derived state

## Status

Accepted for Phase 8.

## Context

Phase 8 must prove a complete internal-alpha user journey can survive application closure and a fresh authenticated session. Before Phase 8, `/v1/matches/rank` was a deterministic but stateless and unauthenticated mock endpoint. A user could receive a ranking, but Mosaic could not later prove which model produced it, which candidate set was evaluated, or whether a reconstructed response was the historical output rather than a newly recomputed one.

This is different from the raw experimental-evidence problem solved in Phases 4–6. A ranking is not a user observation. It is derived model output over an input candidate set. Treating it as raw evidence would collapse an important scientific boundary; leaving it transient would make historical reconstruction impossible.

## Decision

### 1. Ranking runs are append-only derived state

Every persisted ranking run records:

- a server-generated run UUID;
- the pseudonymous `science_subjects.subject_id`;
- the ranker model version;
- the normalized candidate-ID set;
- the requested result limit;
- a canonical SHA-256 request fingerprint;
- the exact ranked candidate output; and
- the database creation timestamp.

`match_rank_runs` rows cannot be updated or deleted. The mobile client has no direct write authority over the table.

### 2. The ranking endpoint is authenticated and server-authoritative

`POST /v1/matches/rank` requires bearer authentication. The engine resolves the account to the existing pseudonymous science subject and performs all ranking persistence through the privileged server boundary.

The mobile application may request a ranking through the generated API contract, but it cannot create, rewrite, or delete ranking history directly.

### 3. Semantically identical requests reuse historical output

For the current deterministic Phase 8 fixture, candidate IDs are sorted before the request fingerprint is computed. The canonical request identity contains:

```text
sorted candidate IDs
requested limit
ranker model version
```

The canonical minified JSON representation is hashed with SHA-256.

For one subject and one ranker model version, the same request fingerprint identifies one immutable run. Reordering the same candidate set therefore does not create a second historical result. If a uniqueness race occurs, the engine rereads the existing row and accepts it only if the complete immutable payload agrees with the locally computed request/output; otherwise it fails closed.

### 4. Model changes create new versioned history

A change in ranking semantics must change the ranker model version. The model version is part of the request fingerprint and persisted row, so a new implementation cannot silently reinterpret or overwrite an older ranking.

The same rule will apply when the deterministic fixture is eventually replaced by real inference: historical output remains attached to the implementation/model identity that produced it.

### 5. Ranking runs participate in detached science-state recovery

Phase 7 originally introduced a detached recovery representation centered on experimental evidence. Phase 8 extends that representation to include versioned derived state needed for historical reconstruction, including `match_rank_runs`.

The representation is therefore versioned as:

```text
mosaic-science-state-backup-v2
```

It continues to omit `science_subjects.user_id`. Recovering scientific state and restoring account identity linkage remain separate privileged operations.

## Consequences

- A user can leave Mosaic, authenticate again, repeat the same internal-alpha ranking request, and recover the exact historical run rather than merely a recomputation.
- Ranking provenance is reconstructable independently of mobile state.
- Raw observations and model outputs remain separate persistence classes.
- Model-version changes become explicit and reviewable.
- Detached recovery now covers the state required to interpret both experimental history and versioned derived outputs.
- The additional persistence adds database and API latency; Phase 8 measures the authenticated persisted path under the existing 500 ms local internal-alpha regression budget.

## Scientific non-claim

The Phase 8 candidate IDs and ranking scores are deterministic infrastructure fixtures. Persistence, reproducibility, authentication, and version provenance do **not** establish attraction inference, compatibility, psychometric validity, matchmaking quality, or long-term relationship prediction.

## Rejected alternatives

### Keep `/v1/matches/rank` stateless

Rejected because application closure would erase the only record of which model/input/output combination the user actually received.

### Persist ranking state in the mobile client

Rejected because scientific/model provenance must remain server-authoritative and reconstructable independently of a device.

### Maintain one mutable “latest ranking” row per user

Rejected because overwriting previous outputs would destroy historical model provenance and make later model-version comparison impossible.
