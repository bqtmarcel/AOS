-- AOS · automatischer Test der Zugriffsregeln (Roadmap M1.2). Läuft in einer Transaktion und wird zurückgerollt.
begin;
select plan(16);

-- Testkonten: zwei Athleten (A, B) und ein Coach (C)
insert into auth.users (id, email, aud, role) values
  ('00000000-0000-4000-a000-00000000000a', 'a@test.invalid', 'authenticated', 'authenticated'),
  ('00000000-0000-4000-a000-00000000000b', 'b@test.invalid', 'authenticated', 'authenticated'),
  ('00000000-0000-4000-a000-00000000000c', 'c@test.invalid', 'authenticated', 'authenticated');
update public.profiles set roles = array['coach'] where id = '00000000-0000-4000-a000-00000000000c';

select is((select count(*)::int from public.profiles where id in ('00000000-0000-4000-a000-00000000000a','00000000-0000-4000-a000-00000000000b','00000000-0000-4000-a000-00000000000c')),
  3, 'Neue Konten bekommen automatisch ein Profil');

-- ---- Athlet A ----
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-4000-a000-00000000000a","role":"authenticated"}', true);
select lives_ok($$ insert into public.records (athlete_id, key, data, updated_at) values ('00000000-0000-4000-a000-00000000000a', 'sessions:t1', '{"v":1}', '2026-11-21T10:00:00Z') $$,
  'Athlet speichert eigene Daten');
select throws_ok($$ insert into public.records (athlete_id, key, data, updated_at) values ('00000000-0000-4000-a000-00000000000b', 'sessions:x', '{}', now()) $$,
  '42501', null, 'Athlet kann keine Daten für andere anlegen');
select throws_ok($$ update public.profiles set roles = array['athlete','admin'] where id = '00000000-0000-4000-a000-00000000000a' $$,
  '42501', null, 'Athlet kann sich keine Rollen geben');
-- Jüngste Änderung gewinnt: älterer Stand überschreibt nicht
update public.records set data = '{"v":0}', updated_at = '2026-11-21T09:00:00Z' where key = 'sessions:t1';
select is((select data->>'v' from public.records where key = 'sessions:t1'), '1', 'Älterer Stand überschreibt keinen neueren');
update public.records set data = '{"v":2}', updated_at = '2026-11-21T11:00:00Z' where key = 'sessions:t1';
select is((select data->>'v' from public.records where key = 'sessions:t1'), '2', 'Neuerer Stand wird übernommen');
select is((select count(*)::int from public.team_season), 1, 'Athlet liest die Teamdaten');
select is((with u as (update public.team_season set data = '{"x":1}' returning 1) select count(*)::int from u), 0, 'Athlet ändert keine Teamdaten');

-- ---- Athlet B ----
reset role; set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-4000-a000-00000000000b","role":"authenticated"}', true);
insert into public.records (athlete_id, key, data, updated_at) values ('00000000-0000-4000-a000-00000000000b', 'sessions:t2', '{}', now());
select is((select count(*)::int from public.records), 1, 'Athlet sieht nur eigene Daten');
select is((select count(*)::int from public.profiles), 1, 'Athlet sieht nur das eigene Profil');
select is((with u as (update public.records set data = '{"fremd":1}' where athlete_id = '00000000-0000-4000-a000-00000000000a' returning 1) select count(*)::int from u), 0,
  'Athlet ändert keine fremden Daten');

-- ---- Coach C ----
reset role; set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-4000-a000-00000000000c","role":"authenticated"}', true);
select is((select count(*)::int from public.records where athlete_id in ('00000000-0000-4000-a000-00000000000a','00000000-0000-4000-a000-00000000000b')), 2,
  'Coach liest die Daten aller Athleten');
select is((with u as (update public.records set data = '{"coach":1}' returning 1) select count(*)::int from u), 0, 'Coach kann nichts ändern');
select throws_ok($$ insert into public.records (athlete_id, key, data, updated_at) values ('00000000-0000-4000-a000-00000000000a', 'sessions:c', '{}', now()) $$,
  '42501', null, 'Coach kann für Athleten nichts anlegen');
select is((with u as (update public.profiles set name = 'x' where id = '00000000-0000-4000-a000-00000000000a' returning 1) select count(*)::int from u), 0,
  'Coach ändert keine Profile anderer');

-- ---- ohne Anmeldung ----
reset role; set local role anon;
select throws_ok($$ select count(*) from public.records $$, '42501', null, 'Ohne Anmeldung kein Zugriff');

reset role;
select * from finish();
rollback;
