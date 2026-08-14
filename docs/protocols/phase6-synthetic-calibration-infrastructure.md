# Phase 6 Synthetic Calibration Infrastructure Protocol

## Purpose

Validate that Mosaic can present controlled synthetic comparison stimuli through the authenticated mobile/API/database stack while preserving enough immutable metadata to reconstruct exactly what a user saw.

This protocol validates infrastructure only. The deterministic geometric PNG candidates are synthetic test artifacts, not validated attraction stimuli and not real Mosaic members.

## Active mock versions

- instrument: `p6-synthetic-pair-1.0.0`
- stimulus specification: `p6-synthetic-spec-1.0.0`
- pair policy: `mock-synthetic-p6-pair-1.0.0`
- QC: `p6-synthetic-qc-1.0.0`
- generator adapter: `deterministic-png-1.0.0`
- provider: `mosaic-local-mock`
- generator model: `geometric-face-card`, revision `1.0.0`

## Experimental record chain

For each of 20 pair ordinals, the server provisions two synthetic candidates before accepting a response:

```text
versioned control-vector specification
        ↓
deterministic PNG bytes
        ↓
SHA-256 content identity + generation provenance
        ↓
versioned QC acceptance
        ↓
deterministic randomized left/right pair
        ↓
A / B / Both / Neither observation
```

The first session request provisions the complete 20-pair mock cache. Subsequent pair delivery uses persisted cached artifacts. `cache_ready=true` means all 20 pair assignments exist in the server-owned ledger.

## Replay requirements

For every accepted response, PostgreSQL must contain enough information to recover:

1. the exact stimulus specification for both candidates;
2. the specification version and SHA-256 identity;
3. the exact PNG bytes delivered to the client, recovered from the stored asset URI;
4. the PNG SHA-256 content hash;
5. generator adapter/provider/model/revision/seed/prompt/parameters;
6. the active QC decision and QC version;
7. the pair ordinal, left/right asset IDs, randomization seed, and pair-policy version;
8. the user's raw response and ingestion timestamps.

No accepted response may reference a missing specification, asset, or pair.

## Automated integration sequence

The Phase 6 CI protocol executes the following against a clean local Supabase database and real FastAPI process:

```text
unauthenticated P6 request rejected
        ↓
create Supabase-authenticated test user
        ↓
request first synthetic comparison
        ↓
server provisions complete 20-pair cache
        ↓
verify PNG data URI + exact SHA-256 bytes
        ↓
repeat /next and receive same unanswered pair
        ↓
submit response
        ↓
retry exact response and receive idempotent duplicate receipt
        ↓
repeat through pair 10
        ↓
re-authenticate
        ↓
resume same session at pair 11
        ↓
complete pair 20
        ↓
reconstruct 40 specs + 40 assets + 40 QC events + 20 pairs + 20 responses
        ↓
verify stored specification hashes
        ↓
verify stored PNG hashes and PNG signature
        ↓
verify every QC decision accepted
        ↓
verify database pair sequence equals API-presented sequence exactly
        ↓
reject direct authenticated-client science write
        ↓
reject privileged mutation of specs/assets/QC/pairs/responses
```

Phase 4 and Phase 5 integration protocols run before Phase 6 in the permanent P6 workflow so new synthetic-calibration infrastructure cannot regress the existing persisted experiment or measurement boundaries.

## Performance interpretation

The roadmap's `<300 ms` target applies to delivery of an already cached comparison under the internal-alpha network profile. The deterministic Phase 6 mock currently provisions the full cache on the first P6 request; that provisioning request is not treated as a cached-delivery measurement.

A production generator should pre-provision or replenish the cache outside the user's comparison interaction loop. Phase 6 establishes the cache contract; generator scheduling and production latency instrumentation can evolve behind it.

## Scientific non-claims

Passing this protocol establishes that Mosaic can run a replayable synthetic comparison experiment. It does **not** establish:

- that the geometric stimuli resemble real potential partners sufficiently for preference inference;
- that any visual control dimension is psychologically meaningful;
- that A/B/Both/Neither responses identify a stable attraction utility;
- that attraction predicts relationship quality;
- that the eventual adaptive selection algorithm is statistically efficient.

Those are later scientific questions. Phase 6 protects the evidence needed to investigate them without ambiguity.
