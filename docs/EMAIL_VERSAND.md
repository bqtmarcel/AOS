# Eigenen E-Mail-Versand einrichten (Roadmap M4.12)

Dauer: ca. 15 Minuten, am besten **am Laptop**. Kosten: keine.
Muss **vor dem Pilot (M4.9)** erledigt sein.

## Warum

Der eingebaute Versand von Supabase schickt Anmelde- und Einladungsmails nur an Mitglieder deiner Supabase-Organisation (also nur an dich) und höchstens 2 pro Stunde. Teamkollegen bekämen keine Mail. Mit einem eigenen Versand:

- erreichen Einladungen und Anmeldecodes jeden Spieler,
- steht in der Anmeldemail ein **6-stelliger Code** zum Eintippen in die App (`supabase/auth/magic_link.html`) – am iPhone viel einfacher als der Übergabecode,
- kommt die Einladung als eigene AOS-Mail (`supabase/auth/invite.html`),
- sind bis zu 60 Mails pro Stunde möglich.

Du trägst nur fünf GitHub-Secrets ein. Den Rest (Versand, Vorlagen, Limit) stellt die Action „Datenbank“ automatisch in Supabase ein. Im Supabase-Dashboard musst du nichts ändern.

## Welcher Anbieter?

| | **A: Gmail (empfohlen)** | B: Brevo |
|---|---|---|
| Voraussetzung | ein Google-Konto mit 2-Faktor-Anmeldung | eigene Domain des Vereins mit Zugriff auf die DNS-Einstellungen |
| Gratis-Limit | ca. 500 Mails pro Tag | 300 Mails pro Tag |
| Absender | die Gmail-Adresse | z. B. `aos@redtigers.at` |
| Aufwand | gering | mittel (DNS-Einträge SPF/DKIM) |

Für einen Kader von 50–70 Spielern reichen beide bei Weitem. **Empfehlung: eigenes Gmail-Konto nur für AOS**, z. B. `redtigers.aos@gmail.com`. So läuft der Versand nicht über dein privates Postfach, und das Konto kann später an jemand anderen im Verein übergeben werden.

---

## Weg A: Gmail

### 1. Gmail-Konto vorbereiten

1. Optional ein neues Google-Konto nur für AOS anlegen ([accounts.google.com](https://accounts.google.com) → Konto erstellen → Für meine private Nutzung).
2. **2-Faktor-Anmeldung einschalten:** [myaccount.google.com/security](https://myaccount.google.com/security) → **Bestätigung in zwei Schritten** → einrichten.

### 2. App-Passwort erzeugen

1. [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) öffnen (geht erst nach Schritt 1.2).
2. Name `AOS Supabase` → **Erstellen**.
3. Das **16-stellige Passwort** wird einmal angezeigt. **Nicht abtippen in einen Chat**, direkt in Schritt 3 eintragen (Leerzeichen weglassen).

### 3. Secrets im Repo `bqtmarcel/AOS` eintragen

[github.com/bqtmarcel/AOS](https://github.com/bqtmarcel/AOS) → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Name | Wert |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | die Gmail-Adresse, z. B. `redtigers.aos@gmail.com` |
| `SMTP_PASS` | das App-Passwort aus Schritt 2 (ohne Leerzeichen) |
| `SMTP_FROM` | dieselbe Gmail-Adresse |

Weiter mit **„Fertig: Action starten“** unten.

---

## Weg B: Brevo (nur mit eigener Vereinsdomain)

1. Konto auf [brevo.com](https://www.brevo.com) anlegen (Free-Plan, keine Kreditkarte).
2. **Senders, Domains & Dedicated IPs → Domains → Add a domain:** Vereinsdomain eintragen und die angezeigten DNS-Einträge (SPF, DKIM, DMARC) beim Domain-Anbieter des Vereins setzen. Warten, bis Brevo „Authenticated“ zeigt.
3. **Senders → Add a sender:** z. B. `aos@<vereinsdomain>`.
4. **SMTP & API → SMTP → Generate a new SMTP key.** Wichtig: ein **SMTP-Key**, kein API-Key.
5. Secrets wie oben, mit diesen Werten:

| Name | Wert |
|---|---|
| `SMTP_HOST` | `smtp-relay.brevo.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | der Login, den Brevo im Reiter SMTP anzeigt (endet auf `@smtp-brevo.com`) |
| `SMTP_PASS` | der SMTP-Key |
| `SMTP_FROM` | der Absender aus Schritt 3 |

---

## Fertig: Action starten

1. [github.com/bqtmarcel/AOS/actions](https://github.com/bqtmarcel/AOS/actions) → links **Datenbank** → **Run workflow** → **Run workflow**.
2. Nach 1–2 Minuten muss der Lauf grün sein. Im Schritt „E-Mail-Versand einstellen“ steht dann der Host und das Mail-Limit 60.

## Prüfen

1. In AOS abmelden (Profil → AOS-Konto → Abmelden) und mit deiner E-Mail neu anmelden.
2. Die Mail heißt jetzt **„Dein AOS-Code“** und enthält einen 6-stelligen Code. Code in der App eingeben → angemeldet.
3. Team → Verwaltung → eine zweite eigene Adresse (oder die eines Pilot-Athleten) einladen. Die Mail **„Einladung zu AOS“** muss ankommen. Landet sie im Spam: als „Kein Spam“ markieren und die Spieler beim Einladen darauf hinweisen.
4. Claude Bescheid geben: **„E-Mail-Versand fertig“**. Dann wird M4.12 abgehakt.

## Gut zu wissen

- **App-Passwort ungültig** (z. B. nach Änderung des Google-Passworts): neues App-Passwort erzeugen, Secret `SMTP_PASS` überschreiben, Action erneut starten.
- **Zurück zum Standardversand:** die fünf Secrets löschen und in Supabase unter Authentication → Emails → SMTP Settings „Enable custom SMTP“ ausschalten.
- Die geheimen Werte stehen nur in den GitHub-Secrets und in Supabase, nie im Code oder im Log.
