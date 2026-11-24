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
SKIP = {'resetAll', 'exportJSON', 'csv', 'go', 'plReload'}

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
  const P={ name:'Demo-Plan', version:'DEMO-1', season:{first_game:[addDays(mon,90)]}, rules:{pain_threshold:3,max_session_min:65,warmup_min:7,leg_regions:['knee'],increments_kg:{high_bar_squat:2.5,bench_press:2.5},
      gelernte_muster:{R1_aufwaermen:{aktiv:true,allgemein:{uebungen:2,saetze:2,dauer_s:40,pool:['Jumping Jacks','High Knees']},spezifisch:{uebungen:[2,3],saetze:3,wdh:6,pool_unten:['broad_jump'],pool_oben:['pull_up']},sprungkontakte_max:15},
        R2_topsatz_backoff:{aktiv:true,ab_phase:'P2',wochen:['build_heavy','peak','peak_test'],backoff_prozent_vom_topsatz:[88,95]},R3_pausen_nutzen:{aktiv:true},R4_kontrastpaare:{aktiv:true,phasen:['P1','P2'],readiness_min:3,runden:[3,5],pause_dazwischen_s:[20,60]},
        R5_speed_strength:{aktiv:true},R6_teil_rom:{aktiv:true},R7_feld_drills:{aktiv:true,testwoche:['10 yd']},R8_emom:{aktiv:true,intervall_s:120},R9_finisher:{aktiv:true,prio:3,durchgaenge:[2,3],strecke_m:20,pause_s:45,pool:['broad_jump']}}},
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
  // T19/T20/U8: Gesamtbelastung, Spielwoche, Wochenrückblick
  { const kf=clone(S.fieldLogs||[]), kc=clone(S.calendar||[]); const t=todayISO();
    let d=null; for(let i=0;i<21 && !d;i++){ const x=addDays(t,i); const due=plDue(x); if(due.tpl==='A' && !due.offday) d=x; }
    if(!d) return 'Testdatum für Spielwoche fehlt';
    // Belastung: 3 ruhige Wochen, dann eine harte → nächste Einheit wird entlastet
    S.fieldLogs=[]; for(let w=1; w<=4; w++) for(const k of [1,3,5]) S.fieldLogs.push({ id:'l'+w+k, date:addDays(d,-(w*7)+k), status:'absolviert', rpe:w===1?9:5, durationMin:w===1?120:60, contact:'leicht' });
    const LR=loadRatio(d); if(!LR || !(LR.ratio>1.3)) return 'Gesamtbelastung: Anstieg nicht erkannt ('+JSON.stringify(LR)+')';
    let P=plBuild({ date:d, tpl:'A', readiness:4 }); if(!P.notes.some(n=>/Belastung der letzten 7 Tage/.test(n))) return 'Gesamtbelastung: keine Entlastung in der Einheit';
    S.fieldLogs=[];
    // Vortag Spiel: nur Aktivierung (Power), keine Hauptübung
    S.calendar=(S.calendar||[]).concat([{ id:'g1', kind:'game', date:addDays(d,1), title:'Test' }]);
    P=plBuild({ date:d, tpl:'A', readiness:4 }); if(P.items.some(x=>x.role==='main') || !P.notes.some(n=>/Morgen Spiel/.test(n))) return 'Spielwoche: Vortag nicht nur Aktivierung';
    // Tag nach dem Spiel mit Beschwerden: Regeneration, Beschwerden wirken wie Check-in
    S.calendar=kc.concat([{ id:'g2', kind:'game', date:addDays(d,-1), title:'Test' }]);
    S.fieldLogs=[{ id:'gl', kind:'game', date:addDays(d,-1), status:'absolviert', rpe:9, snaps:60, contact:'hoch', pain:5, regions:['knee'], durationMin:150 }];
    P=plBuild({ date:d, tpl:'A', readiness:4 }); if(P.items.some(x=>x.role==='main'||x.role==='power') || !P.notes.some(n=>/Beschwerden aus dem Spiel/.test(n))) return 'Spielwoche: Tag danach nicht als Regeneration geplant';
    if(fieldLog(addDays(d,-1))) return 'Spiel-Eintrag wird als Feldtraining gelesen';
    S.fieldLogs=kf; S.calendar=kc;
    const R=weekReview(mondayOf(t)); if(!R || R.week!==mondayOf(t) || typeof R.planned!=='number' || !('next' in R)) return 'Wochenrückblick fehlt';
    if(!(S.push.on.weekly===true && S.push.hours.weekly===19)) return 'Wochenrückblick: Standard-Einstellung fehlt'; }
  // M3: Gruppenregeln (ohne Übungsdatenbank prüfbar; die Testprofile mit echter Datenbank laufen im Datenrepo)
  { const kp=clone(S.profile); const setP=(...a)=>{ S.profile.positions=a.map(([c,w],i)=>({id:'q'+i,code:c,name:c,weight:w})); };
    S.profile.experience='fortgeschritten'; S.profile.cleanSafe=true; S.profile.injuries=[]; S.profile.mobility={}; S.profile.birthYear=null; S.profile.extLoad=false; S.profile.weightGoal='halten'; S.profile.heightCm=null; const kbw=clone(S.bodyweight); S.bodyweight=[];
    setP(['QB',100]); let C=tpContext(); const qb=C.excl.has('bb_push_press') && C.excl.has('dips') && C.req.band_external_rotation===3;
    setP(['RB',70],['DE',30]); C=tpContext(); const rb=C.req.nordic_hamstring===2 && C.req.neck_plate_isometric===1 && C.req.carry_contact===1 && C.req.copenhagen_plank===1 && C.kf===1 && C.label==='RB 70 % / DL 30 %'; const rbInfo=JSON.stringify({req:C.req,kf:C.kf,label:C.label,age:C.age,by:S.profile.birthYear,bw:bwNow()});
    setP(['WR',100]); C=tpContext(); const wr=C.setsDelta('main_squat','P3')===-1 && C.setsDelta('main_push','P3')===0;
    setP(['T',60],['WR',40]); C=tpContext(); const mix=C.setsDelta('main_squat','P3')===0 && C.setsDelta('main_squat','P2')===1;
    S.profile.experience='einsteiger'; S.profile.cleanSafe=false; setP(['DT',100]); C=tpContext(); const ein=C.excl.has('power_clean') && C.excl.has('hang_power_clean') && C.excl.has('depth_jump') && Math.abs(C.kf-0.5)<1e-9;
    S.profile.planEngine='klassisch'; const off=!apUseGroups({start:'2030-01-01'}); S.profile.planEngine='gruppen'; S.profile.planEngineSince='2030-01-01'; const since=!apUseGroups({start:'2029-12-01'}) && apUseGroups({start:'2030-01-06'});
    S.profile=kp; S.bodyweight=kbw;
    if(!qb) return 'Gruppenregeln QB falsch (Ausschlüsse/Pflicht)'; if(!rb) return 'Gruppenregeln RB 70 / DE 30 falsch '+rbInfo;
    if(!wr) return 'WR: Sätze-Delta der Hauptübungen falsch'; if(!mix) return 'Mischung Sätze-Delta (OL 60 / WR 40) falsch';
    if(!ein) return 'Einsteiger/Umsetzen/DT: Ausschlüsse oder Kontaktfaktor falsch'; if(!off||!since) return 'Umstellung auf Positionsgruppen greift nicht wie vorgesehen'; }
  // M4.5: Einstiegsstufe aus der Standortbestimmung und Einstiegswochen parallel zum Teamkalender
  { const f='fortgeschritten';
    const st=[entryStage({w8:'6-8',last:'kurz',lifts:'ja'},f,false), entryStage({w8:'6-8',last:'kurz',lifts:'ja'},f,true), entryStage({w8:'3-5',last:'kurz',lifts:'ja'},f,false),
              entryStage({w8:'6-8',last:'kurz',lifts:'ja'},'einsteiger',false), entryStage({w8:'0-2',last:'kurz',lifts:'ja'},f,false), entryStage({w8:'3-5',last:'mittel',lifts:'teilweise'},f,true)].join('');
    if(st!=='322111') return 'Einstiegsstufen falsch ('+st+', erwartet 322111)';
    const kp=clone(S.profile); const P2=REF.plan.phases.find(p=>p.id==='P2'); const weeks=Math.max(1, Math.round((daysBetween(P2.start,P2.end)+1)/7)); const types=apWeekTypes('P2',P2.start,weeks);
    const blk=()=>REF.plan.blocks.find(b=>b.id==='AUTO-P2'); const wave=b=>b.templates.flatMap(t=>t.slots).find(s=>s.method==='wave');
    S.profile.entry={ stage:3, start:P2.start }; apReplan(); let b=blk(); if(!b) return 'Einstieg: Block P2 fehlt';
    const team1=b.week_wave[1], sets3=wave(b).dose[1][0], tw3=JSON.stringify(b.test_weeks);
    S.profile.entry={ stage:1, start:P2.start }; apReplan(); b=blk(); const w=wave(b);
    if(team1!==AP_WAVE_LABEL[types[0]]) return 'Stufe 3: erste Woche weicht vom Teamplan ab ('+team1+')';
    if(b.week_wave[1]!=='Dein Einstieg 1/2' || b.week_wave[2]!=='Dein Einstieg 2/2') return 'Stufe 1: Einstiegswochen fehlen ('+JSON.stringify(b.week_wave)+')';
    if(!(w.rpe_wave[1]<=7 && w.rpe_wave[2]<=7) || w.dose[1][0]>sets3) return 'Stufe 1: Dosierung/RPE im Einstieg zu hoch ('+JSON.stringify({rw:w.rpe_wave,d:w.dose[1],sets3})+')';
    if(!b.test_weeks.includes(2) || b.week_wave[3]!==AP_WAVE_LABEL[types[2]]) return 'Stufe 1: Eingangstests oder Rückkehr in den Teamplan falsch ('+JSON.stringify(b.test_weeks)+' / '+tw3+')';
    const di=types.findIndex(t=>t==='D'||t==='DT');
    if(di>=0){ S.profile.entry={ stage:2, start:addDays(P2.start,di*7) }; apReplan(); b=blk(); if(!/zählt als dein Einstieg/.test(b.week_wave[di+1])) return 'Stufe 2: Team-Entlastung zählt nicht als Einstieg'; }
    S.profile=kp; apReplan(); }
  // Ausgefallene Einheit: die offenen rücken der Reihe nach auf (Mo frei → Mi D1, Do D2, Fr D3)
  { const mon=addDays(mondayOf(todayISO()),7); const kd=clone(S.suggestionDecisions||{});
    const b={ id:'AUFR', start:mon, weeks:1, session_order:['D1','D2','D3','D4'], week_schedule:{MON:'D1',WED:'D2',THU:'D3',FRI:'D4'}, templates:['D1','D2','D3','D4'].map(id=>({ id, group:'full', slots:[] })) };
    const lbl=()=>plWeekPlan(b,1).upcoming.map(u=>WD_LONG[weekdayOf(u.date)].slice(0,2)+u.tpl).join(' ');
    if(lbl()!=='MoD1 MiD2 DoD3 FrD4') return 'Aufrücken: Normalwoche falsch ('+lbl()+')';
    S.suggestionDecisions=Object.assign({}, kd, { ['sched|'+mon]:{ status:'geändert', tpl:null } });
    const got=lbl(); S.suggestionDecisions=kd;
    if(got!=='MiD1 DoD2 FrD3') return 'Aufrücken: nach abgesagtem Montag falsch ('+got+')'; }
  // M4.2: Onboarding für neue Athleten
  { const kp=clone(S.profile), kt=clone(S.tests), kb=clone(S.bodyweight), kv=ui.view;
    S.profile.positions=[]; delete S.profile.onboarded; delete S.profile.entry; ACT.obOpen(); if(!document.getElementById('onboarding')) return 'Onboarding erscheint nicht';
    const setv=(id,v)=>{ const e=document.getElementById(id); if(!e) throw new Error('Feld '+id+' fehlt'); e.value=v; };
    ACT.obNext(); if(ui.ob.step!==1) return 'Onboarding: Willkommen → Position klappt nicht';
    ACT.obNext(); if(ui.ob.step!==1) return 'Onboarding: ohne Position weiter möglich';
    setv('ob-main','RB'); CHG.obPos(); setv('ob-sec','DE'); CHG.obPos(); ACT.obNext();
    setv('ob-h','180'); setv('ob-kg','90'); setv('ob-by','2000'); ACT.obSet({dataset:{v:'sex:m'}}); ACT.obNext(); if(ui.ob.step!==3) return 'Onboarding: Körperdaten nicht übernommen';
    ACT.obSet({dataset:{v:'clean:1'}}); ACT.obNext();
    ['w8:6-8','last:kurz','lifts:ja'].forEach(v=>ACT.obSet({dataset:{v}})); setv('ob-sq-kg','100'); setv('ob-sq-r','5'); setv('ob-sq-rpe','8'); ACT.obNext(); if(ui.ob.step!==5) return 'Onboarding: Trainingsstand nicht übernommen';
    ACT.obSet({dataset:{v:'loc:home'}}); setv('ob-loctext','Langhantel, Rack, Kurzhanteln, Bank'); ACT.obNext(); ACT.obNext(); ACT.obPain({dataset:{v:'knie'}}); ACT.obNext();
    if(ui.ob.step!==8 || !document.getElementById('onboarding').textContent.includes('Kurzer Einstieg')) return 'Onboarding: Zusammenfassung/Einstiegsstufe falsch';
    ACT.obFinish(); const p=S.profile; const tst=S.tests.find(t=>t.source==='selbstangabe');
    const ok=!ui.ob && p.onboarded && p.positions.map(x=>x.code+x.weight).join()==='RB70,DE30' && p.entry.stage===2 && p.heightCm===180 && p.planEngine==='gruppen'
      && tst && tst.value===95 && (p.locations.find(l=>l.id==='loc-own')||{}).text.includes('Rack') && S.bodyweight.some(x=>x.kg===90) && !document.getElementById('onboarding');
    const info=JSON.stringify({ ob:!!ui.ob, pos:p.positions, entry:p.entry, tst });
    S.profile=kp; S.tests=kt; S.bodyweight=kb; ui.view=kv; apReplan(); render();
    if(!ok) return 'Onboarding: Profil nicht vollständig übernommen '+info; }
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
    # Vorschau der kommenden Einheiten: rechnet ohne Fehler und speichert nichts
    pv = await page.evaluate("""()=>{ const n=S.sessions.length; const W=weekUpcoming(todayISO()); const h=weekPreview(todayISO());
        return { has:!!W, n:W?W.L.length:0, err:h.includes('Vorschau nicht möglich'), rows:(h.match(/<tr>/g)||[]).length, same:S.sessions.length===n }; }""")
    if not pv['has']: errors.append('Vorschau: keine kommenden Einheiten gefunden')
    elif pv['err'] or pv['rows'] == 0: errors.append('Vorschau: Einheiten ohne Übungen')
    if not pv['same']: errors.append('Vorschau: hat Einheiten gespeichert')
    # Freie, erledigte Einheit an einem geplanten Tag zählt als erledigt, nicht als verpasst
    fr = await page.evaluate("""()=>{ const t=todayISO(); const b=plBlockAt(t); if(!b) return 'kein Block';
        let d=null; for(let i=-13;i<14;i++){ const x=addDays(t,i); if(x<b.start||x>addDays(b.start,b.weeks*7-1)||x===t) continue; if(plScheduledAt(b,x).tpl && !plSessions().some(s=>sessionDate(s)===x)){ d=x; break; } }
        if(!d) return 'ohne geplanten Tag nicht prüfbar';
        S.sessions.push({ id:'free-t', name:'Freie Einheit Test', status:'absolviert', plannedDate:d, createdAt:new Date().toISOString(), plan:[], log:{ exercises:[] } });
        ui.ob=null; ui.cob=null; ui.sessionId=null; ui.draft=null; ui.view='plan'; ui.planBlock=b.id; render(); const ok=!!document.querySelector('#main [data-act="startLog"][data-id="free-t"]');
        S.sessions=S.sessions.filter(s=>s.id!=='free-t'); render(); return ok?'ok':'als verpasst angezeigt'; }""")
    if fr != 'ok': errors.append('Plan: freie Einheit ' + fr)
    # AOS im Kopf: am Laptop zur Übersicht, am Handy ohne Funktion
    hm = await page.evaluate("()=>{ ui.ob=null; ui.cob=null; ui.sessionId=null; ui.draft=null; ui.view='plan'; render(); document.getElementById('brand').click(); return ui.view; }")
    if width >= 761 and hm != 'uebersicht': errors.append('Kopf: AOS führt nicht zur Übersicht')
    if width < 761 and hm != 'plan': errors.append('Kopf: AOS reagiert am Handy')
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
    team = {'patched': [], 'invites': [], 'rank': {}, 'season': {'games': []}, 'roles': ['athlete', 'admin']}
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
            return await route.fulfill(status=200, json=[{'roles': team['roles'], 'name': 'Admin', 'active': True}])
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
    # Neues Konto ohne Position: Onboarding erscheint nach dem Login (M4.2), „Später einrichten“ führt zurück
    if not await page.evaluate("!!document.getElementById('onboarding')"): errors.append('Supabase: Onboarding erscheint nach dem ersten Login nicht')
    await page.evaluate("()=>{ ACT.obLater(); ui.view='profil'; render(); }")
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
    # Zurück zum ersten Konto: sein Stand ist wieder da
    await page.evaluate("()=>{ sb.sess.user.id='%s'; sbOwnerCheck(); }" % uid)
    if await page.evaluate("S.profile.name") != 'anderes Gerät': errors.append('Gerätewechsel: Stand des ersten Kontos kommt nicht zurück')
    await ctx.close()
    # Zweites Gerät (Laptop) mit eingerichtetem Konto: kein Onboarding, Profil kommt aus Supabase
    db['profile:_'] = {'data': dict(db['profile:_']['data'], name='Eingerichtet', positions=[{'id': 'p1', 'code': 'RB', 'name': 'Running Back', 'weight': 100}]), 'updated_at': '2099-01-02T00:00:00.000Z', 'deleted': False}
    ctx = await browser.new_context(viewport={'width': 1280, 'height': 900})
    await ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
    await ctx.route('https://*.supabase.co/**', sbr)
    page = await ctx.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
    await page.goto(ROOT.as_uri()); await page.wait_for_timeout(600)
    await page.evaluate("()=>{ ui.view='profil'; ui.profOpen={sb:true}; render(); }")
    await page.fill('#sb-email', 'athlet@test.invalid'); await page.click('[data-act="sbCode"]'); await page.wait_for_timeout(100)
    await page.fill('#sb-otp', '123456'); await page.click('[data-act="sbVerify"]'); await page.wait_for_timeout(500)
    if await page.evaluate("!!document.getElementById('onboarding') || !!ui.ob"): errors.append('Zweites Gerät: Onboarding erscheint trotz eingerichtetem Konto')
    if await page.evaluate("S.profile.name") != 'Eingerichtet': errors.append('Zweites Gerät: Profil kam nicht aus Supabase')
    await ctx.close()
    # Reines Coach-Konto: Coach-Onboarding, nur Team und Profil, Athletenliste nach eigenen Gruppen
    team['roles'] = ['coach']
    db['profile:_'] = {'data': {'name': 'Coach', 'positions': []}, 'updated_at': '2026-01-03T00:00:00.000Z', 'deleted': False}
    ctx = await browser.new_context(viewport={'width': 1280, 'height': 900})
    await ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
    await ctx.route('https://*.supabase.co/**', sbr)
    page = await ctx.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
    await page.goto(ROOT.as_uri()); await page.wait_for_timeout(600)
    await page.evaluate("()=>{ ui.view='profil'; ui.profOpen={sb:true}; render(); }")
    await page.fill('#sb-email', 'athlet@test.invalid'); await page.click('[data-act="sbCode"]'); await page.wait_for_timeout(100)
    await page.fill('#sb-otp', '123456'); await page.click('[data-act="sbVerify"]'); await page.wait_for_timeout(500)
    if await page.evaluate("!!document.getElementById('onboarding')"): errors.append('Coach: Athleten-Onboarding erscheint bei reinem Coach-Konto')
    if not await page.evaluate("!!document.getElementById('coach-onboarding')"): errors.append('Coach: Coach-Onboarding erscheint nicht')
    if await page.evaluate("[...document.querySelectorAll('#nav [data-view]')].map(b=>b.dataset.view).join()") != 'team,profil': errors.append('Coach: Navigation zeigt nicht nur Team und Profil')
    await page.click('[data-act="cobNext"]'); await page.click('[data-act="cobNext"]')
    if await page.evaluate("ui.cob.step") != 1: errors.append('Coach: Funktion ist nicht Pflicht')
    await page.click('[data-act="cobFn"][data-v="sc"]'); await page.click('[data-act="cobGrp"][data-v="WR"]'); await page.click('[data-act="cobNext"]')
    await page.click('[data-act="cobNext"]')
    if await page.evaluate("ui.cob.step") != 2: errors.append('Coach: Vertraulichkeit ist nicht Pflicht')
    await page.click('[data-act="cobOk"]'); await page.click('[data-act="cobNext"]'); await page.click('[data-act="cobNext"]')
    await page.click('[data-act="cobFinish"]'); await page.wait_for_timeout(400)
    if not await page.evaluate("S.profile.coach && S.profile.coach.onboarded && S.profile.coach.groups.join()==='WR' && ui.view==='team' && !ui.cob"): errors.append('Coach: Einrichtung wird nicht gespeichert')
    if not await page.evaluate("document.getElementById('main').textContent.includes('Meine Gruppen (WR)') && document.getElementById('main').textContent.includes('Spieler B')"): errors.append('Coach: Athletenliste filtert nicht nach den eigenen Gruppen')
    await page.evaluate("async()=>{ await sbSync('test'); }")
    if not (db.get('profile:_') or {}).get('data', {}).get('coach'): errors.append('Coach: Einstellungen kamen nicht in Supabase an')
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
