-- AOS · Mehrbenutzer: Admin-Übersicht, Konto löschen, Ranglisten (Roadmap M4.1, M4.4, M6.1–M6.3)

-- ---------- Admin: Konten mit E-Mail und letzter Anmeldung (nur Admin) ----------
create or replace function public.admin_users()
returns table (id uuid, email text, name text, roles text[], active boolean, created_at timestamptz, last_sign_in_at timestamptz, invited_at timestamptz)
language plpgsql stable security definer set search_path = public, auth as $$
begin
  if not public.is_admin() then raise exception 'Nur für den Admin' using errcode = '42501'; end if;
  return query select p.id, u.email::text, p.name, p.roles, p.active, p.created_at, u.last_sign_in_at, u.invited_at
    from public.profiles p join auth.users u on u.id = p.id order by p.created_at;
end $$;
revoke all on function public.admin_users() from public, anon;
grant execute on function public.admin_users() to authenticated;

-- ---------- Konto löschen (M4.4): eigenes Konto samt aller Daten; der letzte Admin kann sich nicht löschen ----------
create or replace function public.delete_me() returns void
language plpgsql security definer set search_path = public, auth as $$
begin
  if auth.uid() is null then raise exception 'Nicht angemeldet' using errcode = '42501'; end if;
  if public.is_admin() and (select count(*) from public.profiles where active and 'admin' = any(roles)) <= 1 then
    raise exception 'Der letzte Admin kann sein Konto nicht löschen' using errcode = '42501';
  end if;
  delete from auth.users where id = auth.uid();   -- Profil, Datensätze und Ranglisten-Einträge folgen über cascade
end $$;
revoke all on function public.delete_me() from public, anon;
grant execute on function public.delete_me() to authenticated;

-- ---------- Ranglisten (M6): nur mit Zustimmung, nie Körpergewicht ----------
-- Jeder Athlet berechnet seine Werte in der App (e1RM aus eigenen Protokollen, DOTS-Score) und legt sie hier ab.
create table public.rankings (
  athlete_id  uuid not null references public.profiles(id) on delete cascade,
  discipline  text not null check (discipline in ('squat','bench','hinge','broad','total')),
  name        text not null default '',
  grp         text not null default '',          -- Positionsgruppe (Hauptgruppe)
  value       numeric not null check (value > 0), -- kg (e1RM) bzw. cm
  score       numeric,                           -- DOTS (nur Kraft)
  updated_at  timestamptz not null default now(),
  primary key (athlete_id, discipline)
);
alter table public.rankings enable row level security;
create policy rankings_read  on public.rankings for select to authenticated using (public.is_active());
create policy rankings_write on public.rankings for insert to authenticated with check (athlete_id = auth.uid() and public.is_active());
create policy rankings_upd   on public.rankings for update to authenticated using (athlete_id = auth.uid()) with check (athlete_id = auth.uid());
create policy rankings_del   on public.rankings for delete to authenticated using (athlete_id = auth.uid());
grant select, insert, update, delete on public.rankings to authenticated;
revoke all on public.rankings from anon;
grant all on public.rankings to service_role;
create trigger rankings_touch before update on public.rankings for each row execute function public.touch_updated_at();
