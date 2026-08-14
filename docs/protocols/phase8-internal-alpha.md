# Phase 8 protocol — Infrastructure-complete internal alpha

## Purpose

Phase 8 proves that the preliminary Mosaic platform behaves as one coherent, resumable application rather than a set of independently validated vertical slices.

It does **not** introduce or validate the real Mosaic matchmaking algorithm.

## Required journey

A clean local stack must support one user through:

```text
create account
      ↓
create profile in onboarding state
      ↓
complete the versioned 20-item measurement fixture
      ↓
prove all five hard-constraint fixture items were traversed
      ↓
activate profile
      ↓
complete the 20-pair synthetic-calibration fixture
      ↓
request a five-candidate deterministic mock ranking
      ↓
persist immutable model/version/request/output provenance
      ↓
simulate application closure with a fresh authenticated session
      ↓
recover active profile
      ↓
recover the same completed measurement session
      ↓
recover the same completed synthetic-calibration session
      ↓
recover the same persisted ranking run and output
```

## Ranking fixture

The internal-alpha ranking cohort contains five fixed non-member UUIDs. They are identifiers for infrastructure fixtures only.

The ranking endpoint is authenticated and persists an append-only `match_rank_runs` row containing:

- pseudonymous science subject;
- ranker model version;
- normalized candidate IDs;
- requested limit;
- canonical SHA-256 request fingerprint;
- exact ranked output; and
- creation timestamp.

Reversing the same candidate-ID input order must resolve to the same run ID, fingerprint, and ranked output.

## Replay implementation

The executable protocol is:

```text
npm run phase8:test
```

implemented by `scripts/test-phase8-internal-alpha.mjs`.

The test must prove all of the following:

1. an unauthenticated ranking request is rejected;
2. a fresh account and onboarding profile can be created;
3. all 20 measurement items can be completed;
4. exactly five hard-constraint fixture items occur in that measurement journey;
5. profile lifecycle can advance to `active`;
6. all 20 synthetic pairs can be completed;
7. the synthetic session reports complete;
8. a five-candidate ranking is persisted with run ID, model version, and 64-character request fingerprint;
9. reordering the same candidate set returns the same persisted run;
10. a fresh password sign-in can be obtained after the original authenticated session is discarded;
11. the same profile remains active;
12. the same measurement session remains complete with 20 responses;
13. the same synthetic session remains complete with 20 responses;
14. the same ranking run, fingerprint, and ranked output are returned;
15. the stored ranking row is independently reconstructable through the privileged data boundary;
16. an authenticated client cannot write a ranking row directly; and
17. even a privileged caller cannot mutate the append-only ranking history.

## Operational envelope

The permanent repository-wide read-only workflow runs the Phase 8 replay after P4, P5, P6, and P6 provenance validation. It then runs:

1. the 100-request internal-alpha latency regression protocol;
2. destructive detached science-state recovery;
3. post-restore authentication/RLS validation; and
4. generated-contract/dependency zero-drift checks.

This ordering is deliberate. The recovery gate cannot pass unless the Phase 8 ranking rows created earlier in the same workflow are included in the detached state and survive the destructive rebuild/restore cycle.

## First complete green replay

On GitHub Actions run `31836243873`, the Phase 8 journey completed successfully on the real FastAPI + local Supabase/PostgreSQL stack after P4–P6 also passed.

The same run measured the authenticated persisted ranking path at:

```text
ranking p50    97.640 ms
ranking p95   114.124 ms
ranking max   114.623 ms
```

Across all 100 latency samples, overall p95 was `160.251 ms`, below the `500 ms` local internal-alpha regression target.

The destructive recovery pass reconstructed two ranking runs along with the P4–P6 state and reproduced the complete snapshot exactly. That run used the pre-final recovery-format label; the final Phase 8 release head must rerun after the `mosaic-science-state-backup-v2` format change and establish the release fingerprint recorded in the roadmap/PR.

## Scientific non-claims

Phase 8 establishes infrastructure integration and reproducibility only.

It does not establish:

- the validity of the mock questionnaire;
- attraction inference from synthetic stimuli;
- compatibility prediction;
- reciprocal selection probability;
- relationship-formation probability;
- long-term relationship quality prediction;
- optimal active-query design; or
- production scalability.

The deterministic candidate IDs, questionnaire answers, synthetic PNG fixtures, and ranking scores are test inputs. They must not be interpreted as evidence that Mosaic's eventual scientific model is valid.
