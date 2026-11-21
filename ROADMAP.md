# AOS – Roadmap: Mehrbenutzer, Positionsgruppen, Coach, Ranglisten

Stand: 21.11.2026 · Version 1
Fachliche Details: Mehrbenutzer-Spezifikation v1 (Rollen, Datenmodell, Positionsgruppen, Coach-Übersicht, Ranglisten mit DOTS, Datenschutz).
Dieses Repo ist öffentlich: Hier stehen nur Aufgaben und Termine, keine persönlichen Werte.

**Leitbild:** AOS ist eine footballspezifische S&C-Coaching-KI für die Spieler der Red Tigers. Eine regelbasierte Engine plant für jeden Athleten vollautomatisch, abgestimmt auf seine Position und seine Daten. Kein Sprachmodell, die App bleibt kompakt. Der Coach sieht alles, greift aber nicht in die Planung ein.

## So wird die Liste geführt

- `[ ]` offen · `[x]` erledigt, mit Datum am Ende (`✅ TT.MM.JJJJ`)
- 👤 = erledigt der Admin selbst · ohne Zeichen = erledigt Claude
- Ein Task gilt erst als erledigt, wenn er umgesetzt **und** geprüft ist (Klicktest grün, Prüfkriterium erfüllt).
- Ein Meilenstein beginnt erst, wenn die Prüfung des vorherigen abgehakt ist.

## Überblick

| # | Zeitraum | Meilenstein | Ergebnis | Stand |
|---|---|---|---|---|
| **0** | 17.–22.11.2026 | Vorbereitung | Zugänge da | 2 / 2 ✅ |
| **M1** | 21.11.–06.12.2026 | Neue Basis: Datenbank, Login, Migration | AOS läuft wie heute, auf Supabase | 11 / 12 |
| **M2** | 07.–13.12.2026 | Engine personenneutral | persönliche Vorlieben nur noch im Profil | 0 / 6 |
| **M3** | 14.–27.12.2026 | Positionsgruppen | Planung für alle Positionen | 0 / 9 |
| **M4** | 28.12.2026–10.01.2027 | Einladungen, Onboarding, Datenschutz, Pilot | 3–5 Pilot-Athleten nutzen AOS | 0 / 12 |
| **Start** | ab 11.01.2027 | Teamstart | alle eingeladenen Spieler | 0 / 2 |
| **M5** | 11.–24.01.2027 | Coach-Übersicht | Coach sieht alle Athleten | 0 / 5 |
| **M6** | 25.01.–07.02.2027 | Ranglisten mit DOTS | erste Ranglisten nach der Testwoche Anfang Februar | 0 / 6 |
| **Stopp** | 01.03.–21.03.2027 | Funktionsstopp bis zum ersten Spiel | nur Fehlerbehebungen | – |
| später | ab Saison | Nachrichten Coach → Athlet prüfen | Entscheidung, ob nötig | 0 / 1 |

**Leitlinien:** Große Umstellungen nur am Wochenende und an einem Phasenwechsel, damit das laufende Training nicht gestört wird. Teamstart mit Beginn des Feldtrainings im Jänner. Ab 01.03.2027 keine neuen Funktionen mehr.

---

## 0 · Vorbereitung (17.–22.11.2026)

- [x] **0.1** Anleitung für die Supabase-Einrichtung schreiben: [`docs/SUPABASE_EINRICHTUNG.md`](docs/SUPABASE_EINRICHTUNG.md) ✅ 16.11.2026
- [x] **0.2** 👤 Supabase einrichten nach der Anleitung (Konto, Projekt in Frankfurt, Login-Einstellungen, GitHub-Secrets), Projekt-URL und Publishable key an Claude geben ✅ 21.11.2026 (Projekt `sraocwhvkisomjjoqznr`, Frankfurt; öffentliche Verbindungsdaten in `supabase/projekt.json`)

## M1 · Neue Basis (23.11.–06.12.2026)

- [x] **M1.1** Datenbankschema `team_season`, `profiles`, `records` als SQL-Migration im Repo (`supabase/migrations/`) ✅ 21.11.2026 (`supabase/migrations`, wird per GitHub Action „Datenbank“ eingespielt)
- [x] **M1.2** Zugriffsregeln (Row Level Security): Athlet nur eigene Daten, Coach alle lesen, nichts schreiben, Admin Rollen und Teamdaten; automatischer Test der Regeln ✅ 21.11.2026 (16 automatische Prüfungen in `supabase/tests`, laufen bei jeder Änderung)
- [x] **M1.3** Login per Magic Link in der App: Anmelden, Abmelden, Sitzung auf iPhone und Laptop merken ✅ 21.11.2026 (Anmeldelink per E-Mail, in der App vom Home-Bildschirm mit Übergabecode; Code direkt in der Mail erst mit eigenem E-Mail-Versand (M4.12))
- [x] **M1.4** Abgleich auf Supabase umstellen: pro Datensatz, jüngste Änderung gewinnt, Löschungen übertragen, offline Warteschlange ✅ 21.11.2026 (läuft bis zur Umstellung zusätzlich zum Datenrepo; Klicktest mit nachgebauter Datenbank)
- [x] **M1.5** Teamdaten (Saisonstart, Phasenkalender, Feldtraining, Spiele) aus `team_season` statt aus der Plandatei lesen ✅ 21.11.2026 (Saison, Phasen und Feldtraining aus `team_season`)
- [x] **M1.6** Einmaliges Migrationsskript `tools/`: bestehende Daten aus `AOS_DATA` nach Supabase (Daten selbst nie in diesem Repo) ✅ 21.11.2026 (`AOS_DATA/tools/supabase_sync.py`, GitHub Action „Supabase“: 105 Datensätze + 28 Löschmarken übertragen und geprüft, wiederholbar)
- [x] **M1.7** Klicktest erweitern: nachgebaute Datenbank statt Datenrepo, Login, Abgleich, „Coach kann nichts ändern“ ✅ 21.11.2026 (Klicktest: Login, Übergabecode, Abgleich, Löschung, jüngste Änderung gewinnt; „Coach kann nichts ändern“ prüft der Datenbanktest)
- [x] **M1.8** Wöchentlicher Export der Datenbank als Backup nach `AOS_DATA` (GitHub Action); hält das Free-Projekt zugleich aktiv (Pause nach 7 Tagen ohne Nutzung) ✅ 21.11.2026 (sonntags nachts nach `AOS_DATA/backup/supabase.json`; Erinnerungen können schon aus Supabase lesen (Umschalter `AOS_SOURCE`))
- [x] **M1.9** Speicherung über GitHub-Token entfernen (inkl. Ablaufwarnung W6) ✅ 21.11.2026 (GitHub-Token wird von jedem Gerät entfernt, Ablaufwarnung entfällt)
- [x] **M1.10** Umstellung am Wochenende 05./06.12. durchführen ✅ 21.11.2026 (auf 21.11. vorgezogen; Erinnerungen lesen aus Supabase, `aos-data.json` ist Archiv, Planänderungen in `AOS_DATA/planner` und `db` gehen automatisch nach Supabase)
- [x] **M1.11** Prüfung: alle Einheiten, Tests und Verläufe vollständig; geplante Einheit für Mo 07.12. vor und nach der Umstellung identisch; Coach-Testkonto kann nichts ändern ✅ 21.11.2026 (Einheiten 23.11.–13.12. inkl. Mo 07.12., Kalorienziele und alle Verläufe mit Daten aus Supabase identisch zum Datenrepo; Coach-Rechte über den Datenbanktest)
- [ ] **M1.12** 👤 Auf iPhone und Laptop anmelden und bestätigen, dass alles wie gewohnt da ist

## M2 · Engine personenneutral (07.–13.12.2026)

- [ ] **M2.1** Bestandsaufnahme: alle personenbezogenen Annahmen im Code auflisten (Positionsanteile, Trainingsort, Ziele, Startlasten, Feldtage)
- [ ] **M2.2** Positionen mit Anteil als Profilwert statt fest im Code
- [ ] **M2.3** Langfristziele als Profilwert; Richtwerte je Positionsgruppe (relativ zum Körpergewicht) als Standard
- [ ] **M2.4** Trainingsorte, Wochentage und Startlasten nur noch aus Profil und Protokollen
- [ ] **M2.5** Neutrales Standardprofil für neue Athleten
- [ ] **M2.6** Prüfung: eigener Plan unverändert; Testprofil „Einsteiger, WR, Home Gym“ bekommt einen vollständigen, eigenen Plan ohne fremde Vorlieben

## M3 · Positionsgruppen (14.–27.12.2026)

- [ ] **M3.1** Fünf Positionsgruppen (Big Men, Big Skill, Skill, QB, Specialists) und Zuordnung aller Positionen
- [ ] **M3.2** Haupt- und Nebenposition nach Anteil mischen
- [ ] **M3.3** Übungsdatenbank v2.0: Positionsrelevanz 0–3 je Gruppe (in `AOS_DATA/db`)
- [ ] **M3.4** Fehlende Übungen ergänzen (z. B. Partner-/Schlittendrücken, Backpedal-Drills, Rotationsübungen QB, Übungen für Specialists)
- [ ] **M3.5** Gruppenregeln im Planer: Sätze, Wiederholungen, Power-Schwerpunkt, Bodenkontakte, Sprintinhalte, Prehab, keine schweren Überkopfübungen für QB
- [ ] **M3.6** Positionsspezifische Inhalte in P4 je Gruppe
- [ ] **M3.7** Trainingserfahrung: Regeln für Einsteiger, „Umsetzen technisch sicher?“ → sonst Trap-Bar-Sprung und Speed Pull
- [ ] **M3.8** Ein Testprofil je Gruppe im Klicktest
- [ ] **M3.9** 👤 Fachliche Prüfung: Pläne P2–P5 der Testprofile nebeneinander (Vergleichsansicht von Claude). Ein O-Liner trainiert erkennbar anders als ein Cornerback

## M4 · Einladungen, Onboarding, Pilot (28.12.2026–10.01.2027)

- [ ] **M4.1** Admin-Bereich: Spieler per E-Mail einladen, Rollen vergeben, Konten deaktivieren
- [ ] **M4.2** Onboarding in 8 Schritten (Einwilligung, Position, Körperdaten, Erfahrung, Ort, Trainingstage, Einschränkungen, Eingangstests in Woche 1)
- [ ] **M4.3** Einwilligung und Datenschutzinfo in der App (Text abgestimmt mit dem Vorstand)
- [ ] **M4.4** Konto löschen und eigene Daten exportieren
- [ ] **M4.5** Einstieg für spätere Starter: 2 Wochen Einstieg, dann im Teamkalender
- [ ] **M4.6** Teamkalender (Spiele, Feldtraining, Saisonstart) durch den Admin in der App pflegen
- [ ] **M4.7** Push-Erinnerungen pro Athlet (Anmeldung je Gerät, Versand für alle)
- [ ] **M4.8** 👤 Freigabe durch den Vorstand einholen
- [ ] **M4.9** 👤 Pilot ab ca. 04.01.: Pilot-Athleten einladen, eine Woche trainieren lassen, Rückmeldungen sammeln
- [ ] **M4.10** Rückmeldungen aus dem Pilot umsetzen
- [ ] **M4.11** Prüfung: Onboarding ohne Hilfe geschafft, niemand sieht fremde Daten, Pläne passen zu Position und Ausstattung
- [ ] **M4.12** 👤 Eigenen E-Mail-Versand einrichten (SMTP-Anbieter, Anleitung von Claude), **vor M4.9**: Der eingebaute Versand von Supabase erreicht nur Mitglieder der Supabase-Organisation, max. 2 Mails pro Stunde

## Teamstart (ab 11.01.2027)

- [ ] **S.1** 👤 Alle Spieler einladen
- [ ] **S.2** Arbeitsweise neu bewerten: Pushes direkt auf `main` treffen ab jetzt alle Athleten gleichzeitig

## M5 · Coach-Übersicht (11.–24.01.2027)

- [ ] **M5.1** Eigene Ansicht für die Rolle Coach
- [ ] **M5.2** Athletenliste: Name, Positionsgruppe, Phase und Woche, Einheiten erledigt / geplant, letzte Einheit, Readiness-Trend, Gewicht und Veränderung 4 Wochen
- [ ] **M5.3** Hinweise: 7 Tage kein Training, Entlastung aktiv, Beschwerden gemeldet
- [ ] **M5.4** Detailansicht je Athlet mit den Verlaufsansichten, nur lesen
- [ ] **M5.5** Prüfung: Der Coach findet in unter einer Minute, wer seit 7 Tagen nicht trainiert hat und wessen Gewicht sich stark verändert

## M6 · Ranglisten (25.01.–07.02.2027)

- [ ] **M6.1** Opt-in für Ranglisten im Profil
- [ ] **M6.2** Ranglisten-Ansicht in der Datenbank: nur Name, Gruppe, Disziplin, Wert bzw. Score, nie Körpergewicht
- [ ] **M6.3** e1RM für Ranglisten nur aus Sätzen mit höchstens 5 Wdh und RPE ≥ 7 der letzten 8 Wochen
- [ ] **M6.4** DOTS-Score (Männer/Frauen) berechnen und gegen einen Referenzrechner prüfen
- [ ] **M6.5** Anzeige: Rangliste je Positionsgruppe und Pound for Pound
- [ ] **M6.6** Prüfung: Athleten ohne Opt-in erscheinen nirgends; erste Ranglisten nach der Testwoche Anfang Februar

## Später

- [ ] **L.1** Nachrichten Coach → Athlet: Bedarf mit dem Coach klären, dann entscheiden

---

## Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| Vorstand gibt den Datenschutz nicht rechtzeitig frei | M1–M3 laufen unabhängig davon; nur der Teamstart verschiebt sich |
| Umstellung M1 stört das laufende Training | Nur am Wochenende des Phasenwechsels; alte Version bleibt bis zur Prüfung abrufbar |
| Fehler treffen alle Athleten sofort (Pushes direkt auf `main`) | Klicktest mit Testprofilen vor jedem Push; bei Problemen sofort auf den letzten Stand zurück; Bewertung in S.2 |
| Weihnachten verzögert M3/M4 | Puffer 08.–28.02.2027 |
| Positionsprofile fachlich unpassend | Fachliche Prüfung in M3.9, Pilot in M4 |
