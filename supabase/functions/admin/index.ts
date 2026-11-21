// AOS · Admin-Funktion (Roadmap M4.1): Spieler per E-Mail einladen.
// Läuft bei Supabase (Edge Function). Prüft, dass der Aufrufer angemeldeter und aktiver Admin ist,
// und nutzt erst dann den geheimen Schlüssel (nur hier auf dem Server, nie in der App).
const URL = Deno.env.get('SUPABASE_URL')!;
const SECRET = Deno.env.get('AOS_SECRET_KEY') || Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
const APP = 'https://bqtmarcel.github.io/AOS/';
const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, apikey, content-type', 'Access-Control-Allow-Methods': 'POST, OPTIONS' };
const out = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
const srv = (path: string, init: RequestInit = {}) => fetch(URL + path, { ...init, headers: { apikey: SECRET, Authorization: 'Bearer ' + SECRET, 'Content-Type': 'application/json', ...(init.headers || {}) } });

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return out(200, { ok: true });
  if (req.method !== 'POST') return out(405, { error: 'Nur POST' });
  if (!SECRET) return out(500, { error: 'Server-Schlüssel fehlt (Action „Datenbank“ erneut starten)' });
  // Aufrufer prüfen
  const auth = req.headers.get('authorization') || '';
  const u = await fetch(URL + '/auth/v1/user', { headers: { apikey: req.headers.get('apikey') || SECRET, Authorization: auth } });
  if (!u.ok) return out(401, { error: 'Nicht angemeldet' });
  const me = await u.json();
  const pr = await srv('/rest/v1/profiles?select=roles,active&id=eq.' + me.id);
  const p = (await pr.json())[0];
  if (!p || !p.active || !(p.roles || []).includes('admin')) return out(403, { error: 'Nur für den Admin' });

  let body: { action?: string; email?: string; name?: string } = {};
  try { body = await req.json(); } catch { return out(400, { error: 'Ungültige Anfrage' }); }
  if (body.action === 'invite') {
    const email = String(body.email || '').trim().toLowerCase();
    const name = String(body.name || '').trim().slice(0, 80);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return out(400, { error: 'Ungültige E-Mail-Adresse' });
    const r = await srv('/auth/v1/invite?redirect_to=' + encodeURIComponent(APP), { method: 'POST', body: JSON.stringify({ email, data: { name } }) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) return out(r.status, { error: j.msg || j.message || j.error_description || ('Einladung fehlgeschlagen (HTTP ' + r.status + ')') });
    if (name) await srv('/rest/v1/profiles?id=eq.' + j.id, { method: 'PATCH', body: JSON.stringify({ name }) });
    return out(200, { ok: true, id: j.id, email });
  }
  if (body.action === 'resend') {   // Anmeldelink erneut schicken (z. B. Einladung abgelaufen)
    const email = String(body.email || '').trim().toLowerCase();
    const r = await srv('/auth/v1/otp?redirect_to=' + encodeURIComponent(APP), { method: 'POST', body: JSON.stringify({ email, create_user: false }) });
    if (!r.ok) { const j = await r.json().catch(() => ({})); return out(r.status, { error: j.msg || j.message || 'Senden fehlgeschlagen' }); }
    return out(200, { ok: true });
  }
  return out(400, { error: 'Unbekannte Aktion' });
});
