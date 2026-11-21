-- Server-Zugang (Secret key) für Übernahme, Backup und Erinnerungen aus dem privaten Datenrepo.
-- Neue Supabase-Projekte geben neuen Tabellen keine Rechte mehr automatisch.
grant usage on schema public to service_role;
grant all on public.profiles, public.team_season, public.ref_docs, public.records to service_role;
