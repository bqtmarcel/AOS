"""Klicktest für AOS – läuft lokal und als GitHub Action.

Öffnet die App mit neutralen Testdaten und einem erfundenen Demo-Plan (ohne AOS-Konto) in iPhone- und Laptop-Breite,
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
  // M2: Richtwerte je Positionsgruppe und Wochenplan aus den Trainingstagen des Profils
  { const kp=clone(S.profile), kb=clone(S.bodyweight), kg=clone(S.goals);
    S.profile.positions=[{id:'t1',code:'WR',name:'Wide Receiver',weight:100}]; S.bodyweight=[{id:'tb',date:todayISO(),kg:80}]; S.goals=[];
    const g=stdGoals(); const sq=g.find(x=>x.name==='Kniebeuge'), bj=g.find(x=>x.name==='Broad Jump');
    const ok1 = sq && sq.target===120 && bj && bj.target===295;
    S.profile.positions=[{id:'t1',code:'RB',name:'Running Back',weight:70},{id:'t2',code:'DE',name:'Defensive End',weight:30}];
    const mix=groupMix().map(x=>x.group+x.share).join(',');
    S.profile.trainingDays=['THU','TUE']; const sc=JSON.stringify(schedFromDays(['D1','D2','D3','D4']));
    delete S.profile.trainingDays; const legacy=JSON.stringify(schedFromDays(['D1','D2','D3','D4']));
    S.profile=kp; S.bodyweight=kb; S.goals=kg;
    if(!ok1) return 'Richtwerte: WR-Werte falsch ('+JSON.stringify(g)+')';
    if(mix!=='RB70,DL30') return 'Positionsgruppen falsch gemischt ('+mix+')';
    if(sc!=='{"TUE":"D1","THU":"D2"}') return 'Trainingstage: Wochenplan falsch ('+sc+')';
    if(legacy!=='{"MON":"D1","WED":"D2","THU":"D3","FRI":"D4"}') return 'Bestehende Profile ohne Trainingstage bekommen einen anderen Wochenplan ('+legacy+')'; }
  // M3: Gruppenregeln (ohne Übungsdatenbank prüfbar; die Testprofile mit echter Datenbank laufen im Datenrepo)
  { const kp=clone(S.profile); const setP=(...a)=>{ S.profile.positions=a.map(([c,w],i)=>({id:'q'+i,code:c,name:c,weight:w})); };
    S.profile.experience='fortgeschritten'; S.profile.cleanSafe=true;
    setP(['QB',100]); let C=tpContext(); const qb=C.excl.has('bb_push_press') && C.excl.has('dips') && C.req.band_external_rotation===3;
    setP(['RB',70],['DE',30]); C=tpContext(); const rb=C.req.nordic_hamstring===2 && C.req.neck_plate_isometric===1 && C.req.carry_contact===1 && C.req.copenhagen_plank===1 && C.kf===1 && C.label==='RB 70 % / DL 30 %';
    setP(['WR',100]); C=tpContext(); const wr=C.setsDelta('main_squat','P3')===-1 && C.setsDelta('main_push','P3')===0;
    setP(['T',60],['WR',40]); C=tpContext(); const mix=C.setsDelta('main_squat','P3')===0 && C.setsDelta('main_squat','P2')===1;
    S.profile.experience='einsteiger'; S.profile.cleanSafe=false; setP(['DT',100]); C=tpContext(); const ein=C.excl.has('power_clean') && C.excl.has('hang_power_clean') && C.excl.has('depth_jump') && Math.abs(C.kf-0.5)<1e-9;
    S.profile.planEngine='klassisch'; const off=!apUseGroups({start:'2030-01-01'}); S.profile.planEngine='gruppen'; S.profile.planEngineSince='2030-01-01'; const since=!apUseGroups({start:'2029-12-01'}) && apUseGroups({start:'2030-01-06'});
    S.profile=kp;
    if(!qb) return 'Gruppenregeln QB falsch (Ausschlüsse/Pflicht)'; if(!rb) return 'Gruppenregeln RB 70 / DE 30 falsch';
    if(!wr) return 'WR: Sätze-Delta der Hauptübungen falsch'; if(!mix) return 'Mischung Sätze-Delta (OL 60 / WR 40) falsch';
    if(!ein) return 'Einsteiger/Umsetzen/DT: Ausschlüsse oder Kontaktfaktor falsch'; if(!off||!since) return 'Umstellung auf Positionsgruppen greift nicht wie vorgesehen'; }
  // Zeitbudget: zu volle Einheit wird auf höchstens 70 min gebracht, Grundübungen bleiben
  { const mk=(role,prio,method,sets,id)=>({ role, prio, method, sets, reps:'5', rest:[150,180], ex:REF.exMap[id], slot:{id}, slotId:id, reasons:[] });
    const it=[mk('power',1,'quality',4,'broad_jump'), mk('main',1,'wave',5,'high_bar_squat'), mk('main',1,'wave',5,'bench_press'), mk('main',1,'bodyweight_reps',5,'pull_up')]
      .concat(Array.from({length:8},(_,i)=>mk('assistance',3,'double',4,'bench_press')));
    const f=plFit(it, 70, 7, []); if(f.min>70) return 'Zeitbudget: Einheit dauert noch '+f.min+' min';
    if(!it.some(x=>x.ex.id==='high_bar_squat') || !it.some(x=>x.ex.id==='pull_up')) return 'Zeitbudget: Grundübung gestrichen'; }
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

async def supabase_test(browser):
    """Abgleich mit Supabase gegen eine nachgebaute Datenbank: Login per Code, Hochladen, Änderung eines anderen Geräts,
    älterer Stand überschreibt keinen neueren (wie der Trigger in der Datenbank)."""
    uid = '00000000-0000-4000-a000-0000000000aa'
    db = {}   # key -> {data, updated_at, deleted}
    other = '00000000-0000-4000-a000-0000000000bb'
    team = {'patched': [], 'invites': [], 'rank': {}, 'season': {'games': []}}
    sent = {'otp': 0}
    async def sbr(route):
        req = route.request; url = req.url; path = url.split('.supabase.co')[1]
        if path.startswith('/auth/v1/otp'):
            sent['otp'] += 1; return await route.fulfill(status=200, json={})
        if path.startswith('/auth/v1/verify'):
            b = json.loads(req.post_data)
            if b.get('token') != '123456': return await route.fulfill(status=403, json={'msg': 'Token has expired or is invalid'})
            return await route.fulfill(status=200, json={'access_token': 'tok', 'refresh_token': 'ref', 'expires_in': 3600, 'user': {'id': uid, 'email': b['email']}})
        if path.startswith('/auth/v1/token'):
            b = json.loads(req.post_data)
            if b.get('refresh_token') != 'uebergabe-abc12': return await route.fulfill(status=400, json={'msg': 'Invalid Refresh Token'})
            return await route.fulfill(status=200, json={'access_token': 'tok2', 'refresh_token': 'ref2', 'expires_in': 3600, 'user': {'id': uid, 'email': 'athlet@test.invalid'}})
        if path.startswith('/auth/v1/user'):
            return await route.fulfill(status=200, json={'id': uid, 'email': 'athlet@test.invalid'})
        if path.startswith('/rest/v1/records') and 'or=(' in path:   # Coach-Übersicht: Datensätze aller Athleten
            return await route.fulfill(status=200, json=[{'athlete_id': other, 'key': 'profile:_', 'data': {'name': 'Spieler B', 'positions': [{'id': 'x', 'code': 'WR', 'name': 'WR', 'weight': 100}]}, 'updated_at': '2026-11-01T00:00:00Z', 'deleted': False},
                                                          {'athlete_id': other, 'key': 'bodyweight:b1', 'data': {'id': 'b1', 'date': '2026-11-01', 'kg': 80}, 'updated_at': '2026-11-01T00:00:00Z', 'deleted': False}])
        if path.startswith('/rest/v1/records'):
            if req.method == 'GET':
                rows = [dict(key=k, **v) for k, v in sorted(db.items())]
                return await route.fulfill(status=200, json=rows)
            if req.method == 'POST':
                for r in json.loads(req.post_data):
                    if r['athlete_id'] != uid: return await route.fulfill(status=403, json={'message': 'row-level security'})
                    cur = db.get(r['key'])
                    if cur and cur['updated_at'] > r['updated_at']: continue   # jüngste Änderung gewinnt
                    db[r['key']] = {'data': r['data'], 'updated_at': r['updated_at'], 'deleted': r['deleted']}
                return await route.fulfill(status=201, body='')
        # Team: Rollen (Admin), Admin-Übersicht, Einladung, Rangliste, Teamkalender, Coach-Übersicht
        if path.startswith('/rest/v1/profiles') and 'select=roles' in path:
            return await route.fulfill(status=200, json=[{'roles': ['athlete', 'admin'], 'name': 'Admin', 'active': True}])
        if path.startswith('/rest/v1/profiles') and req.method == 'PATCH':
            team['patched'].append(json.loads(req.post_data)); return await route.fulfill(status=204, body='')
        if path.startswith('/rest/v1/profiles') and 'select=id,name' in path:
            return await route.fulfill(status=200, json=[{'id': uid, 'name': 'Admin', 'roles': ['athlete', 'admin'], 'active': True}, {'id': other, 'name': 'Spieler B', 'roles': ['athlete'], 'active': True}])
        if path.startswith('/rest/v1/rpc/admin_users'):
            return await route.fulfill(status=200, json=[{'id': uid, 'email': 'athlet@test.invalid', 'name': 'Admin', 'roles': ['athlete', 'admin'], 'active': True, 'last_sign_in_at': '2026-11-21T10:00:00Z'},
                                                          {'id': other, 'email': 'b@test.invalid', 'name': 'Spieler B', 'roles': ['athlete'], 'active': True, 'last_sign_in_at': None, 'invited_at': '2026-11-21T10:00:00Z'}])
        if path.startswith('/functions/v1/admin'):
            team['invites'].append(json.loads(req.post_data)); return await route.fulfill(status=200, json={'ok': True, 'id': 'neu'})
        if path.startswith('/rest/v1/rankings'):
            if req.method == 'POST':
                for r in json.loads(req.post_data): team['rank'][(r['athlete_id'], r['discipline'])] = r
                return await route.fulfill(status=201, body='')
            if req.method == 'DELETE': return await route.fulfill(status=204, body='')
            return await route.fulfill(status=200, json=list(team['rank'].values()) + [{'athlete_id': other, 'discipline': 'total', 'name': 'Spieler B', 'grp': 'WR', 'value': 400, 'score': 280}])
        if path.startswith('/rest/v1/team_season'):
            if req.method == 'PATCH': team['season'] = json.loads(req.post_data)['data']; return await route.fulfill(status=204, body='')
            return await route.fulfill(status=200, json=[{'data': team['season'], 'updated_at': '2026-11-21T10:00:00Z'}])
        if path.startswith('/rest/v1/'):
            return await route.fulfill(status=200, json=[])
        return await route.fulfill(status=404, json={})
    ctx = await browser.new_context(viewport={'width': 390, 'height': 900})
    await ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
    await ctx.route('https://*.supabase.co/**', sbr)
    page = await ctx.new_page(); errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    await page.goto(ROOT.as_uri()); await page.wait_for_timeout(600)
    # Login über die Oberfläche
    await page.evaluate("()=>{ ui.view='profil'; ui.profOpen={sb:true}; render(); }")
    await page.fill('#sb-email', 'athlet@test.invalid'); await page.click('[data-act="sbCode"]'); await page.wait_for_timeout(100)
    if sent['otp'] != 1: errors.append('Supabase: Code wurde nicht angefordert')
    await page.fill('#sb-otp', '000000'); await page.click('[data-act="sbVerify"]'); await page.wait_for_timeout(100)
    if await page.evaluate("sbReady()"): errors.append('Supabase: falscher Code wurde angenommen')
    await page.fill('#sb-otp', '123456'); await page.click('[data-act="sbVerify"]'); await page.wait_for_timeout(300)
    if not await page.evaluate("sbReady()"): errors.append('Supabase: Anmeldung mit richtigem Code klappt nicht'); await ctx.close(); return errors
    # Alles Lokale ist oben
    n_local = await page.evaluate("syncRecords(S).size")
    if len([k for k, v in db.items() if not v['deleted']]) < n_local: errors.append(f'Supabase: nicht alle Datensätze hochgeladen ({len(db)} von {n_local})')
    # Lokale Änderung wird hochgeladen
    await page.evaluate("async()=>{ S.profile.name='Test'; save(); await sbSync('test'); }")
    if (db.get('profile:_') or {}).get('data', {}).get('name') != 'Test': errors.append('Supabase: lokale Änderung kam nicht an')
    # Neuere Änderung eines anderen Geräts kommt an
    db['profile:_'] = {'data': dict(db['profile:_']['data'], name='anderes Gerät'), 'updated_at': '2099-01-01T00:00:00.000Z', 'deleted': False}
    if await page.evaluate("async()=>{ await sbSync('test'); return S.profile.name; }") != 'anderes Gerät':
        errors.append('Supabase: Änderung des anderen Geräts kam nicht an')
    # Löschung auf einem anderen Gerät wird übernommen
    k = next((k for k in db if k.startswith('cal:') or k.startswith('food:')), None)
    if k:
        db[k] = {'data': None, 'updated_at': '2099-01-01T00:00:00.000Z', 'deleted': True}
        gone = await page.evaluate("async k=>{ await sbSync('test'); return !syncRecords(S).has(k); }", k)
        if not gone: errors.append('Supabase: Löschung des anderen Geräts kam nicht an')
    # Übergabecode aus dem Browser (Link aus der Mail) in der App eingeben
    await page.evaluate("()=>{ sb.sess=null; sbStore(); ui.view='profil'; ui.profOpen={sb:true}; render(); }")
    await page.click('[data-act="sbHaveCode"]'); await page.fill('#sb-otp', 'uebergabe-abc12'); await page.click('[data-act="sbVerify"]'); await page.wait_for_timeout(300)
    if not await page.evaluate("sbReady() && sb.sess.access_token==='tok2'"): errors.append('Supabase: Anmeldung mit Übergabecode klappt nicht')
    # Link aus der Mail im Browser: zeigt den Übergabecode
    p2 = await ctx.new_page(); p2.on('pageerror', lambda e: errors.append(str(e)))
    await p2.goto(ROOT.as_uri() + '#access_token=x&refresh_token=handoff-xyz&expires_in=3600&type=magiclink'); await p2.wait_for_timeout(700)
    if 'handoff-xyz' not in (await p2.evaluate("(document.getElementById('dlg')||{}).textContent||''")): errors.append('Supabase: Link aus der Mail zeigt keinen Übergabecode')
    if '#access_token' in p2.url: errors.append('Supabase: Anmeldedaten bleiben in der Adresse stehen')
    await p2.close()
    # Team: Rollen, Rangliste, Coach-Übersicht, Admin, Teamkalender
    await page.evaluate("async()=>{ await teamMe(); ui.view='team'; render(); }"); await page.wait_for_timeout(200)
    if not await page.evaluate("isAdminUser() && document.querySelector('[data-view=\"team\"]')!=null"): errors.append('Team: Admin-Rolle bzw. Team-Ansicht fehlt')
    # Rangliste: DOTS gegen Referenzwert (100 kg, Männer, 600 kg Total ≈ 369,3), eigener Eintrag nur mit Zustimmung
    if abs(await page.evaluate("dots(600,100,'m')") - 369.3) > 0.2: errors.append('Rangliste: DOTS-Score weicht vom Referenzwert ab')
    await page.evaluate("async()=>{ S.profile.rankOptIn=false; save(); await rkPublish(); }")
    if team['rank']: errors.append('Rangliste: ohne Zustimmung wurde etwas eingetragen')
    await page.evaluate("async()=>{ S.profile.rankOptIn=true; S.profile.sex='m'; S.bodyweight.push({id:'rb',date:todayISO(),kg:90}); S.tests.push({id:'rt',name:'Broad Jump',value:280,unit:'cm',date:todayISO()}); save(); await rkPublish(); await rkLoad(); render(); }")
    if not any(k[1] == 'broad' and v['value'] == 280 and 'kg' not in json.dumps(v) for k, v in team['rank'].items()): errors.append('Rangliste: eigener Broad Jump nicht eingetragen')
    if any('bodyweight' in json.dumps(v) or v.get('value') == 90 for v in team['rank'].values()): errors.append('Rangliste: Körpergewicht wurde übertragen')
    if 'Spieler B' not in await page.evaluate("document.getElementById('main').textContent"): errors.append('Rangliste: andere Athleten werden nicht angezeigt')
    await page.evaluate("async()=>{ await teamLoadAthletes(); }")
    if not await page.evaluate("(TEAM.athletes||[]).some(a=>a.name==='Spieler B' && a.grp==='WR' && a.hints.length>0)"): errors.append('Coach: Athletenliste oder Hinweise fehlen')
    if await page.evaluate("S.profile.name") == 'Spieler B': errors.append('Coach: fremde Daten sind in den eigenen Bestand geraten')
    await page.evaluate("async()=>{ await adminLoad(); }")
    await page.fill('#ad-name', 'Neu'); await page.fill('#ad-mail', 'neu@test.invalid'); await page.click('[data-act="adInvite"]'); await page.wait_for_timeout(200)
    if not team['invites'] or team['invites'][0].get('email') != 'neu@test.invalid': errors.append('Admin: Einladung wurde nicht verschickt')
    await page.click('[data-act="adRole"][data-v="coach"][data-id="%s"]' % other); await page.wait_for_timeout(200)
    if not team['patched'] or 'coach' not in team['patched'][-1].get('roles', []): errors.append('Admin: Rolle Coach wurde nicht gesetzt')
    await page.fill('#tc-date', '2027-04-10'); await page.fill('#tc-title', 'Testgegner'); await page.click('[data-act="tcAdd"]'); await page.wait_for_timeout(300)
    if not any(g.get('date') == '2027-04-10' for g in team['season'].get('games', [])): errors.append('Teamkalender: Spiel wurde nicht gespeichert')
    # Abmelden: Daten bleiben auf dem Gerät
    await page.evaluate("()=>{ sb.sess=null; sbStore(); render(); }")
    if await page.evaluate("S.profile.name") != 'anderes Gerät': errors.append('Supabase: Daten nach dem Abmelden weg')
    # Gerätewechsel: anderer Athlet meldet sich an → lokale Daten des vorherigen Kontos verschwinden
    await page.evaluate("()=>{ sb.sess={access_token:'t',refresh_token:'r',expires_at:9e9,user:{id:'00000000-0000-4000-a000-0000000000cc'}}; sbOwnerCheck(); }")
    if await page.evaluate("S.profile.name") == 'anderes Gerät': errors.append('Gerätewechsel: Daten des vorherigen Kontos bleiben stehen')
    await ctx.close()
    return errors

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        failed = False
        errors = await supabase_test(browser)
        print(f'Supabase: {len(errors)} Fehler')
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
