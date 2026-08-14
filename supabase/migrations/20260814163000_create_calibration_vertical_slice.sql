create type public.calibration_session_status as enum (
  'active',
  'complete'
);

create type public.calibration_response_choice as enum (
  'left',
  'right',
  'both',
  'neither'
);

create table public.science_subjects (
  subject_id uuid primary key default gen_random_uuid(),
  user_id uuid unique references auth.users(id) on delete set null,
  created_at timestamptz not null default now()
);

comment on table public.science_subjects is
  'Server-only mapping from authentication identity to a pseudonymous science subject identifier.';
comment on column public.science_subjects.user_id is
  'Nullable account linkage. Authentication deletion can detach identity without deleting pseudonymous experimental evidence.';

create table public.calibration_sessions (
  id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references public.science_subjects(subject_id) on delete restrict,
  instrument_key text not null,
  instrument_version text not null,
  policy_version text not null,
  target_trial_count integer not null check (target_trial_count between 1 and 1000),
  status public.calibration_session_status not null default 'active',
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  unique (id, subject_id),
  unique (subject_id, instrument_key, instrument_version, policy_version),
  check (
    (status = 'active' and completed_at is null)
    or (status = 'complete' and completed_at is not null)
  )
);

create table public.calibration_trials (
  id uuid primary key,
  session_id uuid not null,
  subject_id uuid not null,
  ordinal integer not null check (ordinal >= 1),
  stimulus_id text not null,
  stimulus_version text not null,
  policy_version text not null,
  stimulus jsonb not null,
  response_options jsonb not null,
  created_at timestamptz not null default now(),
  unique (id, session_id, subject_id),
  unique (session_id, ordinal),
  foreign key (session_id, subject_id)
    references public.calibration_sessions(id, subject_id)
    on delete restrict
);

create table public.calibration_responses (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null,
  experiment_id uuid not null unique,
  subject_id uuid not null,
  client_response_id uuid not null unique,
  response public.calibration_response_choice not null,
  client_timestamp timestamptz,
  server_timestamp timestamptz not null default now(),
  policy_version text not null,
  foreign key (experiment_id, session_id, subject_id)
    references public.calibration_trials(id, session_id, subject_id)
    on delete restrict
);

comment on table public.calibration_trials is
  'Immutable server-authored experimental presentations. Stimulus JSON preserves the exact presented artifact for replay.';
comment on table public.calibration_responses is
  'Immutable raw calibration evidence. One response per experiment and one record per client idempotency key.';

create or replace function public.reject_calibration_evidence_mutation()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  raise exception 'calibration evidence is immutable';
end;
$$;

create trigger calibration_trials_are_immutable
before update or delete on public.calibration_trials
for each row
execute function public.reject_calibration_evidence_mutation();

create trigger calibration_responses_are_immutable
before update or delete on public.calibration_responses
for each row
execute function public.reject_calibration_evidence_mutation();

alter table public.science_subjects enable row level security;
alter table public.science_subjects force row level security;
alter table public.calibration_sessions enable row level security;
alter table public.calibration_sessions force row level security;
alter table public.calibration_trials enable row level security;
alter table public.calibration_trials force row level security;
alter table public.calibration_responses enable row level security;
alter table public.calibration_responses force row level security;

revoke all on table public.science_subjects from anon, authenticated;
revoke all on table public.calibration_sessions from anon, authenticated;
revoke all on table public.calibration_trials from anon, authenticated;
revoke all on table public.calibration_responses from anon, authenticated;

revoke all on table public.science_subjects from service_role;
revoke all on table public.calibration_sessions from service_role;
revoke all on table public.calibration_trials from service_role;
revoke all on table public.calibration_responses from service_role;

grant select, insert on table public.science_subjects to service_role;
grant select, insert, update on table public.calibration_sessions to service_role;
grant select, insert, update, delete on table public.calibration_trials to service_role;
grant select, insert, update, delete on table public.calibration_responses to service_role;

revoke all on function public.reject_calibration_evidence_mutation() from public;
