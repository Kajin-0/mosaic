# Mosaic API Contracts

This package is generated from the Mosaic Engine OpenAPI document.

Contract flow:

```text
FastAPI Pydantic models
        ↓
app.openapi()
        ↓
openapi.json
        ↓
openapi-typescript
        ↓
src/generated.ts
```

`openapi.json` and `src/generated.ts` are committed artifacts so contract changes are reviewable. They must not be edited by hand. `src/index.ts` provides stable ergonomic type aliases for TypeScript consumers.

Run from the repository root:

```bash
npm run contracts:sync
npm run contracts:check
```

CI regenerates both artifacts and rejects drift.
