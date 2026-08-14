create or replace function public.protect_synthetic_session_provenance()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if tg_op = 'DELETE' then
    raise exception 'synthetic calibration session is not deletable';
  end if;

  if old.status = 'complete' then
    raise exception 'completed synthetic calibration session is immutable';
  end if;

  if new.id is distinct from old.id
    or new.subject_id is distinct from old.subject_id
    or new.instrument_key is distinct from old.instrument_key
    or new.instrument_version is distinct from old.instrument_version
    or new.pair_policy_version is distinct from old.pair_policy_version
    or new.generator_adapter_version is distinct from old.generator_adapter_version
    or new.target_trial_count is distinct from old.target_trial_count
    or new.created_at is distinct from old.created_at
  then
    raise exception 'synthetic calibration session provenance is immutable';
  end if;

  if new.status <> 'complete' or new.completed_at is null then
    raise exception 'synthetic calibration session may only transition active to complete';
  end if;

  return new;
end;
$$;

create trigger synthetic_calibration_session_provenance_is_immutable
before update or delete on public.synthetic_calibration_sessions
for each row
execute function public.protect_synthetic_session_provenance();

revoke all on function public.protect_synthetic_session_provenance() from public;
