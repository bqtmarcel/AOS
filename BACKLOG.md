# AOS – Backlog

Sammlung möglicher Verbesserungen und Weiterentwicklungen. Dieses Repo ist öffentlich, deshalb stehen hier **keine persönlichen Werte** (Lasten, Körperdaten, Pläne). Fachliche Details stehen in den Spezifikationen in `AOS_DATA/docs`.

Priorität: **P1** = bald und mit großem Nutzen · **P2** = sinnvoll · **P3** = später oder nur eine Idee
Aufwand: **S** = unter 1 Stunde · **M** = einige Stunden · **L** = mehr als ein Tag

---

## Erledigt (15.11.2026) – Durchsicht iPhone und Laptop

- Code der alten, von Hand geführten Planverwaltung entfernt (rund 600 Zeilen): Blöcke und Trainingstage bearbeiten, Anpassungsvorschläge, Druckansicht, Strong- und Markdown-Export, alte Dialoge für Positionen, Orte und Ernährung, Gewichtseingabe der alten Übersicht, ungenutzte CSS-Regeln
- Persönliche Beispielwerte aus Hinweistexten entfernt
- Navigation am Laptop jetzt rund wie am iPhone
- Plan: Wochenraster am iPhone lesbar, Einheiten einklappbar wie im Profil
- Verlauf: alle Bereiche einklappbar, mehr Abstand bei „+ Neue Messung“
- Einheitliche Begriffe („Ruhetag“ in Übersicht und Training) und Zahlenformat (kcal mit Tausenderpunkt)

---

## 1. Training

| # | Idee | Nutzen | Prio | Aufwand |
|---|---|---|---|---|
| T1 | **Pausentimer** beim Erfassen: startet nach jedem Satz automatisch mit der Pause aus dem Plan, mit Vibration bzw. Ton am Ende | Kein Wechsel in eine andere App im Gym | ✅ erledigt | M |
| T2 | **Letzte Leistung je Übung** direkt im Satz anzeigen („letztes Mal: 3×5 @RPE 7“) | Schnellere Orientierung beim Ausführen | ✅ erledigt | S |
| T3 | **Scheibenrechner**: welche Scheiben pro Seite bei der vorgegebenen Last (Stange einstellbar) | Weniger Kopfrechnen | P2 | S |
| T4 | **Aufwärmsätze** automatisch zur Arbeitslast vorschlagen | Strength-Coach-Verhalten | P2 | M |
| T5 | **Deload-Signale** sichtbar machen (Spezifikation 3.7): mehrere schlechte Tagesformen, RPE über Cap, Beschwerden → Hinweis und automatische Entlastung | Überlastung früh erkennen | P2 | M |
| T6 | **Testwoche am Phasenende** (Spezifikation 3.8): Tests als eigene Einheit vorschlagen und Ergebnisse direkt in den Verlauf übernehmen | Tests nicht vergessen | P2 | M |
| T7 | **In-Season-Modus**: ab dem ersten Spiel 1–2 Einheiten pro Woche, Abstand zum Spieltag beachten (offene Punkte 5 und 8 der Spezifikation) | Planung über die Vorbereitung hinaus | P2 | L |
| T8 | **Templates für P2–P5** im Datenrepo anlegen; der Plan zeigt dort derzeit „noch keine Templates“ | Plan über Block 1 hinaus | P1 | M (Planung mit Claude) |
| T9 | „+ Freie Einheit“ als richtigen Button gestalten und Übungen aus der Übungsdatenbank auswählbar machen | Einheitliche Bedienung | P3 | M |

## 2. Verlauf und Auswertung

| # | Idee | Nutzen | Prio | Aufwand |
|---|---|---|---|---|
| V1 | **Geschätztes 1RM (e1RM)** je Hauptübung als Verlauf, klar als Schätzung gekennzeichnet | Fortschritt trotz wechselnder Wdh sichtbar | P2 | M |
| V2 | **Wochenbelastung**: Gym-Volumen und Feld-Belastung (Session-RPE) gemeinsam als Wochenbalken, Warnung bei starkem Anstieg | Verletzungsrisiko senken | P2 | M |
| V3 | **Körpergewicht als 7-Tage-Schnitt** im Diagramm statt nur Einzelwerte | Ruhigeres, ehrlicheres Bild | P2 | S |
| V4 | **Ziele mit Fortschrittsbalken** (aktuell / Ziel) statt nur Tabelle | Motivation | P3 | S |
| V5 | **Readiness-Verlauf** (Tagesform, Beschwerden) als kleine Kurve | Muster erkennen | P3 | S |

## 3. Ernährung

| # | Idee | Nutzen | Prio | Aufwand |
|---|---|---|---|---|
| E1 | **Kalorienziel automatisch anpassen** nach Gewichtstrend (Spezifikation 4.4), mit Begründung | Weniger Nachrechnen | P2 | M |
| E2 | **Barcode per Kamera** (Foto des Strichcodes) für Open Food Facts | Schnelleres Eintragen | P2 | M |
| E3 | **Mahlzeit vom Vortag kopieren** mit einem Tipp | Weniger Tipparbeit | ✅ erledigt | S |
| E4 | **Supplements**: Wochenübersicht abgehakt / vergessen | Regelmäßigkeit | P3 | S |
| E5 | **Meal-Prep-Plan** (Spezifikation 12) als eigene Ansicht: Mengen für die Woche, direkt in die Einkaufsliste | Planung am Wochenende | P2 | M |

## 4. Übersicht und Bedienung

| # | Idee | Nutzen | Prio | Aufwand |
|---|---|---|---|---|
| U1 | **Wochenstreifen** in der Übersicht schon am Sonntag bzw. vor Blockbeginn für die kommende Woche zeigen (derzeit erscheint er erst, wenn die laufende Woche Einheiten hat) | Woche vorausplanen | P2 | S |
| U2 | **Erinnerungen** (Training, Supplements, Gewicht) über Web-Push; auf dem iPhone ab iOS 16.4 für installierte Web-Apps möglich | Weniger vergessen | P3 | L |
| U3 | **Datumsfeld in der Ernährung** durch eigene Anzeige ersetzen (Wochentag + Datum), damit es überall gleich aussieht | Einheitliches Bild | P3 | S |
| U4 | Begriffe angleichen: „Saisonstart“ (Übersicht, Plan) und „Spiel“ (Profil → Kalender) | Klarheit | P3 | S |
| U5 | **Laptop-Layout** mit zwei Spalten ab großer Breite (z. B. Ernährung: Mahlzeiten links, Abdeckung rechts) | Platz am Laptop nutzen | P3 | M |
| U6 | **Sync-Status** verständlicher: Punkt im Kopf antippbar mit „zuletzt gespeichert um …“ | Vertrauen in die Speicherung | P2 | S |

## 5. Technik und Wartung

| # | Idee | Nutzen | Prio | Aufwand |
|---|---|---|---|---|
| W1 | **CSS zusammenführen**: Die Gestaltung besteht aus mehreren übereinanderliegenden Schichten (Grundlayout, Design, Variante B, Red Tigers, Chrome Glass) mit vielen Überschreibungen und `!important`. Eine Schicht mit klaren Variablen | Änderungen am Design werden einfacher und sicherer | P1 | M |
| W2 | **Automatischer Klicktest** (Playwright) als GitHub Action: alle Ansichten in iPhone- und Laptop-Breite öffnen, jeden Button einmal antippen, Fehler melden – mit neutralen Testdaten | Fehler vor dem Ausrollen finden | ✅ erledigt | M |
| W3 | **Altfelder im Datenmodell prüfen** (z. B. `blocks`, `unavailable`, `suggestionDecisions` aus der alten Planverwaltung): was wird noch gebraucht, was kann per `migrate()` entfernt werden | Kleinere Datei, weniger Verwirrung | P2 | M |
| W4 | **`index.html` aufteilen** (z. B. `css/`, `js/kern.js`, `js/training.js` …), weiterhin ohne Build-Schritt | Übersichtlicher bei weiterem Wachstum | P3 | M |
| W5 | **Cache-Version automatisch** aus dem Inhalt von `index.html` erzeugen (GitHub Action), damit das Erhöhen in `sw.js` nicht vergessen wird | Weniger Handarbeit | ✅ erledigt | S |
| W6 | **Token-Ablauf**: rechtzeitig vor Ablauf des GitHub-Tokens warnen | Kein plötzlicher Ausfall der Speicherung | P2 | S |
| W7 | **Barrierefreiheit** prüfen (Kontraste der grauen Texte, Fokus-Rahmen, Beschriftungen der Icon-Buttons) | Bessere Lesbarkeit im Gym-Licht | P3 | S |
