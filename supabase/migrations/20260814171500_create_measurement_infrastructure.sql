create type public.measurement_session_status as enum (
  'active',
  'complete'
);

create table public.measurement_sessions (
  id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references public.science_subjects(subject_id) on delete restrict,
  instrument_key text not null,
  instrument_version text not null,
  selection_policy_version text not null,
  target_item_count integer not null check (target_item_count between 1 and 1000),
  status public.measurement_session_status not null default 'active',
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  unique (id, subject_id),
  unique (subject_id, instrument_key, instrument_version, selection_policy_version),
  check (
    (status = 'active' and completed_at is null)
    or (status = 'complete' and completed_at is not null)
  )
);

create table public.measurement_presentations (
  id uuid primary key,
  session_id uuid not null,
  subject_id uuid not null,
  ordinal integer not null check (ordinal >= 1),
  item_id text not null,
  item_version text not null,
  item_kind text not null check (
    item_kind in ('hard_constraint', 'rating', 'scenario', 'forced_choice')
  ),
  selection_policy_version text not null,
  item jsonb not null check (jsonb_typeof(item) = 'object'),
  created_at timestamptz not null default now(),
  unique (id, session_id, subject_id),
  unique (session_id, ordinal),
  unique (session_id, item_id),
  foreign key (session_id, subject_id)
    references public.measurement_sessions(id, subject_id)
    on delete restrict
);

create table public.measurement_responses (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null,
  presentation_id uuid not null unique,
  subject_id uuid not null,
  client_response_id uuid not null unique,
  answer jsonb not null check (jsonb_typeof(answer) = 'object'),
  client_timestamp timestamptz,
  server_timestamp timestamptz not null default now(),
  instrument_version text not null,
  selection_policy_version text not null,
  foreign key (presentation_id, session_id, subject_id)
    references public.measurement_presentations(id, session_id, subject_id)
    on delete restrict
);

create table public.measurement_score_runs (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null,
  subject_id uuid not null,
  scoring_version text not null,
  evidence_fingerprint text not null check (length(evidence_fingerprint) = 64),
  response_count integer not null check (response_count >= 0),
  scores jsonb not null check (jsonb_typeof(scores) = 'object'),
  created_at timestamptz not null default now(),
  unique (session_id, scoring_version, evidence_fingerprint),
  foreign key (session_id, subject_id)
    references public.measurement_sessions(id, subject_id)
    on delete restrict
);

comment on table public.measurement_presentations is
  'Immutable server-authored onboarding/measurement presentations. Exact item payload and version are retained for replay.';
comment on table public.measurement_responses is
  'Immutable raw measurement evidence. Derived scores are never written back into this table.';
comment on table public.measurement_score_runs is
  'Append-only derived scoring outputs keyed by scoring implementation version and immutable evidence fingerprint.';

create or replace function public.reject_measurement_evidence_mutation()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  raise exception 'measurement evidence is immutable';
end;
$$;

create trigger measurement_presentations_are_immutable
before update or delete on public.measurement_presentations
for each row
execute function public.reject_measurement_evidence_mutation();

create trigger measurement_responses_are_immutable
before update or delete on public.measurement_responses
for each row
execute function public.reject_measurement_evidence_mutation();

create trigger measurement_score_runs_are_immutable
before update or delete on public.measurement_score_runs
for each row
execute function public.reject_measurement_evidence_mutation();

alter table public.measurement_sessions enable row level security;
alter table public.measurement_sessions force row level security;
alter table public.measurement_presentations enable row level security;
alter table public.measurement_presentations force row level security;
alter table public.measurement_responses enable row level security;
alter table public.measurement_responses force row level security;
alter table public.measurement_score_runs enable row level security;
alter table public.measurement_score_runs force row level security;

revoke all on table public.measurement_sessions from anon, authenticated;
revoke all on table public.measurement_presentations from anon, authenticated;
revoke all on table public.measurement_responses from anon, authenticated;
revoke all on table public.measurement_score_runs from anon, authenticated;

revoke all on table public.measurement_sessions from service_role;
revoke all on table public.measurement_presentations from service_role;
revoke all on table public.measurement_responses from service_role;
revoke all on table public.measurement_score_runs from service_role;

grant select, insert, update on table public.measurement_sessions to service_role;
grant select, insert, update, delete on table public.measurement_presentations to service_role;
grant select, insert, update, delete on table public.measurement_responses to service_role;
grant select, insert, update, delete on table public.measurement_score_runs to service_role;

revoke all on function public.reject_measurement_evidence_mutation() from public;
