# Mosaic Database Recovery and Migration Runbook

## Scope

Mosaic has two recovery problems that must not be conflated:

1. recovering the hosted database/account platform; and
2. recovering the pseudonymous scientific evidence required to interpret historical experiments.

The second problem is intentionally less dependent on account identity than the first.

## Recovery classes

### Class A — full hosted platform recovery

Use the deployed Supabase project's supported managed backup/restore mechanism for a full service incident. This is the recovery path for managed authentication data, account linkage, public application state, and the rest of the hosted database.

Before relying on a hosted recovery feature in production, record for the deployed plan/environment:

- backup retention;
- whether point-in-time recovery is enabled;
- the most recent successful backup/restore drill;
- the person/process authorized to initiate restore;
- expected recovery-point and recovery-time objectives; and
- post-restore validation steps.

Do not claim an RPO/RTO until it is measured against the actual hosted configuration.

### Class B — detached science-evidence recovery

Mosaic maintains a provider-independent logical representation of the P4–P6 experimental graph. It intentionally excludes `science_subjects.user_id`.

This recovery class protects the interpretability of research evidence even if authentication linkage is unavailable, corrupted, deleted, or intentionally not restored.

A recovered subject remains pseudonymous and detached until a separate privileged identity operation explicitly reconnects it.

## Evidence included in detached recovery

In dependency order:

1. `science_subjects` — `subject_id`, `created_at` only
2. `calibration_sessions`
3. `calibration_trials`
4. `calibration_responses`
5. `measurement_sessions`
6. `measurement_presentations`
7. `measurement_responses`
8. `measurement_score_runs`
9. `synthetic_calibration_sessions`
10. `synthetic_stimulus_specs`
11. `synthetic_assets`
12. `synthetic_qc_events`
13. `synthetic_pairs`
14. `synthetic_calibration_responses`

The logical backup is canonicalized and SHA-256 fingerprinted. A restore is valid only when the reconstructed graph yields the same fingerprint and row counts.

## Incident procedure

### 1. Stabilize

- Stop or restrict writes if continued operation could compound evidence loss.
- Record the incident start time and affected environment.
- Preserve application/database logs required for diagnosis.
- Do not modify historical migration files as an emergency repair mechanism.

### 2. Classify

Determine whether the incident is primarily:

- authentication/account state;
- application profile state;
- science evidence;
- schema/migration state; or
- a combination.

If authentication linkage is damaged but science evidence is intact, avoid destructive recovery of the science tables merely to repair identity state.

### 3. Choose recovery boundary

Use Class A when the full hosted service must be restored.

Use Class B when the priority is exact reconstruction of Mosaic's pseudonymous experimental graph, including migration/recovery validation in a clean database.

For mixed incidents, restore the full platform first when appropriate, then independently verify the science graph against its known evidence fingerprint if available.

### 4. Restore

For detached science recovery:

1. provision/rebuild the target schema from committed migrations;
2. verify target science evidence tables are empty or intentionally isolated;
3. restore rows in dependency order;
4. leave account linkage detached;
5. recompute canonical fingerprint;
6. compare all table counts;
7. rerun authorization/RLS validation; and
8. rerun relevant P4–P6 replay/integrity checks before reopening writes.

### 5. Re-link identity only when justified

A `science_subjects.user_id` association is identity-bearing state. Never infer it from questionnaire answers, image preferences, timestamps, or other experimental evidence.

If relinking is required, use an explicit privileged procedure based on authoritative account records and audit the change separately.

## Migration policy

### Before merge

Every schema change must:

- be represented by a new migration;
- rebuild cleanly from the beginning of repository migrations;
- preserve relevant RLS/grants/triggers;
- pass all P4–P6 replay tests that touch the changed schema; and
- have a recovery/forward-fix strategy when it transforms persistent evidence.

### After merge/deployment

Treat an applied migration as immutable history.

If a defect is discovered:

- write a new forward migration;
- do not rewrite the old migration and pretend the historical deployment never occurred;
- prefer additive correction over destructive replacement; and
- separately decide whether data recovery is required.

### Representation changes

For a nontrivial representation change:

1. add new representation;
2. make application code able to read the transition state;
3. backfill deterministically with provenance/versioning where scientifically meaningful;
4. validate old and new state;
5. cut writes/read preference to the new representation; and
6. remove obsolete state only in a later migration after recovery implications are understood.

### Rollback semantics

Schema syntax and data meaning are different.

A migration may be syntactically reversible while information written under the new schema is not. Therefore Mosaic does not assume every migration has a safe `DOWN` operation. For evidence-bearing state, a verified backup/restore or forward repair is preferred to destructive schema rollback.

## Secret incident procedure

If a real credential appears in Git or CI output:

1. revoke or rotate the credential immediately;
2. determine what it could access and for what time window;
3. inspect relevant access logs where available;
4. replace affected configuration;
5. only then consider history rewriting as cleanup; and
6. add a detection/prevention rule if the existing scanner did not catch it.

Deleting the string from the current branch is not credential remediation.

## Drill record

For each production recovery drill, record:

- environment;
- backup identifier/time;
- restore start/end time;
- measured RPO/RTO;
- evidence fingerprint before/after when applicable;
- row-count reconciliation;
- RLS/security validation result;
- replay validation result; and
- anomalies/follow-up actions.

The Phase 7 CI drill is the minimum automatic proof for Class B recovery. It does not substitute for a hosted Class A restore drill before external production use.
