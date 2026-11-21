# M2 · Engine personenneutral – Bestandsaufnahme und Umsetzung

Stand 21.11.2026. Ziel: Alles, was nur für einen bestimmten Athleten gilt, kommt aus dessen Profil bzw. Protokollen. Im Code stehen nur allgemeine Standards. Keine persönlichen Werte in diesem Dokument.

## Bestandsaufnahme (M2.1)

| # | Annahme | Wo sie steckte | Jetzt |
|---|---|---|---|
| 1 | Positionen und Anteile | Profilfeld `positions` vorhanden, aber ohne Eingabe; von der Engine nicht genutzt | Profil → *Position & Trainingstage*: Haupt- und Nebenposition mit Anteil 10–50 %. `posMix()` / `groupMix()` liefern Positionsgruppen (OL, DL, LB, TE, RB, WR, DB, QB) gemischt nach Anteil (M2.2) |
| 2 | Langfristziele | eigene Ziele im Datenbereich `goals`; ohne Ziele kein Schwerpunkt | eigene Ziele haben Vorrang; sonst **Richtwerte der Positionsgruppe** relativ zum Körpergewicht (`GOAL_STD`, Trainingspfade 2.0), gemischt nach Anteil. Sie steuern den Schwerpunkt-Satz und stehen im Verlauf unter *Ziele* (übernehmbar) (M2.3) |
| 3 | Trainingstage | fester Wochenplan Mo/Mi/Do/Fr im Code | Profilfeld `trainingDays`; D1–D4 der Reihe nach auf die Tage. Bei weniger Tagen verteilt AOS den Wochenumfang (Sessionplaner 3.10). Bestehende Profile ohne Angabe behalten den bisherigen Plan (M2.4) |
| 4 | Trainingsorte und Ausstattung | Profil (`locations`, Freitext, Standardtage) | unverändert aus dem Profil (M2.4) |
| 5 | Startlasten | `start_loads` nur in früheren festen Blöcken; automatische Blöcke leer | Lasten nur aus Protokollen und Tests (e1RM, Ableitung über allgemeine Verhältnisse `START_EST`). Ohne Daten: keine Lastvorgabe → Kalibrierung beim Onboarding (M4, Mehrbenutzer 6.2) (M2.4) |
| 6 | Spiele | nur eigener Kalender | Teamkalender (`team_season.games`) plus eigener Kalender (`apGames`) |
| 7 | Planerregeln | eine persönliche Plandatei | allgemeine Regeln als Referenzdokument `planer` (ohne persönliche Tage), persönliche Planerdaten im Profil, Teamdaten aus `team_season`; zusammengeführt in `sbRefLoad` (M2.5) |
| 8 | Ernährungsregeln | persönliche Datei | bleibt persönlich im Profil (`profiles.nutrition`); neue Athleten bekommen sie im Onboarding (M4) |
| 9 | Übungsauswahl je Position | Pools D1–D4 im Code (`AP_SLOTS`) auf eine Positionsmischung zugeschnitten | **M3**: Kandidatenlisten je Positionsgruppe aus `AOS_Trainingspfade.json`, Mischung nach `groupMix()` |
| 10 | Erfahrung, Umsetz-Technik, Alter, Verletzungen | nicht vorhanden | **M3/M4** (Modifikatoren der Trainingspfade, Onboarding) |

## Neutrales Standardprofil (M2.5)

Neue Profile (`seedData()`): keine Position, keine Ziele, Trainingstage Mo/Di/Do/Fr, Standardorte (Public Gym, Home Gym, Feld). Plan aus den allgemeinen Planerregeln + Teamdaten.

## Prüfung (M2.6)

- Eigener Plan: alle geplanten Einheiten bis Ende Jänner mit derselben Datenlage vor und nach M2 verglichen – 0 Unterschiede.
- Testprofil „WR, 80 kg, Home Gym, ohne Ziele und Tests“: vollständige Einheiten an Mo/Di/Do/Fr in allen Phasen, eigene Richtwerte (WR: Kniebeuge 1,5 × KG usw.), kein fremder Schwerpunkt, keine fremden Trainingstage oder freien Tage. Positionsspezifische Übungswahl folgt in M3.
- Klicktest prüft Richtwerte (WR), Mischung der Positionsgruppen und den Wochenplan aus den Trainingstagen.
