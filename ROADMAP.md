# AOS – Roadmap: Mehrbenutzer, Positionsgruppen, Coach, Ranglisten

Stand: 24.11.2026 · Version 1
Fachliche Details: Mehrbenutzer-Spezifikation v1.7 in `AOS_DATA/docs` (Rollen, Datenmodell, Positionsgruppen, Onboarding und Einstieg, Coach-Übersicht, Ranglisten mit DOTS, Datenschutz).
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
| **M1** | 21.11.–06.12.2026 | Neue Basis: Datenbank, Login, Migration | AOS läuft wie heute, auf Supabase | 12 / 12 ✅ |
| **M2** | 21.11.2026 | Engine personenneutral | persönliche Vorlieben nur noch im Profil | 6 / 6 ✅ |
| **M3** | 21.11.2026 | Positionsgruppen | Planung für alle Positionen | 9 / 11 |
| **M4** | 28.12.2026–10.01.2027 | Einladungen, Onboarding, Datenschutz, Pilot | 3–5 Pilot-Athleten nutzen AOS | 9 / 13 |
| **Start** | ab 11.01.2027 | Teamstart | alle eingeladenen Spieler | 0 / 2 |
| **M5** | 11.–24.01.2027 | Coach-Übersicht | Coach sieht alle Athleten | 6 / 7 |
| **M6** | 25.01.–07.02.2027 | Ranglisten mit DOTS | erste Ranglisten nach der Testwoche Anfang Februar | 5 / 6 |
| **Stopp** | 01.03.–21.03.2027 | Funktionsstopp bis zum ersten Spiel | nur Fehlerbehebungen | – |
| später | ab Saison | Nachrichten Coach → Athlet prüfen; alten GitHub-Token löschen | Entscheidung, ob nötig | 0 / 2 |

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
- [x] **M1.12** 👤 Auf iPhone und Laptop anmelden und bestätigen, dass alles wie gewohnt da ist ✅ 21.11.2026 (iPhone und Laptop geprüft)

## M2 · Engine personenneutral (21.11.2026)

- [x] **M2.1** Bestandsaufnahme: alle personenbezogenen Annahmen im Code auflisten (Positionsanteile, Trainingsort, Ziele, Startlasten, Feldtage) ✅ 21.11.2026 (`docs/M2_ENGINE_PERSONENNEUTRAL.md`)
- [x] **M2.2** Positionen mit Anteil als Profilwert statt fest im Code ✅ 21.11.2026 (Profil → Position & Trainingstage; Mischung der Positionsgruppen nach Anteil)
- [x] **M2.3** Langfristziele als Profilwert; Richtwerte je Positionsgruppe (relativ zum Körpergewicht) als Standard ✅ 21.11.2026 (eigene Ziele haben Vorrang, sonst Richtwerte der Gruppe × Körpergewicht; steuern den Schwerpunkt-Satz)
- [x] **M2.4** Trainingsorte, Wochentage und Startlasten nur noch aus Profil und Protokollen ✅ 21.11.2026 (Trainingstage im Profil statt festem Wochenplan; Orte aus dem Profil; Lasten nur aus Protokollen und Tests)
- [x] **M2.5** Neutrales Standardprofil für neue Athleten ✅ 21.11.2026 (Standardprofil ohne Position und Ziele, Mo/Di/Do/Fr; allgemeine Planerregeln als Referenzdokument)
- [x] **M2.6** Prüfung: eigener Plan unverändert; Testprofil „Einsteiger, WR, Home Gym“ bekommt einen vollständigen, eigenen Plan ohne fremde Vorlieben ✅ 21.11.2026 (eigener Plan bis Ende Jänner 0 Unterschiede; Testprofil WR/Home Gym vollständig; positionsspezifische Übungswahl folgt in M3)

## M3 · Positionsgruppen (21.11.2026)

- [x] **M3.1** Acht Positionsgruppen (OL, DL, LB, TE, RB, WR, DB, QB) und Zuordnung aller Positionen; Varianten DE/DT/NT, CB/S, FB (Trainingspfade 2.0, Specialists derzeit nicht vorgesehen) ✅ 21.11.2026
- [x] **M3.2** Haupt- und Nebenposition nach Anteil mischen (Übungswahl über Score, Positionsslots der Nebengruppe, Pflicht halb ab 30 %, Zahlenwerte gemittelt) ✅ 21.11.2026
- [x] **M3.3** Übungsdatenbank v2.0: Positionsrelevanz 0–3 je Gruppe (in `AOS_DATA/db`) ✅ 21.11.2026
- [x] **M3.4** Fehlende Übungen ergänzt: Schlitten, Hand Fight, 2-Punkt-Start, Backpedal + Turn, QB Drop-Back, Hüftbeuger-Marsch, Außenrotation Band, Release, Press/Jam ✅ 21.11.2026
- [x] **M3.5** Gruppenregeln im Planer: Vorlage nach Trainingstagen (2/3/4), Kandidaten, Sätze-Delta der Hauptübungen, Wdh der Ergänzung, Kontaktfaktor, Pflichtübungen, Ausschlüsse (QB kein schweres Überkopfdrücken, OL/DT keine Depth Jumps) ✅ 21.11.2026
- [x] **M3.6** Positionsspezifische Inhalte P3–P5 je Gruppe: Feld-Slot (Starts, Cuts, Backpedal, Press/Jam, Get-off, Drop-Back) an Feldtagen aus dem Profil, sonst Hinweis aufs Teamtraining ✅ 21.11.2026
- [x] **M3.7** Trainingserfahrung (Einsteiger: Ausschlüsse, Grundübungen, RPE −0,5, weniger Kontakte) und „Umsetzen technisch sicher?“ (sonst Trap-Bar-Sprung, Speed Pull, KB Swing); hohes Körpergewicht ≥ 115 kg ✅ 21.11.2026
- [x] **M3.8** Testprofil je Gruppe: Action „Gruppentest“ im Datenrepo (echte Übungsdatenbank, 8 Profile, Prüffälle der Trainingspfade); Gruppenregeln zusätzlich im Klicktest ✅ 21.11.2026
- [ ] **M3.9** 👤 Fachliche Prüfung: Pläne P2–P5 der Testprofile nebeneinander (Vergleichsansicht von Claude). Ein O-Liner trainiert erkennbar anders als ein Cornerback. Danach entscheidet Marcel, ob er seinen eigenen Plan umstellt (Profil → Planung, gilt ab dem nächsten Block)
- [x] **M3.10** Gelernte Muster aus hochgeladenen Trainingssystemen (Lernbasis `AOS_DATA/docs/AOS_Planungswissen.json`, Regeln in `planner/plan.json → rules.gelernte_muster`): R1 Aufwärmvorlage, R2 Top-Satz + Back-off (Back-off-Prozent lernt aus den eigenen Sätzen), R3 Prehab in Sprung-/Wurfpausen, R4 Kontrastpaare P3, R5 Speed Strength, R6 Teil-ROM, R7 Feld-Drills und Feldtests, R8 EMOM-Timer, R9 Finisher; Übungsdatenbank v2.1, Trainingspfade v2.1. Ohne aktive Regel plant AOS wie bisher (geprüft mit echter Datenbank, beide Planungsarten, alle Phasen; Klicktest grün) ✅ 24.11.2026
- [ ] **M3.11** 👤 Erste Wochen mit den gelernten Mustern beobachten (Aufwärmen, Back-off-Lasten, Kontrastpaare in P3); Rückmeldung, welche Muster bleiben oder angepasst werden

Hinweis: Bestehende Profile planen weiter mit den bisherigen Vorlagen, bis der Athlet umstellt. Alter, Verletzungen, Mobilitäts-Screen und Zeit pro Einheit aus den Trainingspfaden kommen mit dem Onboarding (M4.2).

## M4 · Einladungen, Onboarding, Pilot (28.12.2026–10.01.2027)

- [x] **M4.1** Admin-Bereich: Spieler per E-Mail einladen, Rollen vergeben, Konten deaktivieren (Team → Verwaltung: Einladen per Admin-Funktion auf dem Server, Rollen Spieler/Coach/Admin, Sperren; Mails erreichen Spieler erst mit M4.12) ✅ 21.11.2026
- [x] **M4.2** Onboarding beim ersten Login (Position, Körperdaten, Erfahrung, Trainingsstand, Ort und Ausstattung, Trainingstage und Zeit, Einschränkungen, Ergebnis); Arbeitsgewichte als Startwert (95 %, zählen nicht für Ranglisten); „Später einrichten“, Start auch im Profil; reine Coach-Konten ohne Onboarding ✅ 22.11.2026
- [x] **M4.2a** Gegebenheiten im Profil und in der Planung (vor dem Onboarding): Zeit pro Einheit, Verletzungen der letzten 12 Monate, Mobilitäts-Check, Körpergewichtsziel, Außenbelastung, Alter und Größe; wirken auf Übungswahl, Pflicht, Kontakte und Aufwärmen ✅ 21.11.2026
- [x] **M4.3** ~~Einwilligung und Datenschutzinfo in der App~~ entfällt: Datenschutz ist außerhalb der App geregelt, in der App keine Bestätigung (Entscheidung Marcel) ✅ 21.11.2026
- [x] **M4.4** Konto löschen und eigene Daten exportieren (Profil → AOS-Konto: Daten herunterladen, Konto samt Daten löschen; der letzte Admin kann sich nicht löschen) ✅ 21.11.2026
- [x] **M4.5** Einstieg für spätere Starter: Einstiegsstufe 1–3 aus der Standortbestimmung (Beschwerden eine Stufe tiefer), Einstiegswochen parallel zum Teamkalender mit P1-Dosierung (RPE ≤ 7 bzw. 7,5), Team-Entlastung zählt als Einstieg, in P5/Saison nur RPE-Grenze, Eingangstests am Ende; Nachsteuerung nach Woche 1 (Woche nachsetzen bzw. vorzeitig beenden) ✅ 22.11.2026
- [x] **M4.6** Teamkalender (Spiele, Feldtraining, Saisonstart) durch den Admin in der App pflegen (Team → Verwaltung → Teamkalender: Spiele, Feldtraining-Tage, Start und Dauer) ✅ 21.11.2026
- [x] **M4.7** Push-Erinnerungen pro Athlet (Anmeldung je Gerät, Versand für alle) (Erinnerungen für alle aktiven Athleten mit eigenen Geräten und Uhrzeiten) ✅ 21.11.2026
- [x] **M4.8** 👤 Freigabe durch den Vorstand einholen ✅ 21.11.2026
- [ ] **M4.9** 👤 Pilot ab ca. 04.01.: Pilot-Athleten einladen, eine Woche trainieren lassen, Rückmeldungen sammeln
- [ ] **M4.10** Rückmeldungen aus dem Pilot umsetzen
- [ ] **M4.11** Prüfung: Onboarding ohne Hilfe geschafft, niemand sieht fremde Daten, Pläne passen zu Position und Ausstattung
- [ ] **M4.12** 👤 Eigenen E-Mail-Versand einrichten nach [`docs/EMAIL_VERSAND.md`](docs/EMAIL_VERSAND.md) (5 GitHub-Secrets; Versand, Mail-Vorlagen mit Code und Limit stellt die Action „Datenbank“ automatisch ein), **vor M4.9**: Der eingebaute Versand von Supabase erreicht nur Mitglieder der Supabase-Organisation, max. 2 Mails pro Stunde

## Teamstart (ab 11.01.2027)

- [ ] **S.1** 👤 Alle Spieler einladen
- [ ] **S.2** Arbeitsweise neu bewerten: Pushes direkt auf `main` treffen ab jetzt alle Athleten gleichzeitig

## M5 · Coach-Übersicht (11.–24.01.2027)

- [x] **M5.1** Eigene Ansicht für die Rolle Coach (Ansicht „Team“, Abschnitt „Athleten“ für Coach und Admin) ✅ 21.11.2026
- [x] **M5.2** Athletenliste: Name, Positionsgruppe, Phase und Woche, Einheiten erledigt / geplant, letzte Einheit, Readiness-Trend, Gewicht und Veränderung 4 Wochen ✅ 21.11.2026
- [x] **M5.3** Hinweise: 7 Tage kein Training, Entlastung aktiv, Beschwerden gemeldet (plus Gewichtsänderung ≥ 3 kg in 4 Wochen) ✅ 21.11.2026
- [x] **M5.4** Detailansicht je Athlet mit den Verlaufsansichten, nur lesen (letzte Einheiten, Gewicht, Tests, Ziele; nur lesen, nie im eigenen Datenbestand) ✅ 21.11.2026
- [x] **M5.6** Coach-Onboarding beim ersten Login (Willkommen und Rolle, Funktion und betreute Positionsgruppen, Vertraulichkeit bestätigen, Übersicht erklärt); bei Spieler + Coach nach dem Athleten-Onboarding; später änderbar unter Team → „Coach-Einstellungen“ ✅ 23.11.2026
- [x] **M5.7** Athletenliste zuerst nach den eigenen Gruppen („Meine Gruppen“ / „Alle“); reine Coach-Konten sehen nur Team und Profil ✅ 23.11.2026
- [ ] **M5.5** Prüfung: Der Coach findet in unter einer Minute, wer seit 7 Tagen nicht trainiert hat und wessen Gewicht sich stark verändert

## M6 · Ranglisten (25.01.–07.02.2027)

- [x] **M6.1** Opt-in für Ranglisten im Profil (Team → Rangliste → Mitmachen, mit Hinweis was sichtbar wird) ✅ 21.11.2026
- [x] **M6.2** Ranglisten-Ansicht in der Datenbank: nur Name, Gruppe, Disziplin, Wert bzw. Score, nie Körpergewicht (Tabelle rankings: Name, Gruppe, Disziplin, Wert, Score) ✅ 21.11.2026
- [x] **M6.3** e1RM für Ranglisten nur aus Sätzen mit höchstens 5 Wdh und RPE ≥ 7 der letzten 8 Wochen ✅ 21.11.2026
- [x] **M6.4** DOTS-Score (Männer/Frauen) berechnen und gegen einen Referenzrechner prüfen (Referenz 100 kg / 600 kg Total → 369,3 im Klicktest) ✅ 21.11.2026
- [x] **M6.5** Anzeige: Rangliste je Positionsgruppe und Pound for Pound ✅ 21.11.2026
- [ ] **M6.6** Prüfung: Athleten ohne Opt-in erscheinen nirgends; erste Ranglisten nach der Testwoche Anfang Februar

## Später

- [ ] **L.1** Nachrichten Coach → Athlet: Bedarf mit dem Coach klären, dann entscheiden

- [ ] **L.2** 👤 Alten GitHub-Token löschen: GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens (wird seit der Umstellung am 21.11.2026 nicht mehr gebraucht)
---

## Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| Vorstand gibt den Datenschutz nicht rechtzeitig frei | M1–M3 laufen unabhängig davon; nur der Teamstart verschiebt sich |
| Umstellung M1 stört das laufende Training | Nur am Wochenende des Phasenwechsels; alte Version bleibt bis zur Prüfung abrufbar |
| Fehler treffen alle Athleten sofort (Pushes direkt auf `main`) | Klicktest mit Testprofilen vor jedem Push; bei Problemen sofort auf den letzten Stand zurück; Bewertung in S.2 |
| Weihnachten verzögert M3/M4 | Puffer 08.–28.02.2027 |
| Positionsprofile fachlich unpassend | Fachliche Prüfung in M3.9, Pilot in M4 |
