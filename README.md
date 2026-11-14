# AOS – Athlete Operating System

Persönliches Trainings- und Ernährungssystem für American Football als Web-App (PWA).
Läuft auf dem iPhone (über Safari „Zum Home-Bildschirm“) und im Browser am Laptop, auch offline.

## Aufbau

| Repo | Sichtbarkeit | Inhalt |
|---|---|---|
| `bqtmarcel/AOS` (dieses Repo) | öffentlich, GitHub Pages | App-Code: `index.html`, Service Worker, Manifest, Icons |
| `bqtmarcel/AOS_DATA` | **privat** | alle persönlichen Daten (`aos-data.json`), Datenbanken (`db/`), Spezifikationen (`docs/`) |

**In diesem Repo stehen keine persönlichen Daten** (keine Körperwerte, Tests, Lasten, Pläne, Ernährungsangaben).
Die App startet mit einem leeren, neutralen Stand und lädt alles Persönliche aus `AOS_DATA`.

## Speicherung und Abgleich

- Die App speichert jede Änderung sofort auf dem Gerät (localStorage) und gleicht sie nach wenigen Sekunden mit `aos-data.json` in `AOS_DATA` ab (GitHub Contents API, ein Commit pro Abgleich).
- Abgleich auch beim Start, beim Zurückkehren in die App und sobald wieder Netz da ist. Ohne Netz wird gepuffert.
- Zusammenführen pro Datensatz: Die jüngste Änderung gewinnt, Löschungen werden übertragen. Schreibkonflikte zwischen Geräten (HTTP 409) werden automatisch neu geladen, zusammengeführt und erneut geschrieben.
- Eine ungültige oder kaputte Datei im Datenrepo wird nie überschrieben.
- Zugriff über einen **Fine-grained Personal Access Token**, der nur `AOS_DATA` mit „Contents: Read and write“ darf. Der Token wird pro Gerät in der App eingetragen (Profil → Datenspeicherung), bleibt nur auf dem Gerät, steht in keiner Sicherung und wird nur an `api.github.com` gesendet (per Content-Security-Policy erzwungen).

## Entwicklung

Einzelne Datei `index.html` ohne Build-Schritt. Bei Änderungen an `index.html` die Cache-Version in `sw.js` erhöhen, sonst sehen installierte Apps die neue Version nicht.
