# ADR 0003 — FastAPI/OpenAPI is the wire-contract authority

**Status:** Accepted for Phase 3 bootstrap

## Context

Mosaic now has a TypeScript mobile client and is introducing a Python scientific/application engine. Maintaining request/response interfaces independently in both languages would permit semantic drift exactly at the boundary that future scientific inference depends on.

## Decision

- Python Pydantic request/response models in `services/engine` define the server wire schema.
- FastAPI's generated OpenAPI 3 schema is the canonical serialized contract.
- `packages/contracts/openapi.json` is generated from the running application object and committed for reviewability.
- `packages/contracts/src/generated.ts` is generated from that OpenAPI document with `openapi-typescript` and committed.
- TypeScript application code imports API DTO types from `@mosaic/contracts`; it must not independently redefine engine request/response structures.
- CI regenerates the OpenAPI and TypeScript artifacts and fails on any uncommitted diff.
- Operation IDs are explicit and stable.
- Phase 3 calibration and ranking behavior is visibly marked as mock output. Endpoint shape is being established; scientific semantics are not being claimed.

## Consequences

A Pydantic model or route change necessarily changes the reviewable OpenAPI artifact and generated TypeScript interface. The mobile client can evolve against a typed contract without importing Python implementation details. Scientific implementations can later replace deterministic mocks behind the same versioned boundary or intentionally revise the contract with an explicit diff.

Authentication/authorization of engine requests and persistence are deliberately deferred to the Phase 4 vertical slice.
