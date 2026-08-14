create type public.synthetic_calibration_session_status as enum (
  'active',
  'complete'
);

create type public.synthetic_qc_decision as enum (
  'accepted',
  'rejected'
);

create table public.synthetic_calibration_sessions (
  id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references public.science_subjects(subject_id) on delete restrict,
  instrument_key text not null,
  instrument_version text not null,
  pair_policy_version text not null,
  generator_adapter_version text not null,
  target_trial_count integer not null check (target_trial_count between 1 and 1000),
  status public.synthetic_calibration_session_status not null default 'active',
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  unique (id, subject_id),
  unique (
    subject_id,
    instrument_key,
    instrument_version,
    pair_policy_version,
    generator_adapter_version
  ),
  check (
    (status = 'active' and completed_at is null)
    or (status = 'complete' and completed_at is not null)
  )
);

create table public.synthetic_stimulus_specs (
  id uuid primary key,
  session_id uuid not null,
  subject_id uuid not null,
  stimulus_key text not null,
  spec_version text not null,
  specification_sha256 text not null check (length(specification_sha256) = 64),
  specification jsonb not null check (jsonb_typeof(specification) = 'object'),
  created_at timestamptz not null default now(),
  unique (id, session_id, subject_id),
  unique (session_id, stimulus_key),
  foreign key (session_id, subject_id)
    references public.synthetic_calibration_sessions(id, subject_id)
    on delete restrict
);

create table public.synthetic_assets (
  id uuid primary key,
  spec_id uuid not null,
  session_id uuid not null,
  subject_id uuid not null,
  media_type text not null,
  content_sha256 text not null check (length(content_sha256) = 64),
  asset_uri text not null,
  generation_provenance jsonb not null check (jsonb_typeof(generation_provenance) = 'object'),
  created_at timestamptz not null default now(),
  unique (id, session_id, subject_id),
  unique (spec_id),
  foreign key (spec_id, session_id, subject_id)
    references public.synthetic_stimulus_specs(id, session_id, subject_id)
    on delete restrict
);

create table public.synthetic_qc_events (
  id uuid primary key,
  asset_id uuid not null,
  session_id uuid not null,
  subject_id uuid not null,
  qc_version text not null,
  decision public.synthetic_qc_decision not null,
  reasons jsonb not null default '[]'::jsonb check (jsonb_typeof(reasons) = 'array'),
  created_at timestamptz not null default now(),
  unique (asset_id, qc_version),
  foreign key (asset_id, session_id, subject_id)
    references public.synthetic_assets(id, session_id, subject_id)
    on delete restrict
);

create table public.synthetic_pairs (
  id uuid primary key,
  session_id uuid not null,
  subject_id uuid not null,
  ordinal integer not null check (ordinal >= 1),
  left_asset_id uuid not null,
  right_asset_id uuid not null,
  randomization_seed bigint not null check (randomization_seed >= 0),
  pair_policy_version text not null,
  created_at timestamptz not null default now(),
  unique (id, session_id, subject_id),
  unique (session_id, ordinal),
  check (left_asset_id <> right_asset_id),
  foreign key (left_asset_id, session_id, subject_id)
    references public.synthetic_assets(id, session_id, subject_id)
    on delete restrict,
  foreign key (right_asset_id, session_id, subject_id)
    references public.synthetic_assets(id, session_id, subject_id)
    on delete restrict
);

create table public.synthetic_calibration_responses (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null,
  pair_id uuid not null unique,
  subject_id uuid not null,
  client_response_id uuid not null unique,
  response text not null check (response in ('left', 'right', 'both', 'neither')),
  client_timestamp timestamptz,
  server_timestamp timestamptz not null default now(),
  pair_policy_version text not null,
  foreign key (pair_id, session_id, subject_id)
    references public.synthetic_pairs(id, session_id, subject_id)
    on delete restrict
);

comment on table public.synthetic_stimulus_specs is
  'Immutable synthetic-stimulus specifications. Exact controllable inputs and content identity are retained for replay.';
comment on table public.synthetic_assets is
  'Immutable generated experimental artifacts with content hash, asset location, and provider-neutral generation provenance.';
comment on table public.synthetic_qc_events is
  'Append-only QC adjudications. New QC versions append events rather than rewriting generated artifacts.';
comment on table public.synthetic_pairs is
  'Immutable randomized pair assignments referencing accepted generated assets.';
comment on table public.synthetic_calibration_responses is
  'Immutable user observations over persisted synthetic pairs.';

create or replace function public.reject_synthetic_artifact_mutation()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  raise exception 'synthetic calibration artifact is immutable';
end;
$$;

create trigger synthetic_stimulus_specs_are_immutable
before update or delete on public.synthetic_stimulus_specs
for each row
execute function public.reject_synthetic_artifact_mutation();

create trigger synthetic_assets_are_immutable
before update or delete on public.synthetic_assets
for each row
execute function public.reject_synthetic_artifact_mutation();

create trigger synthetic_qc_events_are_immutable
before update or delete on public.synthetic_qc_events
for each row
execute function public.reject_synthetic_artifact_mutation();

create trigger synthetic_pairs_are_immutable
before update or delete on public.synthetic_pairs
for each row
execute function public.reject_synthetic_artifact_mutation();

create trigger synthetic_calibration_responses_are_immutable
before update or delete on public.synthetic_calibration_responses
for each row
execute function public.reject_synthetic_artifact_mutation();

alter table public.synthetic_calibration_sessions enable row level security;
alter table public.synthetic_calibration_sessions force row level security;
alter table public.synthetic_stimulus_specs enable row level security;
alter table public.synthetic_stimulus_specs force row level security;
alter table public.synthetic_assets enable row level security;
alter table public.synthetic_assets force row level security;
alter table public.synthetic_qc_events enable row level security;
alter table public.synthetic_qc_events force row level security;
alter table public.synthetic_pairs enable row level security;
alter table public.synthetic_pairs force row level security;
alter table public.synthetic_calibration_responses enable row level security;
alter table public.synthetic_calibration_responses force row level security;

revoke all on table public.synthetic_calibration_sessions from anon, authenticated;
revoke all on table public.synthetic_stimulus_specs from anon, authenticated;
revoke all on table public.synthetic_assets from anon, authenticated;
revoke all on table public.synthetic_qc_events from anon, authenticated;
revoke all on table public.synthetic_pairs from anon, authenticated;
revoke all on table public.synthetic_calibration_responses from anon, authenticated;

revoke all on table public.synthetic_calibration_sessions from service_role;
revoke all on table public.synthetic_stimulus_specs from service_role;
revoke all on table public.synthetic_assets from service_role;
revoke all on table public.synthetic_qc_events from service_role;
revoke all on table public.synthetic_pairs from service_role;
revoke all on table public.synthetic_calibration_responses from service_role;

grant select, insert, update on table public.synthetic_calibration_sessions to service_role;
grant select, insert, update, delete on table public.synthetic_stimulus_specs to service_role;
grant select, insert, update, delete on table public.synthetic_assets to service_role;
grant select, insert, update, delete on table public.synthetic_qc_events to service_role;
grant select, insert, update, delete on table public.synthetic_pairs to service_role;
grant select, insert, update, delete on table public.synthetic_calibration_responses to service_role;

revoke all on function public.reject_synthetic_artifact_mutation() from public;
