-- Deterministic development fixture. This Auth row has no password and cannot be used to sign in.
insert into auth.users (id, email, raw_user_meta_data)
values (
  '00000000-0000-4000-8000-000000000001',
  'seed-profile@mosaic.invalid',
  '{}'::jsonb
)
on conflict (id) do nothing;

insert into public.profiles (user_id, lifecycle_state)
values ('00000000-0000-4000-8000-000000000001', 'onboarding')
on conflict (user_id) do nothing;
