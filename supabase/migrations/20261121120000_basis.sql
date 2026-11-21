-- AOS · Basis für den Mehrbenutzerbetrieb (Roadmap M1.1 / M1.2)
-- Grundsatz: Jeder Datensatz gehört genau einem Athleten. Teamdaten liegen getrennt.
-- Rechte erzwingt die Datenbank (Row Level Security): Athlet nur eigene Daten, Coach alles lesen und nichts schreiben,
-- Admin zusätzlich Rollen und Teamdaten.

create extension if not exists pgtap with schema extensions;

-- ---------- Tabellen ----------
create table public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  name        text not null default '',
  roles       text[] not null default array['athlete']::text[]
              check (roles <@ array['athlete','coach','admin']::text[]),
  active      boolean not null default true,
  data        jsonb not null default '{}'::jsonb,   -- Profilwerte (ab M2: Position, Orte, Tage, Einschränkungen …)
  planner     jsonb,                                -- persönliche Planerdaten (bisher planner/plan.json)
  nutrition   jsonb,                                -- persönliche Ernährungsregeln (bisher planner/nutrition.json)
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create table public.team_season (
  id          int primary key default 1 check (id = 1),   -- genau eine Zeile: das Team
  data        jsonb not null default '{}'::jsonb,          -- Saisonstart, Phasenkalender, Feldtraining, Spiele
  updated_at  timestamptz not null default now()
);

create table public.ref_docs (
  name        text primary key,                            -- z. B. 'uebungen', 'lebensmittel', 'rezepte'
  data        jsonb not null,
  updated_at  timestamptz not null default now()
);

-- Alle Datenbereiche aus aos-data.json, ein Datensatz je Schlüssel der App ('sessions:<id>', 'profile:_', …)
create table public.records (
  athlete_id  uuid not null references public.profiles(id) on delete cascade,
  key         text not null check (length(key) between 3 and 300),
  data        jsonb,
  updated_at  timestamptz not null,                        -- Änderungszeit laut Gerät (jüngste gewinnt)
  deleted     boolean not null default false,              -- Löschmarke, damit Löschungen übertragen werden
  server_at   timestamptz not null default now(),          -- Eingang beim Server (für den Abgleich ab einem Zeitpunkt)
  primary key (athlete_id, key)
);
create index records_server_at on public.records (athlete_id, server_at);

-- ---------- Rollen-Hilfsfunktionen ----------
create or replace function public.has_role(r text) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles p where p.id = auth.uid() and p.active and r = any(p.roles));
$$;
create or replace function public.is_admin() returns boolean language sql stable as $$ select public.has_role('admin'); $$;
create or replace function public.is_staff() returns boolean language sql stable as $$ select public.has_role('coach') or public.has_role('admin'); $$;
create or replace function public.is_active() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles p where p.id = auth.uid() and p.active);
$$;

-- ---------- Trigger ----------
-- Neues Konto (nur per Einladung möglich) → Profil als Athlet
create or replace function public.on_auth_user_created() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, name) values (new.id, coalesce(new.raw_user_meta_data->>'name', ''))
  on conflict (id) do nothing;
  return new;
end $$;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.on_auth_user_created();

-- Rollen und Sperre ändert nur der Admin; Zeitstempel pflegen
create or replace function public.profiles_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (new.roles is distinct from old.roles or new.active is distinct from old.active or new.id is distinct from old.id)
     and coalesce(auth.role(), '') = 'authenticated' and not public.is_admin() then
    raise exception 'Nur der Admin darf Rollen ändern' using errcode = '42501';
  end if;
  new.updated_at := now();
  return new;
end $$;
create trigger profiles_guard before update on public.profiles
  for each row execute function public.profiles_guard();

-- Jüngste Änderung gewinnt: ein älterer Stand eines anderen Geräts überschreibt keinen neueren
create or replace function public.records_newest_wins() returns trigger
language plpgsql as $$
begin
  if new.updated_at < old.updated_at then
    return null;   -- Update verwerfen, bestehender (neuerer) Datensatz bleibt
  end if;
  new.server_at := now();
  return new;
end $$;
create trigger records_newest_wins before update on public.records
  for each row execute function public.records_newest_wins();

create or replace function public.touch_updated_at() returns trigger language plpgsql as $$
begin new.updated_at := now(); return new; end $$;
create trigger team_season_touch before update on public.team_season for each row execute function public.touch_updated_at();
create trigger ref_docs_touch before update on public.ref_docs for each row execute function public.touch_updated_at();

-- ---------- Zugriffsregeln ----------
alter table public.profiles    enable row level security;
alter table public.team_season enable row level security;
alter table public.ref_docs    enable row level security;
alter table public.records     enable row level security;

-- Profile: selbst lesen/ändern; Coach und Admin lesen alle; Admin ändert alle (Rollen, Sperre)
create policy profiles_read   on public.profiles for select to authenticated using (id = auth.uid() or public.is_staff());
create policy profiles_update on public.profiles for update to authenticated
  using ((id = auth.uid() and public.is_active()) or public.is_admin())
  with check ((id = auth.uid() and public.is_active()) or public.is_admin());

-- Teamdaten und Referenzdaten: alle Angemeldeten lesen, nur Admin schreibt
create policy team_read   on public.team_season for select to authenticated using (public.is_active());
create policy team_write  on public.team_season for all    to authenticated using (public.is_admin()) with check (public.is_admin());
create policy ref_read    on public.ref_docs    for select to authenticated using (public.is_active());
create policy ref_write   on public.ref_docs    for all    to authenticated using (public.is_admin()) with check (public.is_admin());

-- Datensätze: Athlet nur eigene (lesen und schreiben); Coach und Admin lesen alle, schreiben nie fremde
create policy records_read   on public.records for select to authenticated using (athlete_id = auth.uid() or public.is_staff());
create policy records_insert on public.records for insert to authenticated with check (athlete_id = auth.uid() and public.is_active());
create policy records_update on public.records for update to authenticated
  using (athlete_id = auth.uid() and public.is_active()) with check (athlete_id = auth.uid());
-- Löschen läuft über Löschmarken (deleted = true), physisches Löschen nur über das Konto (cascade)

grant select, insert, update on public.records to authenticated;
grant select, update on public.profiles to authenticated;
grant select, insert, update on public.team_season to authenticated;
grant select, insert, update on public.ref_docs to authenticated;
revoke all on public.records, public.profiles, public.team_season, public.ref_docs from anon;

-- ---------- Bestehende Konten ----------
-- Beim Einrichten gibt es nur das Konto des Admins (Selbstregistrierung ist aus): Profil + Admin-Rolle
insert into public.profiles (id, name, roles)
  select u.id, '', array['athlete','admin']::text[] from auth.users u
  on conflict (id) do update set roles = array['athlete','admin']::text[];
insert into public.team_season (id) values (1) on conflict do nothing;
