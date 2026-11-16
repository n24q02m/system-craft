#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F1 — sợi chỉ đỏ trên TUYẾN HỌC (facts/edu-order.csv) + nhịp nối khai báo. --strict: cấm nhịp nối thừa."""
import csv, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.paths import FACTS as F, fname_to_chap, read_csv_rows as read_csv  # noqa: E402

def main():
    strict = '--strict' in sys.argv
    errs, warns = [], []
    rt = {r[1].strip(): (r[2].strip(), r[3].strip()) for r in read_csv(os.path.join(F,'red-thread.csv'))[1:] if len(r) >= 4}
    route = []
    for r in read_csv(os.path.join(F, 'edu-order.csv')):
        if not r[0].strip().endswith('.md'): continue
        ch = fname_to_chap(r[0])
        if ch: route.append(ch)
    bridges = {(r[0].strip(), r[1].strip()): r[2].strip()
               for r in read_csv(os.path.join(F,'red-thread-edu-bridges.csv'))[1:] if len(r) >= 3}
    if len(route) != 145: errs.append('edu-order: %d chương (phải 145)' % len(route))
    missing = [c for c in route if c not in rt]
    if missing: errs.append('thiếu trong red-thread: %s' % ', '.join(missing[:6]))
    direct = bridged = 0; breaks = []; used = set()
    for i in range(len(route)-1):
        a, b = route[i], route[i+1]
        if a not in rt or b not in rt: continue
        if rt[a][1] == rt[b][0]:
            direct += 1
            if strict and (a,b) in bridges: warns.append('%s→%s khớp trực tiếp mà vẫn có nhịp nối' % (a,b))
        elif (a,b) in bridges: bridged += 1; used.add((a,b))
        else: breaks.append((a,b))
    for a,b in breaks: errs.append('ĐỨT: %s → %s không có nhịp nối' % (a,b))
    for (a,b), txt in bridges.items():
        if (a,b) not in used: errs.append('nhịp nối thừa: %s→%s' % (a,b))
        if not txt.rstrip().endswith('?'): errs.append('nhịp nối %s→%s không kết thúc bằng "?"' % (a,b))
        if not (60 <= len(txt) <= 400): warns.append('nhịp nối %s→%s dài %d ký tự' % (a,b,len(txt)))
    print('Tuyến học: %d chương · khớp trực tiếp %d · nhịp nối %d · đứt %d' % (len(route), direct, bridged, len(breaks)))
    for w in warns: print('  [warn]', w)
    for e in errs: print('  [ERR ]', e)
    print('RED-THREAD-EDU: %s' % ('PASS' if not errs else 'FAIL'))
    return 0 if not errs else 1

if __name__ == '__main__':
    sys.exit(main())
