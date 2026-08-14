create table public.match_rank_runs (
  id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references public.science_subjects(subject_id) on delete restrict,
  model_version text not null,
  request_fingerprint text not null check (length(request_fingerprint) = 64),
  candidate_ids uuid[] not null check (cardinality(candidate_ids) between 1 and 50),
  requested_limit integer not null check (requested_limit between 1 and 50),
  ranked_candidates jsonb not null check (jsonb_typeof(ranked_candidates) = 'array'),
  created_at timestamptz not null default now(),
  unique (subject_id, model_version, request_fingerprint)
);

comment on table public.match_rank_runs is
  'Append-only versioned match-ranking outputs. Phase 8 rows are deterministic infrastructure fixtures, not validated matchmaking predictions.';

create or replace function public.reject_match_rank_run_mutation()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  raise exception 'match ranking run is immutable';
end;
$$;

create trigger match_rank_runs_are_immutable
before update or delete on public.match_rank_runs
for each row
execute function public.reject_match_rank_run_mutation();

alter table public.match_rank_runs enable row level security;
alter table public.match_rank_runs force row level security;

revoke all on table public.match_rank_runs from anon, authenticated;
revoke all on table public.match_rank_runs from service_role;
grant select, insert, update, delete on table public.match_rank_runs to service_role;

revoke all on function public.reject_match_rank_run_mutation() from public;
