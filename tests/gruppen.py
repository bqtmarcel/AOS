#!/usr/bin/env python3
"""Testprofile je Positionsgruppe (Roadmap M3.8) mit der echten Übungsdatenbank.

Aufruf:  python tests/gruppen.py <Pfad zu AOS_Uebungsdatenbank.json> [--html vergleich.html]
Die Datenbank liegt im privaten Datenrepo; der Test läuft dort als Action „Gruppentest“.
Geprüft wird je Profil über alle Phasen (P1–P5, Saison): vollständige Einheiten, Gruppenregeln
(Ausschlüsse, Pflichtübungen, Feldarbeit nur an Feldtagen, Sätze-Delta) und Modifikatoren (Einsteiger, Umsetzen, Körpergewicht).
Mit --html entsteht die Vergleichsansicht P2–P5 der Testprofile nebeneinander (M3.9). Keine persönlichen Werte."""
import asyncio, json, pathlib, sys, html as H
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = json.load(open(sys.argv[1], encoding='utf-8'))
OUT = sys.argv[sys.argv.index('--html') + 1] if '--html' in sys.argv else None

def pos(*a): return [{'id': 'p%d' % i, 'code': c, 'name': c, 'weight': w} for i, (c, w) in enumerate(a)]
PROFILE = [  # Name, Positionen, Optionen
    ('OL · Tackle, 128 kg, 3 Tage', pos(('T', 100)), {'kg': 128, 'days': ['MON', 'WED', 'FRI']}),
    ('DL · Defensive Tackle, 140 kg', pos(('DT', 100)), {'kg': 140, 'clean': True, 'exp': 'erfahren'}),
    ('LB 60 / TE 40, 3 Tage', pos(('MLB', 60), ('TE', 40)), {'days': ['MON', 'WED', 'FRI'], 'clean': True, 'exp': 'erfahren'}),
    ('TE · Tight End', pos(('TE', 100)), {'clean': True}),
    ('RB 70 / DE 30', pos(('RB', 70), ('DE', 30)), {'clean': True, 'exp': 'erfahren', 'kg': 92}),
    ('WR · Home Gym, Umsetzen unsicher', pos(('WR', 100)), {'kg': 80}),
    ('DB · Cornerback, Feld Mo/Do', pos(('CB', 100)), {'field': [1, 4], 'clean': True}),
    ('QB · Einsteiger, 2 Tage', pos(('QB', 100)), {'exp': 'einsteiger', 'days': ['TUE', 'FRI']}),
]
# Neutraler Saisonplan (Phasen wie im Sessionplaner, Daten frei gewählt)
PLAN = {'name': 'Testplan', 'version': 'TEST', 'season': {'first_game': ['2027-03-21']}, 'rules': {'pain_threshold': 3, 'max_session_min': 70, 'warmup_min': 10, 'leg_regions': ['knee']},
        'phases': [{'id': 'P1', 'name': 'P1', 'start': '2026-11-16', 'end': '2026-12-06'}, {'id': 'P2', 'name': 'P2', 'start': '2026-12-07', 'end': '2027-01-10'},
                   {'id': 'P3', 'name': 'P3', 'start': '2027-01-11', 'end': '2027-02-07'}, {'id': 'P4', 'name': 'P4', 'start': '2027-02-08', 'end': '2027-03-07'},
                   {'id': 'P5', 'name': 'P5', 'start': '2027-03-08', 'end': '2027-03-21'}], 'blocks': [], 'games': [{'date': '2027-04-10'}, {'date': '2027-05-01'}]}

JS = """([plan, ex, pos, opt])=>{
  S=freshData(); S.profile.positions=pos; S.profile.trainingDays=opt.days||['MON','TUE','THU','FRI'];
  if(opt.exp) S.profile.experience=opt.exp; if(opt.clean!=null) S.profile.cleanSafe=opt.clean;
  S.bodyweight=[{id:'b1',date:'2026-11-10',kg:opt.kg||90}];
  if(opt.field) S.profile.locations.forEach(l=>{ if(l.id==='loc-field') l.days=opt.field; });
  syncInit(); ensureProfileDefaults(); refSet(plan, ex, '', {nut:null,food:null,recipes:null});
  const C=tpContext(); const err=[]; const nm=id=>(REF.exMap[id]||{}).name_de||id;
  const blocks=REF.plan.blocks.map(b=>{ const wk=b.phase==='IN'?1:2;
    b.templates.forEach(t=>{ const sl=t.slots.filter(s=>(s.dose||{})[wk]);
      if(b.phase!=='IN' && sl.length<5) err.push(b.phase+' '+t.id+': nur '+sl.length+' Übungen');
      if(t.id!=='IN2' && !sl.some(s=>s.role==='main')) err.push(b.phase+' '+t.id+': keine Hauptübung');
      const ids=sl.map(s=>s.candidates[0]); if(new Set(ids).size<ids.length) err.push(b.phase+' '+t.id+': Übung doppelt');
      sl.forEach(s=>{ const id=s.candidates[0]; if(C.excl.has(id)) err.push(b.phase+' '+t.id+': ausgeschlossen '+id+' ('+C.why[id]+')');
        if(s.tp==='field'){ const d=Object.keys(b.week_schedule).find(k=>b.week_schedule[k]===t.id); if(!tpFieldDay(d)) err.push(b.phase+' '+t.id+': Feldarbeit ohne Feldtag'); } }); });
    if(b.phase!=='IN') Object.entries(C.req).forEach(([k,n])=>{ const have=b.templates.reduce((a,t)=>a+t.slots.filter(s=>(TP.slots[k]?s.tp===k:s.candidates[0]===k)).length,0);
      const max=b.templates.length; if(have<Math.min(n,max) && tpAllowed(C,k,b.phase)!==false && (TP.slots[k]||REF.exMap[k])) err.push(b.phase+': Pflicht '+k+' '+have+'/'+n); });
    return { phase:b.phase, label:b.groups, cap:b.rpe_cap[0], contacts:b.limits.contacts_per_session, notes:(b.week_notes[1]||[]).slice(-2),
      t:b.templates.map(t=>({ id:t.id, name:t.name, s:t.slots.filter(s=>(s.dose||{})[wk]).map(s=>({ n:nm(s.candidates[0]), d:(s.dose[wk]||[]).join('×'), role:s.role, grp:s.grp||'', p:!!s.pflicht, tp:s.tp||'' })) })) }; });
  return { err, blocks, kf:C.kf, label:C.label }; }"""

async def main():
    res = []
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto((ROOT / 'index.html').as_uri()); await pg.wait_for_timeout(300)
        for name, ps, opt in PROFILE:
            r = await pg.evaluate(JS, [json.loads(json.dumps(PLAN)), DB, ps, opt]); r['name'] = name; res.append(r)
        await b.close()
    bad = 0
    for r in res:
        e = r['err'] + []
        print(('OK  ' if not e else 'FEHLER ') + r['name'] + ' · Kontaktfaktor ' + str(round(r['kf'], 2)) + (' · ' + '; '.join(e) if e else ''))
        bad += len(e)
    # Gruppen müssen sich unterscheiden: O-Line und Cornerback in P4 nicht gleich
    def ex(name, ph):
        r = next(x for x in res if x['name'].startswith(name)); bl = next(x for x in r['blocks'] if x['phase'] == ph)
        return {s['n'] for t in bl['t'] for s in t['s']}
    ol, cb = ex('OL', 'P4'), ex('DB', 'P4'); same = len(ol & cb) / max(1, len(ol | cb))
    # Prüffälle aus den Trainingspfaden
    checks = [('Cornerback: Backpedal oder Press/Jam an Feldtagen (P4)', bool(cb & {'Backpedal mit Hüftdrehung und Sprint', 'Press/Jam aus der Coverage'})),
              ('QB: kein Überkopfdrücken', not (ex('QB', 'P4') & {'Push Press Langhantel', 'KH-Schulterdrücken stehend', 'Einarmiger KH Push Press', 'Dips'})),
              ('QB: Außenrotation in jeder Einheit (P2)', all(any(s['n'] == 'Außenrotation mit Band' for s in t['s']) for t in next(x for x in res if x['name'].startswith('QB'))['blocks'][1]['t'])),
              ('DT: keine Depth Jumps', not any('Depth' in n for P in ['P2', 'P3', 'P4'] for n in ex('DL', P))),
              ('WR (Umsetzen unsicher): kein Umsetzen', not any('Clean' in n and 'Pull' not in n for P in ['P2', 'P3', 'P4'] for n in ex('WR', P))),
              ('Einsteiger: kein Power Clean', not any(n == 'Power Clean vom Boden' for P in ['P2', 'P3', 'P4'] for n in ex('QB', P)))]
    for n, ok in checks: print(('OK  ' if ok else 'FEHLER ') + n); bad += not ok
    print('Überschneidung OL/CB in P4: %d %%' % round(same * 100)); bad += same > 0.6
    if errs: print('Seitenfehler:', errs); bad += 1
    if OUT: write_html(res, OUT); print('Vergleichsansicht:', OUT)
    print('Fehler:', bad); sys.exit(1 if bad else 0)

def write_html(res, path):
    ph = ['P2', 'P3', 'P4', 'P5']
    rows = []
    for P in ph:
        rows.append('<h2>' + P + '</h2><div class="grid">')
        for r in res:
            bl = next((x for x in r['blocks'] if x['phase'] == P), None)
            if not bl: continue
            c = '<section><h3>' + H.escape(r['name']) + '</h3><p class="m">' + H.escape(bl['label'] or '') + ' · RPE ≤ ' + str(bl['cap']) + ' · Kontakte ' + '–'.join(map(str, bl['contacts'])) + '</p>'
            for t in bl['t']:
                c += '<h4>' + t['id'] + ' ' + H.escape(t['name']) + '</h4><ul>' + ''.join(
                    '<li class="' + s['role'] + '">' + H.escape(s['n']) + ' <span>' + H.escape(s['d']) + '</span>' + (' <b>' + s['grp'] + '</b>' if s['grp'] else '') + (' <i>Pflicht</i>' if s['p'] else '') + '</li>' for s in t['s']) + '</ul>'
            rows.append(c + '</section>')
        rows.append('</div>')
    css = ('body{font:14px/1.4 -apple-system,system-ui,sans-serif;margin:16px;background:#16181b;color:#e6e6e6}h1{font-size:20px}h2{margin-top:28px;border-bottom:1px solid #333}'
           '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}section{background:#1f2226;border:1px solid #2c3035;border-radius:10px;padding:10px}'
           'h3{font-size:15px;margin:0 0 4px}h4{font-size:12px;margin:10px 0 2px;color:#aaa;text-transform:uppercase;letter-spacing:.04em}ul{margin:0;padding-left:16px}'
           'li span{color:#999}li.main{font-weight:600}li b{font-size:11px;color:#bbb;border:1px solid #555;border-radius:4px;padding:0 3px}li i{font-size:11px;color:#bbb}.m{color:#999;font-size:12px;margin:0}')
    open(path, 'w', encoding='utf-8').write('<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AOS · Positionsgruppen im Vergleich</title><style>' + css +
        '</style></head><body><h1>AOS · Positionsgruppen im Vergleich (Woche 2 je Phase)</h1><p class="m">Fett: Hauptübung · Kästchen: Slot aus der Nebengruppe · Pflicht: Pflichtübung der Gruppe. Testprofile ohne persönliche Werte.</p>' + ''.join(rows) + '</body></html>')

asyncio.run(main())
