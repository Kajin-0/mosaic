create type public.profile_lifecycle_state as enum (
  'onboarding',
  'active',
  'paused',
  'deleted'
);

create table public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  lifecycle_state public.profile_lifecycle_state not null default 'onboarding',
  profile_version bigint not null default 1 check (profile_version >= 1),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table public.profiles is 'Private application profile state keyed one-to-one to auth.users.';
comment on column public.profiles.profile_version is 'Monotonic row revision used for audit/concurrency boundaries.';

create or replace function public.bump_profile_revision()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  new.profile_version = old.profile_version + 1;
  return new;
end;
$$;

create trigger profiles_bump_revision
before update on public.profiles
for each row
execute function public.bump_profile_revision();

alter table public.profiles enable row level security;
alter table public.profiles force row level security;

revoke all on table public.profiles from anon, authenticated;
grant select on table public.profiles to authenticated;
grant insert (user_id, lifecycle_state) on table public.profiles to authenticated;
grant update (lifecycle_state) on table public.profiles to authenticated;

revoke all on function public.bump_profile_revision() from public;

create policy "profiles_select_own"
on public.profiles
for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "profiles_insert_own"
on public.profiles
for insert
to authenticated
with check ((select auth.uid()) = user_id);

create policy "profiles_update_own"
on public.profiles
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);
