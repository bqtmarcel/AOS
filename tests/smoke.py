"""Klicktest für AOS – läuft lokal und als GitHub Action.

Öffnet die App mit neutralen Testdaten und einem erfundenen Demo-Plan (ohne Datenrepo) in iPhone- und Laptop-Breite,
öffnet jede Ansicht, klappt alle Bereiche auf, tippt jeden Button einmal an und
meldet jeden JavaScript-Fehler. Keine persönlichen Daten, kein Netzzugriff.

Aufruf:  python tests/smoke.py [Pfad zu index.html]
"""
import asyncio, base64, json, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / 'index.html').resolve()
VIEWS = ['uebersicht', 'training', 'ernaehrung', 'tests', 'plan', 'profil']
SKIP = {'resetAll', 'exportJSON', 'csv', 'go', 'plReload', 'ghSyncNow', 'ghDisconnect', 'ghOpen'}

# Neutrale Beispieldaten: eine freie Einheit, zwei Gewichtsmessungen, ein Test

# Neutraler Demo-Plan (frei erfunden, keine persönlichen Werte). Startet am Montag der aktuellen Woche.
DEMO = """(()=>{
  const mon=mondayOf(todayISO()), end=addDays(mon,20);
  const ex=(id,name,pattern,role,eq,prog,cpr)=>({id,name_de:name,pattern,role,capabilities:[],equipment:eq,equipment_type:eq.length?'free_weight':'bodyweight',
    progression:prog,unilateral:false,contacts_per_rep:cpr,phases:['P1'],fatigue:'M',regions:[],substitutes:[],min_increment_kg:2.5,machine:false,selection_penalty:0,position_relevance:{},equipment_check:[]});
  const X={ name:'Demo-Übungen', exercises:[
    ex('high_bar_squat','Kniebeuge','squat','main',['barbell','rack'],['rpe_linear'],0),
    ex('bench_press','Bankdrücken','horizontal_push','main',['barbell','bench'],['rpe_linear'],0),
    ex('pull_up','Klimmzug','vertical_pull','main',[],['bodyweight_reps'],0),
    ex('broad_jump','Standweitsprung','jump','power',[],['quality'],1) ]};
  const dose={'1':[3,'5'],'2':[3,'5'],'3':[3,'5']};
  const P={ name:'Demo-Plan', version:'DEMO-1', season:{first_game:[addDays(mon,90)]}, rules:{pain_threshold:3,max_session_min:65,warmup_min:7,leg_regions:['knee'],increments_kg:{high_bar_squat:2.5,bench_press:2.5}},
    phases:[{id:'P1',name:'P1 Demo',start:mon,end,rpe_cap:[7,8]},{id:'P2',name:'P2 Demo (automatisch)',start:addDays(end,1),end:addDays(end,28),rpe_cap:[8,8]}],
    blocks:[{ id:'DEMO-B1', name:'Demo-Block', phase:'P1', start:mon, weeks:3, rpe_cap:[7,8], status:'bestätigt',
      week_wave:{'1':'Einstieg','2':'Aufbau','3':'Test'}, week_schedule:{MON:'A',WED:'B',FRI:'A'}, week_overrides:{}, session_order:['A','B'],
      limits:{contacts_per_session:[10,30],sprint_m_per_session:[0,0]}, week_notes:{}, start_loads:{high_bar_squat:60,bench_press:40},
      templates:[
        {id:'A',name:'Unterkörper',group:'lower',time_min:45,goal:'Demo',slots:[
          {id:'A-1',role:'power',prio:1,method:'quality',candidates:['broad_jump'],dose:{'1':[3,'3'],'2':[3,'3'],'3':[3,'3']},rest:[60,90]},
          {id:'A-2',role:'main',prio:1,method:'rpe_linear',candidates:['high_bar_squat'],dose,rest:[120,150],rpe:'≤ 8'}]},
        {id:'B',name:'Oberkörper',group:'upper',time_min:45,goal:'Demo',slots:[
          {id:'B-1',role:'main',prio:1,method:'wave',candidates:['bench_press'],dose,rpe_wave:{'1':7,'2':7.5,'3':8},rest:[120,150]},
          {id:'B-2',role:'main',prio:1,method:'bodyweight_reps',candidates:['pull_up'],dose,rest:[90,90]}]} ]}] };
  refSet(P, X, new Date().toISOString(), {nut:null,food:null,recipes:null});
  if(!REF.plan.blocks.some(b=>b.auto && b.templates.some(t=>t.slots.length))) throw new Error('Automatische Blockplanung hat keinen Block erzeugt');
})()"""


# Ablauf: Einheit aus dem Demo-Plan starten, Satz eintragen (Pausentimer), speichern
FLOW = """(async()=>{
  ui.view='training'; ui.sessionId=null; ui.draft=null; ui.pl=null; render();
  const n=plNextTraining(todayISO()); if(!n) return 'keine geplante Einheit';
  ui.pl.date=n.date; render();
  const c=document.querySelector('[data-act="plChip"][data-k="readiness"][data-v="4"]'); if(c) c.click();
  const t=document.querySelector('[data-act="plTake"]'); if(!t) return 'Start-Button fehlt';
  t.click(); await new Promise(r=>setTimeout(r,100));
  const i=document.querySelector('input[data-f="reps"]'); if(!i) return 'Eingabefeld fehlt';
  i.value='5'; i.dispatchEvent(new Event('input',{bubbles:true}));
  if(!document.getElementById('rest-bar')) return 'Pausentimer startet nicht';
  if(!document.querySelector('.last-perf')) return 'Hinweis „Letztes Mal“ fehlt';
  if(!ui.draft.startedAt || !document.querySelector('[data-clock]')) return 'Einheitsdauer läuft nicht';
  // Laufende Einheit bleibt beim Wechsel der Ansicht offen und ist auf dem Gerät gesichert
  const sid=ui.sessionId; document.querySelector('nav [data-view="tests"]').click();
  if(ui.sessionId!==sid || !document.querySelector('.live-bar')) return 'Laufende Einheit geht beim Wechsel der Ansicht verloren';
  if(!localStorage.getItem('aos-live-v1')) return 'Laufende Einheit nicht auf dem Gerät gesichert';
  document.querySelector('.live-bar').click(); if(!document.querySelector('[data-act="saveDraft"]')) return 'Zurück zur laufenden Einheit klappt nicht';
  ACT.saveDraft(); if(!sessionById(sid).draft) return 'Zwischenspeichern speichert nichts';
  document.querySelector('[data-act="saveLog"]').click(); document.querySelectorAll('.fin').forEach(x=>x.remove());
  if(document.getElementById('rest-bar')) return 'Pausentimer bleibt nach dem Speichern';
  const done=sessionById(sid); if(done.draft || !done.log || done.log.durationMin==null) return 'Dauer oder Zwischenstand nach dem Beenden falsch';
  if(localStorage.getItem('aos-live-v1')) return 'Laufende Einheit bleibt nach dem Beenden gespeichert';
  return 'ok';
})()"""

SEED = """(()=>{
  S.bodyweight.push({id:'t-bw1',date:'2026-01-05',kg:80,note:'',source:'eingabe'},{id:'t-bw2',date:'2026-01-12',kg:81,note:'',source:'eingabe'});
  S.tests.push({id:'t-t1',name:'Testsprung',category:'Sprung & Power',date:'2026-01-05',value:200,unit:'cm',conditions:''},
               {id:'t-t2',name:'Testsprung',category:'Sprung & Power',date:'2026-01-12',value:205,unit:'cm',conditions:''});
  ACT.logFree(); ui.draft.exercises=[{planExId:null,name:'Testübung',variant:'',metric:'kraft',
    sets:[{reps:5,kg:50,rpe:7,time:null,dist:null,height:null}],note:''}];
  ACT.saveLog({dataset:{st:'absolviert'}}); document.querySelectorAll('.fin').forEach(x=>x.remove());
  ui.sessionId=null; ui.draft=null; render();
})()"""

async def run(browser, width):
    ctx = await browser.new_context(viewport={'width': width, 'height': 900})
    await ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
    page = await ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    await page.goto(ROOT.as_uri())
    await page.wait_for_timeout(800)
    await page.evaluate(DEMO)
    await page.evaluate(SEED)
    clicks = 0
    for v in VIEWS:
        await page.evaluate("v=>{ui.view=v;ui.sessionId=null;ui.draft=null;render()}", v)
        acts = await page.evaluate("()=>{document.querySelectorAll('#main details').forEach(d=>d.open=true);return [...document.querySelectorAll('#main [data-act]')].map(e=>e.dataset.act)}")
        for i, a in enumerate(acts):
            if a in SKIP:
                continue
            await page.evaluate("""([v,i])=>{ if(ui.view!==v){ui.view=v;ui.sessionId=null;ui.draft=null;render();}
                document.querySelectorAll('#main details').forEach(d=>d.open=true);
                const e=[...document.querySelectorAll('#main [data-act]')][i]; if(e) e.click(); }""", [v, i])
            clicks += 1
            await page.wait_for_timeout(20)
            await page.evaluate("()=>{const d=document.getElementById('dlg'); if(d&&d.open) d.close(); document.querySelectorAll('.fin').forEach(x=>x.remove());}")
    r = await page.evaluate(FLOW)
    if r != 'ok':
        errors.append('Ablauf Training: ' + str(r))
    await ctx.close()
    return clicks, errors

# Abgleich mit dem Datenrepo gegen ein nachgebautes GitHub (nur im Test, kein Netz):
# 1. Eine lokale Eingabe muss den Abgleich mit einem älteren, noch nicht bereinigten Stand (Altfelder) überstehen.
# 2. Eine neuere Änderung von einem anderen Gerät muss lokal ankommen.
async def sync_test(browser):
    remote = {'text': None, 'sha': 0}
    async def gh(route):
        req = route.request; url = req.url
        if '/branches/' in url:
            return await route.fulfill(status=200, json={'name': 'main'})
        if req.method == 'GET':
            if remote['text'] is None:
                return await route.fulfill(status=404, json={'message': 'Not Found'})
            return await route.fulfill(status=200, json={'content': base64.b64encode(remote['text'].encode()).decode(), 'encoding': 'base64', 'sha': str(remote['sha'])})
        if req.method == 'PUT':
            body = json.loads(req.post_data)
            if remote['text'] is not None and body.get('sha') != str(remote['sha']):
                return await route.fulfill(status=409, json={'message': 'conflict'})
            remote['text'] = base64.b64decode(body['content']).decode(); remote['sha'] += 1
            return await route.fulfill(status=200, json={'content': {'sha': str(remote['sha'])}})
        return await route.fulfill(status=405, json={})
    ctx = await browser.new_context(viewport={'width': 390, 'height': 900})
    await ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
    await ctx.route('https://api.github.com/**', gh)
    page = await ctx.new_page(); errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    await page.add_init_script("localStorage.setItem('aos-github-v1', JSON.stringify({cfg:{owner:'demo',repo:'demo',branch:'main',path:'aos-data.json',token:'demo'}}))")
    await page.goto(ROOT.as_uri()); await page.wait_for_timeout(800)
    # Älterer Stand im Datenrepo, wie ihn ein Gerät mit alter App-Version geschrieben hätte
    old = json.loads(await page.evaluate("JSON.stringify(S)"))
    old['profile']['sex'] = 'x'; old['profile']['positionHistory'] = []
    for l in old['profile']['locations']: l['equipment'] = ['Langhantel']
    old['unavailable'] = ['2026-01-07']
    remote['text'] = json.dumps(old); remote['sha'] = 1
    loc = await page.evaluate("S.profile.locations[0].id")
    r = await page.evaluate("""async id=>{ await new Promise(r=>setTimeout(r,50));
        const t=document.createElement('textarea'); t.id='loc-t-'+id; t.value='Langhantel, Rack, keine Sprünge'; document.body.appendChild(t);
        CHG.locSave({dataset:{id}}); t.remove(); await ghSync('test'); return locById(id).text; }""", loc)
    if r != 'Langhantel, Rack, keine Sprünge':
        errors.append('Abgleich: lokale Eingabe ging verloren (' + repr(r) + ')')
    R = json.loads(remote['text'])
    if R['profile']['locations'][0].get('text') != 'Langhantel, Rack, keine Sprünge':
        errors.append('Abgleich: lokale Eingabe kam nicht im Datenrepo an')
    if 'equipment' in R['profile']['locations'][0] or 'sex' in R['profile'] or R.get('unavailable'):
        errors.append('Abgleich: Altfelder stehen noch im Datenrepo')
    # Neuere Änderung von einem anderen Gerät
    R['profile']['locations'][0]['text'] = 'anderes Gerät'
    R['sync']['stamps']['profile:_'] = '2099-01-01T00:00:00.000Z'
    remote['text'] = json.dumps(R); remote['sha'] += 1
    r = await page.evaluate("async id=>{ await ghSync('test'); return locById(id).text; }", loc)
    if r != 'anderes Gerät':
        errors.append('Abgleich: neuere Änderung des anderen Geräts kam nicht an (' + repr(r) + ')')
    await ctx.close()
    return errors

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        failed = False
        errors = await sync_test(browser)
        print(f'Abgleich: {len(errors)} Fehler')
        for e in errors:
            print('  FEHLER:', e)
        failed |= bool(errors)
        for w, name in [(390, 'iPhone'), (1280, 'Laptop')]:
            clicks, errors = await run(browser, w)
            print(f'{name}: {clicks} Klicks, {len(errors)} Fehler')
            for e in errors:
                print('  FEHLER:', e)
            failed |= bool(errors)
        await browser.close()
    sys.exit(1 if failed else 0)

asyncio.run(main())
