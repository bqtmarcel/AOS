# Supabase einrichten (Roadmap 0.2)

Dauer: ca. 20 Minuten. Am besten **am Laptop** – einige Einstellungen gibt es in der GitHub-App am iPhone nicht.
Kosten: keine. Der Free-Plan reicht, eine Kreditkarte ist nicht nötig.

## Was geheim ist und was nicht

| Wert | Beispiel | Geheim? | Wohin |
|---|---|---|---|
| Projekt-URL | `https://abcdefgh.supabase.co` | nein | an Claude im Chat |
| Publishable key | `sb_publishable_…` | nein (gehört in die App) | an Claude im Chat |
| Datenbank-Passwort | – | **ja** | Passwort-Manager + GitHub-Secret |
| Secret key | `sb_secret_…` | **ja** | nur GitHub-Secret |
| Access Token | `sbp_…` | **ja** | nur GitHub-Secret |

**Die drei geheimen Werte nie in einen Chat, eine Datei oder eine Nachricht kopieren**, auch nicht an Claude. Sie kommen nur in die GitHub-Secrets (Schritte 7 und 8). Dort kann sie niemand mehr auslesen, auch nicht du selbst. Sollte einer davon doch einmal irgendwo landen: in Supabase einen neuen erzeugen und den alten löschen.

---

## 1. Konto anlegen

1. [supabase.com](https://supabase.com) öffnen → **Start your project**.
2. **Continue with GitHub** wählen und mit dem Konto `bqtmarcel` anmelden.
3. Organisation anlegen: Name z. B. `Red Tigers AOS`, Typ **Personal**, Plan **Free**.

## 2. Projekt erstellen

1. **New project**.
2. Ausfüllen:
   - **Project name:** `aos`
   - **Database Password:** auf **Generate a password** tippen und das Passwort **sofort im Passwort-Manager speichern** (z. B. iCloud-Schlüsselbund). Du brauchst es in Schritt 7.
   - **Region:** **Central EU (Frankfurt)** – wichtig für den Datenschutz.
   - Alle übrigen Einstellungen (z. B. Data API) so lassen, wie sie vorgeschlagen werden.
3. **Create new project**. Die Einrichtung dauert 1–2 Minuten.

## 3. Projekt-URL und Publishable key notieren

1. Links unten **Project Settings** (Zahnrad) → **API Keys**.
2. Steht dort ein Knopf **Create new API keys**: antippen.
3. Unter **Publishable key** den Wert `sb_publishable_…` kopieren.
4. Die **Projekt-URL** steht unter **Project Settings → Data API** (oder oben über den Knopf **Connect**): `https://<projekt-id>.supabase.co`.
   Der Teil `<projekt-id>` (ca. 20 Buchstaben) ist die **Project Ref** für Schritt 7.

Beides brauchst du am Ende (Schritt 9).

## 4. Login einstellen

1. Links **Authentication** → **URL Configuration**:
   - **Site URL:** die Adresse, unter der du AOS am iPhone öffnest (`https://bqtmarcel.github.io/AOS/`)
   - Unter **Redirect URLs** → **Add URL**: dieselbe Adresse mit `**` am Ende (`https://bqtmarcel.github.io/AOS/**`) → **Save**
2. **Authentication** → **Sign In / Providers**:
   - **Email** muss aktiviert sein (Standard).
   - **Allow new users to sign up** **ausschalten** → **Save**. Damit kann sich niemand selbst registrieren; Spieler kommen nur per Einladung hinein.

## 5. Dein eigenes Konto anlegen

1. **Authentication** → **Users** → **Add user** → **Create new user**.
2. Deine E-Mail-Adresse eintragen, ein beliebiges langes Passwort (wird nicht gebraucht, angemeldet wird später per Link aus der E-Mail).
3. **Auto Confirm User** anhaken → **Create user**.

Die Admin-Rolle bekommt dieses Konto automatisch beim Einrichten der Datenbank (Roadmap M1).

## 6. Access Token erzeugen

Damit kann GitHub später die Datenbankstruktur automatisch anlegen und ändern.

1. Oben rechts auf dein Profilbild → **Account preferences** → **Access Tokens**.
2. **Generate new token**, Name `AOS GitHub Actions`, längste mögliche Laufzeit.
3. Den Token `sbp_…` kopieren – er wird nur einmal angezeigt – und **direkt in Schritt 7 eintragen**.

## 7. Secrets im Repo `bqtmarcel/AOS` eintragen

1. [github.com/bqtmarcel/AOS](https://github.com/bqtmarcel/AOS) → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Drei Secrets anlegen (Name genau so schreiben):

| Name | Wert |
|---|---|
| `SUPABASE_ACCESS_TOKEN` | Token aus Schritt 6 (`sbp_…`) |
| `SUPABASE_DB_PASSWORD` | Datenbank-Passwort aus Schritt 2 |
| `SUPABASE_PROJECT_REF` | Project Ref aus Schritt 3 |

## 8. Secrets im Repo `bqtmarcel/AOS_DATA` eintragen

Für das wöchentliche Backup und die einmalige Übernahme deiner Daten.

1. In Supabase: **Project Settings** → **API Keys** → unter **Secret keys** den Schlüssel `sb_secret_…` aufdecken und kopieren.
2. [github.com/bqtmarcel/AOS_DATA](https://github.com/bqtmarcel/AOS_DATA) → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Name | Wert |
|---|---|
| `SUPABASE_URL` | Projekt-URL aus Schritt 3 |
| `SUPABASE_SECRET_KEY` | Secret key (`sb_secret_…`) |

## 9. Claude Bescheid geben

Im Chat schreiben: **„Supabase fertig“** plus

- Projekt-URL
- Publishable key

Mehr braucht Claude nicht. Damit ist Roadmap-Task 0.2 erledigt und M1 kann starten.

---

## Gut zu wissen

- **Pausieren:** Im Free-Plan pausiert Supabase ein Projekt nach 7 Tagen ohne Nutzung. Durch das tägliche Training und das wöchentliche Backup (Roadmap M1.8) passiert das nicht. Falls doch: im Dashboard **Resume project** – die Daten bleiben erhalten.
- **E-Mails für Einladungen:** Der eingebaute E-Mail-Versand von Supabase schickt Login-Links nur an Mitglieder deiner Supabase-Organisation (also nur an dich) und höchstens 2 pro Stunde. Für dich allein reicht das. Bevor Teamkollegen eingeladen werden, kommt ein eigener E-Mail-Anbieter dazu (Roadmap M4.12) – dafür gibt es dann eine eigene Anleitung.
