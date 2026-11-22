# AOS – Lebensmitteldatenbanken

Automatisch erzeugt von `.github/workflows/lebensmittel.yml` (Branch `main`), jede Woche neu. Nicht von Hand bearbeiten –
der Branch wird bei jedem Lauf komplett ersetzt.

| Datei | Inhalt | Quelle und Lizenz |
|---|---|---|
| `off.json.gz` | Markenprodukte, die in Österreich oder Deutschland verkauft werden (mit vollständigen Nährwerten) | Open Food Facts, Open Database License (ODbL) – openfoodfacts.org |
| `bls.json.gz` | Grundlebensmittel und Gerichte | Max Rubner-Institut (2025): Bundeslebensmittelschlüssel (BLS), Version 4.0 – Deutsche Nährstoffdatenbank. CC BY 4.0 |
| `ch.json.gz` | Grundlebensmittel | Schweizer Nährwertdatenbank, Bundesamt für Lebensmittelsicherheit und Veterinärwesen BLV – naehrwertdaten.ch |
| `index.json` | Stand, Anzahl und Prüfsumme je Datei | – |

Alle Werte pro 100 g bzw. 100 ml, gerundet. Spalte `chain` in `off.json.gz`: Handelskette (b Billa, p Penny, a ADEG, s Spar, h Hofer, l Lidl, m MPreis, u Unimarkt, d dm), erkannt über Kettenname oder eindeutige Eigenmarke. Die Daten wurden für AOS gekürzt (nur Energie und Makronährstoffe).
