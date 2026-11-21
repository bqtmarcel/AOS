# Hinweise für Claude

- Dieses Repo ist **öffentlich** (GitHub Pages). Niemals persönliche Daten des Athleten hier ablegen: keine Körperwerte, Tests, Lasten, Startwerte, Trainingspläne, Ernährungs- oder Gesundheitsangaben, keine Spezifikationen mit solchen Werten. All das liegt in Supabase (Daten der Athleten) bzw. im privaten Repo `bqtmarcel/AOS_DATA` (Planer- und Datenbankdateien, Spezifikationen, Backup).
- `seedData()` in `index.html` bleibt neutral. Persönliche Daten liegen seit 21.11.2026 in Supabase (`records` je Athlet); `AOS_DATA/aos-data.json` ist nur noch Archiv.
- **Supabase:** Struktur und Zugriffsregeln nur über neue Dateien in `supabase/migrations/` (nie bestehende ändern), Tests in `supabase/tests/`; die Action „Datenbank“ spielt beides ein und prüft. Öffentliche Verbindungsdaten in `supabase/projekt.json`; geheime Schlüssel nur in GitHub-Secrets.
- Änderungen an `AOS_DATA/planner/` oder `AOS_DATA/db/` überträgt die Action „Supabase“ im Datenrepo automatisch (Modus `plan`).
- Datenformat der App: siehe `validateData`, `migrate`, `syncRecords` und `mergeData` in `index.html`. Schemaänderungen brauchen eine Migration in `migrate()`, damit bestehende Daten auf iPhone und Laptop erhalten bleiben.
- Nach jeder Änderung an `index.html` die Cache-Version in `sw.js` erhöhen: `./tools/bump-cache.sh` (die GitHub Action prüft das).
- Vor dem Hochladen den Klicktest laufen lassen: `python tests/smoke.py` (läuft auch automatisch als GitHub Action bei jedem Push).
- **Roadmap:** `ROADMAP.md` führt die Tasks für Mehrbenutzer, Positionsgruppen, Coach und Ranglisten. Jeden Task nach erfolgreichem Abschluss (umgesetzt und geprüft) im selben Commit abhaken: `[x]` und `✅ TT.MM.JJJJ` ans Ende, Zähler „Stand“ im Überblick aktualisieren. Neue oder geänderte Tasks dort eintragen. Keine persönlichen Werte in die Roadmap.
- Spezifikationen und Datenbanken (Sessionplaner, Nutrition, Übungen, Lebensmittel, Rezepte) liegen in `AOS_DATA/docs` und `AOS_DATA/db`.
- **Rollen:** Spieler, Coach, Admin in `profiles.roles`; Rechte erzwingt die Datenbank. Fremde Daten (Coach-Übersicht) nur anzeigen, nie in `S` übernehmen. Einladungen laufen über die Edge Function `supabase/functions/admin` (geheimer Schlüssel nur dort, gesetzt von der Action „Datenbank“).
- Gruppenregeln (`TP` in `index.html`) nicht von Hand ändern: `python3 tools/tp-gen.py ../AOS_DATA/docs/AOS_Trainingspfade.json`. Testprofile je Gruppe: `python tests/gruppen.py <Übungsdatenbank>` (Action „Gruppentest“ im Datenrepo).
