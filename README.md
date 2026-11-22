# AOS – Athlete Operating System

Trainings- und Ernährungssystem für die Spieler der Red Tigers als Web-App (PWA): eine footballspezifische S&C-Coaching-Engine, die für jeden Athleten vollautomatisch plant – Übungen, Varianten, Sätze, Wiederholungen, Lasten und Phasen – passend zu Position, Ausstattung, Trainingsstand und eigenen Protokollen. Regelbasiert, ohne Sprachmodell.
Läuft auf dem iPhone (Safari „Zum Home-Bildschirm“) und im Browser am Laptop, auch offline.

## Aufbau

| Ort | Sichtbarkeit | Inhalt |
|---|---|---|
| `bqtmarcel/AOS` (dieses Repo) | öffentlich, GitHub Pages | App-Code `index.html`, Service Worker, Manifest, Icons, Supabase-Struktur (`supabase/`), Tests, Werkzeuge, Roadmap |
| Supabase (Projekt in Frankfurt) | privat, Login per Einladung | Daten aller Athleten (`records`), Profile und Rollen (`profiles`), Teamdaten (`team_season`), Ranglisten |
| `bqtmarcel/AOS_DATA` | **privat** | Planerregeln (`planner/`), Übungs-, Lebensmittel- und Rezeptdatenbank (`db/`), Spezifikationen (`docs/`), Push-Versand, wöchentliches Backup der Datenbank, Archiv des alten Datenstands |

**In diesem Repo stehen keine persönlichen Daten** (keine Körperwerte, Tests, Lasten, Pläne, Ernährungsangaben). Die App startet mit einem neutralen Stand; alles Persönliche kommt nach dem Login aus Supabase.

## Rollen

| Rolle | Darf |
|---|---|
| Spieler (`athlete`) | eigene Einheiten, Protokolle, Readiness, Körper- und Ernährungsdaten, eigenes Profil |
| Coach (`coach`) | Daten aller Athleten **nur lesen** (Ansicht Team → Athleten); greift nicht in die Planung ein |
| Admin (`admin`) | Spieler einladen, Rollen vergeben, Konten sperren, Teamkalender pflegen |

Die Rechte erzwingt die Datenbank (Row Level Security, `supabase/migrations/`), geprüft durch `supabase/tests/`. Eine Person kann mehrere Rollen haben.

## Login und erste Schritte

- Kein Selbst-Registrieren: Der Admin lädt per E-Mail ein (Team → Verwaltung; Edge Function `supabase/functions/admin`).
- Anmelden mit der E-Mail-Adresse: AOS schickt einen Code bzw. Link. Am iPhone öffnet sich der Link in Safari; dort zeigt AOS einen Übergabecode für die App vom Home-Bildschirm.
- Eigener E-Mail-Versand (nötig, damit Mails an alle Spieler gehen): [`docs/EMAIL_VERSAND.md`](docs/EMAIL_VERSAND.md).
- **Onboarding** beim ersten Login (ca. 5 Minuten): Position, Körperdaten, Erfahrung, Trainingsstand, Ort und Ausstattung, Trainingstage und Zeit, Einschränkungen. AOS bestimmt daraus die **Einstiegsstufe** (direkt in die Teamphase, 1 Woche Einstieg oder 2 Wochen Eingewöhnung) und plant sofort.

## Speicherung und Abgleich

- Jede Änderung wird sofort auf dem Gerät gespeichert (localStorage) und nach wenigen Sekunden mit Supabase abgeglichen (Tabelle `records`, ein Datensatz je Eintrag und Athlet).
- Abgleich auch beim Start, beim Zurückkehren in die App und sobald wieder Netz da ist. Ohne Netz (z. B. im Gym) wird auf dem Gerät gepuffert.
- Zusammenführen pro Datensatz: Die jüngste Änderung gewinnt, Löschungen werden übertragen.
- Profil → AOS-Konto: eigene Daten herunterladen, Konto samt Daten löschen.
- Backup: Die Action „Supabase“ im Datenrepo exportiert jeden Sonntag alle Tabellen nach `AOS_DATA/backup/supabase.json`.
- Seit 21.11.2026 gibt es keine Speicherung über GitHub-Token mehr; `AOS_DATA/aos-data.json` ist nur noch Archiv.

## Planung

- Sessionplaner und Football-Progressionsmodell: Phasen P1–P5 und Saison, Wochenwellen, Hauptübungen über geschätztes 1RM, Autoregulation, automatische Entlastung, Tests (Spezifikation in `AOS_DATA/docs`).
- Positionsgruppen OL, DL, LB, TE, RB, WR, DB, QB mit Haupt- und Nebenposition: Regeln `TP` in `index.html`, erzeugt aus `AOS_DATA/docs/AOS_Trainingspfade.json` mit `tools/tp-gen.py`.
- Teamdaten (Saisonstart, Phasenkalender, Feldtraining, Spiele) gelten für alle und kommen aus `team_season`; der Countdown zeigt bei allen dasselbe Spiel.
- Einheiten dauern höchstens 70 Minuten; fallen Einheiten weg, verteilt AOS den Wochenumfang neu. AOS lernt je Athlet Dauer und Pausen mit.

## Team

- **Coach-Übersicht** (Team → Athleten): Liste mit Phase, Einheiten, Readiness-Trend, Gewicht und Hinweisen; Detailansicht je Athlet, nur lesen.
- **Ranglisten** (Team → Rangliste): je Positionsgruppe und Pound for Pound (DOTS), nur mit Opt-in, nie mit Körpergewicht. Es zählen nur protokollierte Sätze und Tests, keine Selbstangaben.

## Lebensmitteldatenbanken

Die GitHub Action `.github/workflows/lebensmittel.yml` lädt jede Woche (Nacht auf Sonntag) drei freie Datenbanken, bereitet sie mit `tools/lebensmittel/build.py` auf und legt sie auf dem Branch **`lebensmittel`** ab. Der Branch wird jedes Mal komplett ersetzt, alte Stände bleiben nicht liegen. Schlägt eine Quelle fehl, bleibt ihr letzter Stand.

| Quelle | Inhalt | Lizenz |
|---|---|---|
| Open Food Facts | Markenprodukte aus Österreich (AT zuerst) und Deutschland, Handelsketten auch über Eigenmarken | ODbL |
| Bundeslebensmittelschlüssel 4.0 (Max Rubner-Institut) | rund 7.000 Grundlebensmittel und Gerichte | CC BY 4.0 |
| Schweizer Nährwertdatenbank (BLV) | Grundlebensmittel | frei, mit Quellenangabe |

Eine offene österreichische Nährwertdatenbank gibt es nicht; der Österreich-Bezug kommt aus Open Food Facts (Verkaufsland, Handelsketten, österreichische Begriffe).
Die App lädt neue Stände im Hintergrund (höchstens alle 12 Stunden prüfen, nur geänderte Dateien), speichert sie im Gerät (IndexedDB) und sucht lokal. Ein verwendeter Treffer wird als eigenes Lebensmittel kopiert – eingetragene Werte gehen bei einem neuen Datenbank-Stand nicht verloren.

## Erinnerungen (Push)

Profil → Erinnerungen: pro Gerät aktivieren (iPhone: nur als Home-Bildschirm-App, ab iOS 16.4), Uhrzeiten für „Einheit des Tages“, „Readiness-Check“, „Protokoll offen“ und den Wochenrückblick am Sonntag wählen.
Push-Abo und Vorschau der nächsten Trainingstage liegen je Athlet in Supabase; den Versand übernimmt eine stündliche GitHub Action im Datenrepo. In diesem Repo steht nur der öffentliche Push-Schlüssel (`PUSH_VAPID_PUBLIC`), der Service Worker (`sw.js`) zeigt die Nachrichten an.

## Entwicklung

- Einzelne Datei `index.html` ohne Build-Schritt. Bei Änderungen die Cache-Version in `sw.js` erhöhen (`./tools/bump-cache.sh`), sonst sehen installierte Apps die neue Version nicht.
- Datenbankstruktur und Zugriffsregeln nur über neue Dateien in `supabase/migrations/`; die Action „Datenbank“ spielt sie ein, prüft die Regeln, stellt Login und E-Mail-Versand ein und stellt die Admin-Funktion bereit. Anleitung zur Einrichtung: [`docs/SUPABASE_EINRICHTUNG.md`](docs/SUPABASE_EINRICHTUNG.md).
- Tests: `python tests/smoke.py` öffnet die App mit neutralen Testdaten in iPhone- und Laptop-Breite, tippt jeden Button an und prüft Trainingsablauf, Planerregeln, Onboarding, Einstieg und den Abgleich gegen eine nachgebaute Supabase. Läuft bei jedem Push als GitHub Action (`.github/workflows/test.yml`), zusammen mit einer Prüfung der Cache-Version. `python tests/gruppen.py <Übungsdatenbank>` prüft Testprofile je Positionsgruppe (Action „Gruppentest“ im Datenrepo).
- Änderungen gehen direkt auf `main`.

Aufgaben des Ausbaus: [ROADMAP.md](ROADMAP.md) · Ideen und Verbesserungen: [BACKLOG.md](BACKLOG.md)
