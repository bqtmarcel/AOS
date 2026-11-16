# AOS – Backlog

Sammlung möglicher Verbesserungen und Weiterentwicklungen. Dieses Repo ist öffentlich, deshalb stehen hier **keine persönlichen Werte** (Lasten, Körperdaten, Pläne). Fachliche Details stehen in den Spezifikationen in `AOS_DATA/docs`.

Der große Ausbau (Mehrbenutzer, Positionsgruppen, Coach-Übersicht, Ranglisten) steht mit allen Tasks in [`ROADMAP.md`](ROADMAP.md).

Status: ✅ erledigt · 🟡 teilweise · ⏸ wartet (Grund in der Spalte)

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
| T3 | **Scheibenrechner**: welche Scheiben pro Seite bei der vorgegebenen Last (Stange einstellbar) | Weniger Kopfrechnen | ✅ erledigt | S |
| T4 | **Aufwärmsätze** automatisch zur Arbeitslast vorschlagen | Strength-Coach-Verhalten | ✅ erledigt | M |
| T5 | **Deload-Signale** sichtbar machen (Spezifikation 3.7): mehrere schlechte Tagesformen, RPE über Cap, Beschwerden → Hinweis und automatische Entlastung | Überlastung früh erkennen | ✅ erledigt: Entlastung läuft automatisch | M |
| T6 | **Testwoche am Phasenende** (Spezifikation 3.8): Tests als eigene Einheit vorschlagen und Ergebnisse direkt in den Verlauf übernehmen | Tests nicht vergessen | ✅ erledigt | M |
| T7 | **In-Season-Modus**: ab dem ersten Spiel 1–2 Einheiten pro Woche, Abstand zum Spieltag beachten (offene Punkte 5 und 8 der Spezifikation) | Planung über die Vorbereitung hinaus | ✅ erledigt | L |
| T8 | **Templates für P2–P5** im Datenrepo anlegen; der Plan zeigt dort derzeit „noch keine Templates“ | Plan über Block 1 hinaus | ✅ erledigt: AOS plant P2–P5 automatisch (Blockgenerator, 15.11.) | M (Planung mit Claude) |
| T9 | „+ Freie Einheit“ als richtigen Button gestalten und Übungen aus der Übungsdatenbank auswählbar machen | Einheitliche Bedienung | ✅ erledigt | M |
| T10 | **Autoregulation in der Einheit**: Liegt ein Satz einer Hauptübung über der RPE-Obergrenze, werden die restlichen Sätze automatisch 5 % leichter (mindestens 1 RPE über dem Ziel: 2,5 %) | Wiedereinstieg und schlechte Tage ohne Rechnen | ✅ erledigt | S |
| T11 | **Standortbestimmung automatisch übernehmen**: In der Testwoche eines Blocks landen Top-Satz Kniebeuge, Bank, Trap Bar und beste Broad-Jump-Weite beim Speichern direkt als Test im Verlauf | Neue Werte fließen ohne Knopfdruck in den nächsten Block | ✅ erledigt | S |
| T12 | **„Tag frei“ lässt Einheiten nachrücken** (wie die nicht verfügbaren Tage im Datenrepo) statt nur Kernübungen umzuverteilen | Feiertage, kurzfristige Ausfälle | ⏸ zurückgestellt (15.11.): bleibt vorerst wie bisher, evtl. später | M |

## 2. Verlauf und Auswertung

| # | Idee | Nutzen | Prio | Aufwand |
|---|---|---|---|---|
| V1 | **Geschätztes 1RM (e1RM)** je Hauptübung als Verlauf, klar als Schätzung gekennzeichnet | Fortschritt trotz wechselnder Wdh sichtbar | ✅ erledigt | M |
| V2 | **Wochenbelastung**: Gym-Volumen und Feld-Belastung (Session-RPE) gemeinsam als Wochenbalken, Warnung bei starkem Anstieg | Verletzungsrisiko senken | ✅ erledigt | M |
| V3 | **Körpergewicht als 7-Tage-Schnitt** im Diagramm statt nur Einzelwerte | Ruhigeres, ehrlicheres Bild | ✅ erledigt | S |
| V4 | **Ziele mit Fortschrittsbalken** (aktuell / Ziel) statt nur Tabelle | Motivation | ✅ erledigt | S |
| V5 | **Readiness-Verlauf** (Tagesform, Beschwerden) als kleine Kurve | Muster erkennen | ✅ erledigt | S |

## 3. Ernährung

| # | Idee | Nutzen | Prio | Aufwand |
|---|---|---|---|---|
| E1 | **Kalorienziel automatisch anpassen** nach Gewichtstrend (Spezifikation 4.4), mit Begründung | Weniger Nachrechnen | ✅ erledigt | M |
| E3 | **Mahlzeit vom Vortag kopieren** mit einem Tipp | Weniger Tipparbeit | ✅ erledigt | S |
| E4 | **Supplements**: Wochenübersicht abgehakt / vergessen | Regelmäßigkeit | ✅ erledigt | S |
| E6 | **Online-Suche mit Österreich-Fokus**: Handelskette im Suchbegriff (Billa, Spar, Hofer …) hebt deren Eigenmarken hervor, österreichische Begriffe werden zusätzlich auf Deutsch gesucht (Topfen → Quark), zusammengeschriebene Namen auch getrennt (Speckstangerl → Speck Stangerl), Treffer mit unvollständigen Nährwerten erscheinen ausgegraut | Mehr heimische Produkte finden | ✅ erledigt (16.11.) | M |
| E7 | **Rezeptrechner** für Selbstgekochtes: Zutaten mit Menge, Gewicht fertig gekocht und Portionen → Nährwerte pro 100 g und pro Portion; gespeichert als eigenes Gericht, jederzeit änderbar | Genaues Tracking ohne Schätzen | ✅ erledigt (16.11.) | M |
| E8 | **Lebensmitteldatenbanken lokal**: Open Food Facts (AT/DE), BLS 4.0 und Schweizer Nährwertdatenbank wöchentlich per GitHub Action aufbereitet, im Gerät gespeichert und offline durchsuchbar; Online-Suche nur noch ergänzend | Schnelle, verlässliche Suche ohne Limit | ✅ erledigt (16.11.) | L |
| E5 | **Meal-Prep-Plan** (Spezifikation 12) als eigene Ansicht: Mengen für die Woche, direkt in die Einkaufsliste | Planung am Wochenende | ⏸ braucht deine Antwort zu offenem Punkt 7 (Mittagessen pro Woche, Gefrierschrank) | M |

## 4. Übersicht und Bedienung

| # | Idee | Nutzen | Prio | Aufwand |
|---|---|---|---|---|
| U1 | **Wochenstreifen** in der Übersicht schon am Sonntag bzw. vor Blockbeginn für die kommende Woche zeigen (derzeit erscheint er erst, wenn die laufende Woche Einheiten hat) | Woche vorausplanen | ✅ erledigt | S |
| U3 | **Datumsfeld in der Ernährung** durch eigene Anzeige ersetzen (Wochentag + Datum), damit es überall gleich aussieht | Einheitliches Bild | ✅ erledigt | S |
| U4 | Begriffe angleichen: „Saisonstart“ (Übersicht, Plan) und „Spiel“ (Profil → Kalender) | Klarheit | ✅ erledigt | S |
| U5 | **Laptop-Layout** mit zwei Spalten ab großer Breite (z. B. Ernährung: Mahlzeiten links, Abdeckung rechts) | Platz am Laptop nutzen | ✅ erledigt | M |
| U6 | **Sync-Status** verständlicher: Punkt im Kopf antippbar mit „zuletzt gespeichert um …“ | Vertrauen in die Speicherung | ✅ erledigt | S |
| U7 | **Push-Erinnerungen** (Einheit des Tages, Readiness-Check, Protokoll offen) mit eigener Uhrzeit pro Erinnerung; Versand per GitHub Action im Datenrepo | Training nicht vergessen, ohne andere App | ✅ erledigt (16.11.) | M |

## 5. Technik und Wartung

| # | Idee | Nutzen | Prio | Aufwand |
|---|---|---|---|---|
| W1 | **CSS zusammenführen**: Die Gestaltung besteht aus mehreren übereinanderliegenden Schichten (Grundlayout, Design, Variante B, Red Tigers, Chrome Glass) mit vielen Überschreibungen und `!important`. Eine Schicht mit klaren Variablen | Änderungen am Design werden einfacher und sicherer | ✅ erledigt (15.11.: 44 Regeln und 236 Deklarationen entfernt, die überall überschrieben wurden; jede Ansicht und jeder Dialog in iPhone- und Laptop-Breite pixelgleich geprüft) | M |
| W2 | **Automatischer Klicktest** (Playwright) als GitHub Action: alle Ansichten in iPhone- und Laptop-Breite öffnen, jeden Button einmal antippen, Fehler melden – mit neutralen Testdaten | Fehler vor dem Ausrollen finden | ✅ erledigt | M |
| W3 | **Altfelder im Datenmodell prüfen** (z. B. `blocks`, `unavailable`, `suggestionDecisions` aus der alten Planverwaltung): was wird noch gebraucht, was kann per `migrate()` entfernt werden | Kleinere Datei, weniger Verwirrung | ✅ erledigt | M |
| W4 | **`index.html` aufteilen** (z. B. `css/`, `js/kern.js`, `js/training.js` …), weiterhin ohne Build-Schritt | Übersichtlicher bei weiterem Wachstum | ⏸ zurückgestellt: kein sichtbarer Nutzen, erhöht das Risiko beim Zwischenspeichern; sinnvoll erst bei deutlich mehr Code | M |
| W5 | **Cache-Version automatisch** aus dem Inhalt von `index.html` erzeugen (GitHub Action), damit das Erhöhen in `sw.js` nicht vergessen wird | Weniger Handarbeit | ✅ erledigt | S |
| W6 | **Token-Ablauf**: rechtzeitig vor Ablauf des GitHub-Tokens warnen | Kein plötzlicher Ausfall der Speicherung | ✅ erledigt | S |
| W7 | **Barrierefreiheit** prüfen (Kontraste der grauen Texte, Fokus-Rahmen, Beschriftungen der Icon-Buttons) | Bessere Lesbarkeit im Gym-Licht | ✅ erledigt | S |
| W8 | **Klicktest prüft den Abgleich** mit einem nachgebauten Datenrepo: lokale Eingabe übersteht einen älteren Stand mit Altfeldern, neuere Änderung eines anderen Geräts kommt an. Dabei behoben: neue Installation hatte keine Standard-Trainingsorte | Fehler wie der Ausstattungs-Verlust fallen vor dem Hochladen auf | ✅ erledigt | S |
