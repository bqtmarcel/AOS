#!/usr/bin/env python3
"""Überträgt die allgemeinen Gruppenregeln aus AOS_DATA/docs/AOS_Trainingspfade.json als Konstante TP in index.html.
Aufruf: python3 tools/tp-gen.py ../AOS_DATA/docs/AOS_Trainingspfade.json
Nur allgemeine Regeln (Kandidaten, Dosierung, Pflicht, Ausschlüsse, Vorlagen) – keine persönlichen Werte."""
import json, sys, re, pathlib
tp = json.load(open(sys.argv[1], encoding='utf-8'))
G = {}
for g in tp['gruppen']:
    d = g['dosierung']
    o = {'k': g['kandidaten'], 'sd': d['hauptuebungen_saetze_delta'], 'sf': d.get('gilt_fuer'), 'w': d['ergaenzung_wdh'], 'kf': d['kontakte_faktor'],
         'sprint': d['sprint'], 'p': [[x['uebung_oder_slot'], x['mal']] for x in g['pflicht_pro_woche']],
         'x': [[x['uebung'], x['gilt_wenn']] for x in g['ausschluesse']], 'sp': g.get('slot_prio', {})}
    if g.get('varianten'):
        V = {}
        for vk, v in g['varianten'].items():
            if 'wie' in v: V[vk] = {'wie': v['wie']}; continue
            V[vk] = {k: v[k] for k in ('kontakte_faktor', 'hauptuebungen_saetze_delta', 'kandidaten_vorne') if k in v}
            if 'pflicht_zusatz' in v: V[vk]['p'] = [[x['uebung_oder_slot'], x['mal']] for x in v['pflicht_zusatz']]
            if 'ausschluesse_zusatz' in v: V[vk]['x'] = [x['uebung'] for x in v['ausschluesse_zusatz']]
        o['v'] = V
    G[g['id']] = o
S = {k: dict({'n': v['name'], 'r': v['rollen'], 'p': v['prio'], 'm': v.get('muster', [])}, **({'ph': v['phasen']} if 'phasen' in v else {})) for k, v in tp['slots'].items()}
H = {'unten': 'lower', 'oben': 'upper', 'ganz': 'full'}
V = {n: [{'id': e['id'], 'name': e['name'], 'half': H[e['koerperhaelfte']], 'slots': e['slots']} for e in v['einheiten']] for n, v in tp['vorlagen'].items()}
E = tp['modifikatoren']['erfahrung']['einsteiger']
M = {'einsteiger': {'x': E['ausgeschlossen'], 'cap': E['rpe_cap_delta'], 'minReps': E['hauptuebungen_min_wdh'], 'kf': E['kontakte_faktor'], 'wd': E['ergaenzung_wdh_delta'], 'pref': E['bevorzugt']},
     'clean': tp['modifikatoren']['umsetzen_technisch_sicher']['nein'],
     'schwer': {'kg': 115, 'kf': tp['modifikatoren']['koerper']['schwer']['kontakte_faktor'], 'x': tp['modifikatoren']['koerper']['schwer']['ausgeschlossen']},
     'gross': {'cm': 193, 'pref': tp['modifikatoren']['koerper']['gross']['bevorzugt']}}
Mo = tp['modifikatoren']
def verl(v):
    o = {}
    if 'pflicht' in v: o['p'] = [[x['uebung_oder_slot'], x['mal']] for x in v['pflicht']]
    if 'ausgeschlossen' in v: o['x'] = v['ausgeschlossen']
    if 'bevorzugt' in v: o['pref'] = v['bevorzugt']
    if 'kontakte_faktor' in v: o['kf'] = v['kontakte_faktor']
    if 'flying_10m_ab' in v: o['ab'] = {'flying_10m': v['flying_10m_ab']}
    if 'cod_slots_ab' in v: o['codAb'] = v['cod_slots_ab']
    if 'hinweis' in v: o['h'] = v['hinweis']
    return o
M['verletzung'] = {k: verl(v) for k, v in Mo['verletzungen_12_monate'].items()}
M['alter'] = {'30': {'kf': Mo['alter']['ab_30']['kontakte_faktor'], 'warm': Mo['alter']['ab_30']['aufwaermen_min']}, '35': {'kf': Mo['alter']['ab_35']['kontakte_faktor'], 'warm': Mo['alter']['ab_35']['aufwaermen_min']}}
ms = Mo['mobilitaet_screen_woche_1']
M['mobil'] = {'overhead': {'x': ms['ueberkopf']['nicht_ok']['ausgeschlossen']}, 'ankle': {'pref': ms['sprunggelenk_kniewand_unter_8cm']['bevorzugt'], 'p': [[x['uebung_oder_slot'], x['mal']] for x in ms['sprunggelenk_kniewand_unter_8cm']['pflicht']]}, 'frontRack': {'x': ms['front_rack']['nicht_ok']['ausgeschlossen']}}
M['gewicht'] = {'aufbauen': {'w': Mo['koerpergewicht_ziel']['aufbauen']['ergaenzung_wdh']}, 'reduzieren': {'sd': {'P2': -1, 'P3': -1}}}
M['aussen'] = {'sd': Mo['aussenbelastung']['koerperlich_harter_beruf_oder_schicht']['ergaenzung_saetze_delta']}
j = lambda x: json.dumps(x, ensure_ascii=False, separators=(',', ':'))
body = ('const TP={ version:' + j(tp['version']) + ',\n  slots:' + j(S) + ',\n  vorlagen:' + j(V) + ',\n  mod:' + j(M) + ',\n  gruppen:{\n' +
        ',\n'.join('    ' + k + ':' + j(v) for k, v in G.items()) + '\n  } };')
p = pathlib.Path(__file__).resolve().parent.parent / 'index.html'
s = p.read_text(encoding='utf-8')
a, b = '/* TP-BEGIN (tools/tp-gen.py) */', '/* TP-END */'
if a in s:
    s = re.sub(re.escape(a) + r'.*?' + re.escape(b), lambda m: a + '\n' + body + '\n' + b, s, flags=re.S)
    p.write_text(s, encoding='utf-8'); print('TP aktualisiert (Trainingspfade ' + tp['version'] + ')')
else:
    print('Marker fehlen in index.html'); sys.exit(1)
