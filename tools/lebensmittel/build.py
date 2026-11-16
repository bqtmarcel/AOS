#!/usr/bin/env python3
"""AOS – Lebensmitteldatenbanken aufbereiten (läuft wöchentlich als GitHub Action, siehe .github/workflows/lebensmittel.yml).

Quellen (alle frei nutzbar, Quellenangabe in der App):
  off  Open Food Facts – Produkte, die in Österreich oder Deutschland verkauft werden (ODbL)
  bls  Bundeslebensmittelschlüssel 4.0, Max Rubner-Institut (CC BY 4.0)
  ch   Schweizer Nährwertdatenbank, BLV (Nutzung frei, Quellenangabe)

Aufruf: build.py AUSGABEORDNER [--off DATEI.csv.gz] [--bls DATEI.zip|.xlsx] [--ch DATEI.xlsx]
Ohne Dateiangabe wird die Quelle heruntergeladen. Schlägt eine Quelle fehl, bleibt die vorhandene Datei im
Ausgabeordner unverändert (die App behält dann den alten Stand) – der Lauf meldet den Fehler, bricht aber nicht ab.

Ausgabe je Quelle: <quelle>.json.gz  {"src","updated","fields",[...],"items":[[...], ...]}  (Werte pro 100 g bzw. 100 ml)
sowie index.json mit Anzahl, Stand und Prüfsumme je Quelle.
"""
import csv, gzip, hashlib, html, io, json, os, re, sys, tempfile, time, urllib.parse, urllib.request, zipfile
from datetime import datetime, timezone

UA = {'User-Agent': 'AOS-Athlete-Operating-System/1.0 (github.com/bqtmarcel/AOS; weekly food data build)'}
NOW = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def log(*a): print(*a, flush=True)

def fetch(url, path=None, timeout=600):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        if path is None:
            return r.read()
        with open(path, 'wb') as f:
            while True:
                b = r.read(1 << 20)
                if not b: break
                f.write(b)
    return path

def num(v):
    """Zahl aus Zelle/Text; '<0,1', 'Spuren', 'tr' → 0; leer/unlesbar → None."""
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    s = str(v).strip().replace(',', '.')
    if not s or s in ('-', '–', 'n.a.', 'na', 'NA'): return None
    if s.lower() in ('tr', 'spuren', 'sp.', 'sp'): return 0.0
    if s.startswith('<'): return 0.0
    m = re.match(r'^-?\d+(\.\d+)?', s)
    return float(m.group(0)) if m else None

def r1(x): return round(x * 10) / 10

def plausible(k, p, c, f):
    if None in (k, p, c, f): return False
    if min(k, p, c, f) < 0 or k > 950 or p + c + f > 101: return False
    # Energie grob gegen Makros prüfen (Alkohol/Ballaststoffe erlauben Abweichungen)
    calc = 4 * p + 4 * c + 9 * f
    return not (k > 40 and calc > 0 and (calc > k * 1.6 + 20 or calc < k * 0.4 - 20))

def write_source(out, src, fields, items, meta):
    data = {'src': src, 'updated': NOW, 'fields': fields, 'items': items}
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    path = os.path.join(out, src + '.json.gz')
    with open(path, 'wb') as f:
        f.write(gzip.compress(raw, 9, mtime=0))
    meta[src] = {'file': src + '.json.gz', 'count': len(items), 'updated': NOW,
                 'sha': hashlib.sha256(raw).hexdigest()[:16], 'bytes': os.path.getsize(path)}
    log(f'{src}: {len(items)} Einträge, {os.path.getsize(path) / 1e6:.1f} MB gepackt')

# ---------------------------------------------------------------- Open Food Facts
OFF_URL = 'https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz'
CHAINS = [('b', ('billa', 'merkur')), ('s', ('spar', 'interspar', 'eurospar')), ('h', ('hofer', 'aldi')),
          ('l', ('lidl',)), ('p', ('penny',)), ('m', ('mpreis', 'm-preis')), ('u', ('unimarkt',)), ('a', ('adeg',)), ('d', ('dm',))]

def build_off(out, meta, path=None):
    if path is None:
        path = os.path.join(tempfile.gettempdir(), 'off.csv.gz')
        log('Open Food Facts: lade', OFF_URL); t = time.time(); fetch(OFF_URL, path, timeout=3600)
        log(f'  geladen in {time.time() - t:.0f} s, {os.path.getsize(path) / 1e9:.2f} GB')
    csv.field_size_limit(1 << 30)
    items, seen, n = [], set(), 0
    with gzip.open(path, 'rt', encoding='utf-8', errors='replace', newline='') as fh:
        rd = csv.reader(fh, delimiter='\t', quoting=csv.QUOTE_NONE)
        head = next(rd); ix = {h: i for i, h in enumerate(head)}
        need = ['code', 'product_name', 'countries_tags', 'proteins_100g', 'carbohydrates_100g', 'fat_100g']
        miss = [h for h in need if h not in ix]
        if miss: raise RuntimeError('Spalten fehlen im OFF-Export: ' + ', '.join(miss))
        g = lambda row, h: row[ix[h]] if h in ix and ix[h] < len(row) else ''
        for row in rd:
            n += 1
            ct = g(row, 'countries_tags')
            at = 'en:austria' in ct
            if not at and 'en:germany' not in ct: continue
            code = g(row, 'code').strip()
            if not code or code in seen: continue
            name = (g(row, 'product_name_de') or g(row, 'product_name') or g(row, 'generic_name_de') or g(row, 'generic_name')).strip()
            if len(name) < 2: continue
            p, c, f = num(g(row, 'proteins_100g')), num(g(row, 'carbohydrates_100g')), num(g(row, 'fat_100g'))
            k = num(g(row, 'energy-kcal_100g'))
            if k is None:
                kj = num(g(row, 'energy_100g'))
                k = kj / 4.184 if kj is not None else None
            if not plausible(k, p, c, f): continue
            seen.add(code)
            brand = g(row, 'brands').split(',')[0].strip()[:40]
            stores = (g(row, 'stores') + ',' + g(row, 'brands')).lower()
            chain = ''.join(sorted({ch for ch, keys in CHAINS if any(re.search(r'(^|[^a-z])' + re.escape(kk) + r'([^a-z]|$)', stores) for kk in keys)}))
            qty = g(row, 'quantity').strip()[:20]
            sq = num(g(row, 'serving_quantity'))
            items.append([code, name[:90], brand, round(k), r1(p), r1(c), r1(f), qty, 1 if at else 0, chain, round(sq) if sq and 0 < sq < 2000 else 0])
    log(f'  {n} Zeilen gelesen')
    # Österreich zuerst (nur Reihenfolge der Datei)
    items.sort(key=lambda x: -x[8])
    write_source(out, 'off', ['code', 'name', 'brand', 'kcal', 'P', 'K', 'F', 'qty', 'at', 'chain', 'portion'], items, meta)

# ---------------------------------------------------------------- Tabellen (BLS, Schweiz)
def sheet_rows(xlsx_bytes):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes), read_only=True, data_only=True)
    best = None
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        if best is None or len(rows) > len(best): best = rows
    return best or []

def find_header(rows, must):
    for i, r in enumerate(rows[:40]):
        cells = [str(c or '').strip() for c in r]
        if all(any(re.search(m, c, re.I) for c in cells) for m in must):
            return i, cells
    raise RuntimeError('Kopfzeile nicht gefunden (gesucht: ' + ', '.join(must) + ')')

def pick(cells, pats, avoid=r'englisch|english|herkunft|quelle|source|flag|referenz|kommentar|comment|säure|saeure|acid|ratio|anteil an', prefer=r'100'):
    cand = [i for i, c in enumerate(cells) if any(re.search(p, c, re.I) for p in pats) and not re.search(avoid, c, re.I)]
    if not cand: return None
    pref = [i for i in cand if re.search(prefer, cells[i], re.I)]
    return (pref or cand)[0]

def table_items(rows, spec):
    hi, cells = find_header(rows, spec['must'])
    cols = {k: pick(cells, v) for k, v in spec['cols'].items()}
    log('  Spalten:', {k: (cells[i] if i is not None else None) for k, i in cols.items()})
    miss = [k for k in ('name', 'kcal', 'P', 'K', 'F') if cols.get(k) is None]
    if miss: raise RuntimeError('Spalten nicht erkannt: ' + ', '.join(miss))
    items = []
    for n, r in enumerate(rows[hi + 1:]):
        cell = lambda k: r[cols[k]] if cols.get(k) is not None and cols[k] < len(r) else None
        name = str(cell('name') or '').strip()
        if len(name) < 2: continue
        k, p, c, f = num(cell('kcal')), num(cell('P')), num(cell('K')), num(cell('F'))
        if not plausible(k, p, c, f): continue
        code = str(cell('code') or n).strip()
        items.append([code, name[:110], round(k), r1(p), r1(c), r1(f)])
    return items

BLS_PAGE = 'https://blsdb.de/download'
BLS_SPEC = {'must': [r'bezeichnung|lebensmittel|name', r'kcal|ENERCC'],
            'cols': {'code': [r'^(BLS[ _-]?)?(code|schl[üu]ssel)$', r'^SBLS', r'BLS.?Code'],
                     'name': [r'^lebensmittelbezeichnung', r'bezeichnung', r'^lebensmittel$', r'^name'],
                     'kcal': [r'ENERCC', r'kcal'],
                     'P': [r'^PROT', r'^protein', r'eiwei'],
                     'K': [r'^CHO\b', r'kohlenhydrate,? verf', r'^kohlenhydrat'],
                     'F': [r'^FAT\b', r'^fett\b', r'^fett,? ?gesamt', r'^fett']}}

BLS_DOI = 'https://doi.org/10.25826/Data20251217-134202-0'
BROWSER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'de-AT,de;q=0.9'}

def fetch_page(url):
    req = urllib.request.Request(url, headers=BROWSER)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl(), r.read().decode('utf-8', 'replace')

def bls_candidates():
    """Download-Adressen in sinnvoller Reihenfolge: Link auf blsdb.de (mit Token), Datenpaket bei OpenAgrar (DOI), direkte Adresse."""
    out = []
    try:
        base, page = fetch_page(BLS_PAGE)
        links = [html.unescape(m) for m in re.findall(r'''["']([^"'\s]*?BLS[^"'\s]*?\.(?:zip|xlsx)(?:\?[^"'\s]*)?)["']''', page, re.I)]
        tok = re.search(r'token=([A-Z0-9-]{10,})', page)
        if tok: links.append('/assets/uploads/BLS_4_0_2025_DE.zip?token=' + tok.group(1))
        out += [urllib.parse.urljoin(base, l) for l in links]
        log(f'  blsdb.de: {len(links)} Link(s) gefunden')
    except Exception as e:
        log('  blsdb.de nicht lesbar:', e)
    try:
        base, page = fetch_page(BLS_DOI)
        links = [html.unescape(m) for m in re.findall(r'''["']([^"'\s]*?MCRFileNodeServlet[^"'\s]*?\.(?:zip|xlsx))["']''', page, re.I)]
        out += [urllib.parse.urljoin(base, l) for l in links]
        log(f'  OpenAgrar: {len(links)} Datei(en) gefunden')
    except Exception as e:
        log('  OpenAgrar nicht lesbar:', e)
    out.append('https://blsdb.de/assets/uploads/BLS_4_0_2025_DE.zip')
    good = [u for u in out if not re.search(r'Components|Dokumentation|_EN\.', u, re.I)]
    good.sort(key=lambda u: 0 if re.search(r'Daten|BLS_4_\d_\d{4}_DE', u, re.I) else 1)
    return list(dict.fromkeys(good))

def build_bls(out, meta, path=None):
    if path is None:
        blob = None
        for url in bls_candidates():
            try:
                req = urllib.request.Request(url, headers=BROWSER)
                with urllib.request.urlopen(req, timeout=600) as r: b = r.read()
                if b[:2] == b'PK': blob = b; log('BLS: geladen von', url.split('?')[0], f'({len(b) / 1e6:.1f} MB)'); break
                log('  keine ZIP/Excel-Datei:', url.split('?')[0])
            except Exception as e:
                log('  fehlgeschlagen:', url.split('?')[0], e)
        if blob is None: raise RuntimeError('BLS-Download nicht möglich (blsdb.de und OpenAgrar)')
    else:
        blob = open(path, 'rb').read()
    if blob[:2] == b'PK' and not path_is_xlsx(blob):
        z = zipfile.ZipFile(io.BytesIO(blob))
        names = [n for n in z.namelist() if n.lower().endswith('.xlsx') and re.search(r'daten', n, re.I) and not re.search(r'components', n, re.I)]
        names = names or [n for n in z.namelist() if n.lower().endswith('.xlsx') and not re.search(r'components', n, re.I)]
        if not names: raise RuntimeError('Keine Daten-Excel im BLS-ZIP')
        log('  Datei:', names[0]); blob = z.read(names[0])
    items = table_items(sheet_rows(blob), BLS_SPEC)
    if len(items) < 1000: raise RuntimeError(f'BLS: nur {len(items)} Einträge erkannt – Format geändert?')
    write_source(out, 'bls', ['code', 'name', 'kcal', 'P', 'K', 'F'], items, meta)

def path_is_xlsx(blob):
    try: return 'xl/workbook.xml' in zipfile.ZipFile(io.BytesIO(blob)).namelist()
    except Exception: return False

CH_PAGE = 'https://naehrwertdaten.ch/de/downloads/'
CH_FALLBACK = 'https://naehrwertdaten.ch/wp-content/uploads/2023/08/Schweizer_Nahrwertdatenbank.xlsx'
CH_SPEC = {'must': [r'^name$', r'kcal|kalorien'],
           'cols': {'code': [r'^id$'], 'name': [r'^name$'],
                    'kcal': [r'kalorien', r'kcal'],
                    'P': [r'^protein', r'eiwei'],
                    'K': [r'kohlenhydrate,? verf', r'^kohlenhydrat'],
                    'F': [r'^fett,? total', r'^fett']}}

def build_ch(out, meta, path=None):
    if path is None:
        url = CH_FALLBACK
        try:
            page = fetch(CH_PAGE, timeout=60).decode('utf-8', 'replace')
            xl = [html.unescape(m) for m in re.findall(r'''href=["']([^"']+?\.xlsx)["']''', page, re.I)]
            xl = [u for u in xl if re.search(r'n[aä]h?e?rwert', u, re.I) and not re.search(r'_(fr|it|en)\b|french|italian|english', u, re.I)]
            if xl: url = xl[0] if xl[0].startswith('http') else 'https://naehrwertdaten.ch' + xl[0]
        except Exception as e:
            log('  Download-Seite nicht lesbar, nehme bekannte Adresse:', e)
        log('Schweiz: lade', url); blob = fetch(url, timeout=300)
    else:
        blob = open(path, 'rb').read()
    items = table_items(sheet_rows(blob), CH_SPEC)
    if len(items) < 300: raise RuntimeError(f'Schweiz: nur {len(items)} Einträge erkannt – Format geändert?')
    write_source(out, 'ch', ['code', 'name', 'kcal', 'P', 'K', 'F'], items, meta)

# ---------------------------------------------------------------- Ablauf
def main():
    args = sys.argv[1:]
    if not args: sys.exit(__doc__)
    out = args[0]; os.makedirs(out, exist_ok=True)
    opt = {a[2:]: args[i + 1] for i, a in enumerate(args) if a.startswith('--') and i + 1 < len(args)}
    only = [s for s in ('off', 'bls', 'ch') if s in opt] or ['bls', 'ch', 'off']
    idx_path = os.path.join(out, 'index.json')
    old = json.load(open(idx_path)) if os.path.exists(idx_path) else {}
    meta = dict(old.get('sources', {})); errors = {}
    for src, fn in (('bls', build_bls), ('ch', build_ch), ('off', build_off)):
        if src not in only: continue
        try: fn(out, meta, opt.get(src))
        except Exception as e:
            errors[src] = str(e)[:300]
            log(f'FEHLER {src}: {e} – vorhandene Datei bleibt' + ('' if src in meta else ' (keine vorhanden)'))
    idx = {'updated': NOW, 'sources': meta, 'errors': errors,
           'licenses': {'off': 'Open Food Facts – Open Database License (ODbL), openfoodfacts.org',
                        'bls': 'Max Rubner-Institut (2025): Bundeslebensmittelschlüssel (BLS), Version 4.0 – Deutsche Nährstoffdatenbank. CC BY 4.0',
                        'ch': 'Schweizer Nährwertdatenbank, Bundesamt für Lebensmittelsicherheit und Veterinärwesen BLV, naehrwertdaten.ch'}}
    json.dump(idx, open(idx_path, 'w'), ensure_ascii=False, indent=1)
    log('index.json:', json.dumps({k: v.get('count') for k, v in meta.items()}), 'Fehler:', list(errors) or 'keine')
    if not meta: sys.exit(1)   # gar nichts vorhanden → Lauf rot

if __name__ == '__main__':
    main()
