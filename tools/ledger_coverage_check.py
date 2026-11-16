#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F2 — chương nêu tên sản phẩm ở §3 thì facts/versions.csv phải có dòng. --strict: khoảng hở = exit 1."""
import csv, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.paths import CONTENT_BOOK as SRC, FACTS as F, fname_to_chap, read_csv_rows as read_csv  # noqa: E402

def ledger_products():
    with open(os.path.join(F,'versions.csv'), encoding='utf-8-sig') as f:
        lines = [l for l in f if not l.lstrip().startswith('#')]
    rd = csv.reader(lines); next(rd)
    return {r[1].strip() for r in rd if r and len(r) > 1}

def candidates():
    out, exempt = {}, []
    for line in open(os.path.join(F,'product-candidates.txt'), encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('#'): continue
        if line.startswith('!'): exempt.append(line[1:].split('|')[0].strip()); continue
        parts = [x.strip() for x in line.split('|')]
        if len(parts) >= 2: out[parts[0]] = parts[1]
    return out, exempt

def section3(text):
    m = re.search(r'^##\s*3\.[^\n]*\n(.*?)(?=^##\s|\Z)', text, re.S | re.M)
    return m.group(1) if m else ''

def main():
    strict = '--strict' in sys.argv
    prods = ledger_products(); canon, exempt = candidates()
    names = {w.lower(): c for w, c in canon.items()}
    for x in exempt: names.pop(x.lower(), None)
    pat = re.compile(r'(?<![\w.])(' + '|'.join(sorted((re.escape(k) for k in names), key=len, reverse=True)) + r')(?![\w.])', re.I)
    total = hit = 0; gaps = {}
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith('.md') or fn.startswith('P15'): continue
        ch = fname_to_chap(fn)
        if not ch: continue
        sec = section3(open(os.path.join(SRC, fn), encoding='utf-8').read())
        if not sec.strip(): continue
        total += 1; found = False
        for m in pat.finditer(sec):
            c = names[m.group(1).lower()]
            if c in prods: found = True
            else: gaps.setdefault('%s ← "%s"' % (c, m.group(1)), set()).add(ch)
        if found: hit += 1
    print('Chương có mục §3: %d · nêu tên ≥1 sản phẩm CÓ trong ledger: %d' % (total, hit))
    for k, v in sorted(gaps.items(), key=lambda kv: -len(kv[1])):
        print('  %-34s %2d chương (vd %s)' % (k, len(v), ', '.join(sorted(v)[:4])))
    print('LEDGER-COVERAGE: %s' % ('PASS' if not gaps else 'CÓ KHOẢNG HỞ (%d)' % len(gaps)))
    return 0 if (not gaps or not strict) else 1

if __name__ == '__main__':
    sys.exit(main())
