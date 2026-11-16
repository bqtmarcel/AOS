# Hinweise für Claude

- Dieses Repo ist **öffentlich** (GitHub Pages). Niemals persönliche Daten des Athleten hier ablegen: keine Körperwerte, Tests, Lasten, Startwerte, Trainingspläne, Ernährungs- oder Gesundheitsangaben, keine Spezifikationen mit solchen Werten. All das gehört ins private Repo `bqtmarcel/AOS_DATA`.
- `seedData()` in `index.html` bleibt neutral. Persönliche Startdaten liegen in `AOS_DATA/aos-data.json`.
- Datenformat der App: siehe `validateData`, `migrate`, `syncRecords` und `mergeData` in `index.html`. Schemaänderungen brauchen eine Migration in `migrate()`, damit bestehende Daten auf iPhone und Laptop erhalten bleiben.
- Nach jeder Änderung an `index.html` die Cache-Version in `sw.js` erhöhen: `./tools/bump-cache.sh` (die GitHub Action prüft das).
- Vor dem Hochladen den Klicktest laufen lassen: `python tests/smoke.py` (läuft auch automatisch als GitHub Action bei jedem Push).
- **Roadmap:** `ROADMAP.md` führt die Tasks für Mehrbenutzer, Positionsgruppen, Coach und Ranglisten. Jeden Task nach erfolgreichem Abschluss (umgesetzt und geprüft) im selben Commit abhaken: `[x]` und `✅ TT.MM.JJJJ` ans Ende, Zähler „Stand“ im Überblick aktualisieren. Neue oder geänderte Tasks dort eintragen. Keine persönlichen Werte in die Roadmap.
- Spezifikationen und Datenbanken (Sessionplaner, Nutrition, Übungen, Lebensmittel, Rezepte) liegen in `AOS_DATA/docs` und `AOS_DATA/db`.
