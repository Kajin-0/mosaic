# ADR 0001 — Preliminary Foundation Stack

- **Status:** Accepted for preliminary infrastructure
- **Date:** 2026-08-14

## Context

Mosaic needs a mobile-first client, relational/policy-aware persistence, and a rapidly evolving scientific inference layer. During early development, API contracts, schema, experiment provenance, and UI will change together frequently.

## Decision

Use an initial monorepo with these major boundaries:

- React Native + Expo + TypeScript mobile client under `apps/mobile`.
- Supabase/PostgreSQL for authentication, relational persistence, row-level policy, and initial storage/realtime capabilities.
- Python + FastAPI engine under `services/engine` for server-authoritative scientific and application logic.
- Version-controlled database migrations under `supabase/`.
- Shared TypeScript-facing data/API contracts under `packages/contracts` where useful.

Use npm workspaces initially for JavaScript/TypeScript workspaces to minimize package-manager-specific complexity during bootstrap.

## Rationale

### Monorepo
The architecture is not yet stable enough to benefit from independent repositories. Atomic changes across the mobile client, schemas, migrations, and contracts are currently more valuable than independent release boundaries.

### Expo / React Native
One TypeScript client can target iOS and Android while retaining access to native functionality when required. Expo has current first-class monorepo support and file-based routing through Expo Router.

### PostgreSQL / Supabase
Mosaic's data is strongly relational and requires strict per-user access policies, immutable experiment references, and migration-controlled schema evolution. Supabase supplies managed/local PostgreSQL plus Auth, Storage, and RLS-compatible client access without making hosted dashboard state the schema source of truth.

### Python / FastAPI
The scientific engine will require numerical/statistical tooling and should remain independent of the mobile runtime. FastAPI provides typed HTTP contracts around Python implementations and can begin with deterministic mocks before sophisticated models exist.

## Consequences

Positive:
- one repository captures the complete early system state;
- API and schema changes can be reviewed atomically;
- scientific code is isolated from UI code;
- local database state can be reconstructed from migrations;
- a future service split remains possible.

Costs:
- monorepo tooling introduces some dependency-management complexity;
- TypeScript and Python require separate toolchains;
- Supabase introduces a platform dependency that must remain behind clear interfaces;
- generator infrastructure will add another service boundary later.

## Revisit triggers

Reconsider this decision only if measured evidence shows one or more of:
- independent teams require independent release cycles;
- service security isolation cannot be achieved cleanly inside the current deployment model;
- Expo/native constraints materially block required UX or capabilities;
- Supabase/PostgreSQL no longer satisfies a demonstrated data/security requirement;
- the science engine requires a deployment topology incompatible with the application API.
