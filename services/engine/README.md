# Mosaic Engine

Phase 3 establishes the server-authoritative API and contract boundary. The endpoints in this phase are deterministic infrastructure mocks; they are not relationship-science models.

## Toolchain

- Python 3.13
- FastAPI
- Pydantic / Pydantic Settings
- Uvicorn
- uv
- Ruff
- pytest

## Local setup

From the repository root:

```bash
python -m pip install uv==0.12.4
uv sync --project services/engine --all-groups
npm ci
```

Run checks:

```bash
npm run engine:check
```

Run the API:

```bash
npm run engine:serve
```

Regenerate the committed wire contract and TypeScript types:

```bash
npm run contracts:sync
```

Do not hand-edit `packages/contracts/openapi.json` or `packages/contracts/src/generated.ts`.
