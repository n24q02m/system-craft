#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FRESHNESS CHECK — cơ chế chống phân rã dữ kiện (F2).

VÌ SAO CÓ FILE NÀY
  Một lượt audit tay chỉ kiểm đúng danh sách sản phẩm mà người audit nhớ tới.
  File này biến danh sách đó thành dữ liệu (facts/watchlist.csv) và việc kiểm
  thành script chạy được trong build.

CÁCH DÙNG
  python3 tools/freshness_check.py                 # in báo cáo, exit 1 nếu có DRIFT
  python3 tools/freshness_check.py --json out.json # ghi JSON để build.py gate
  python3 tools/freshness_check.py --max-age 7     # cảnh báo dòng quá hạn kiểm

NGUỒN (chỉ 2 loại, cả hai đều đọc máy được — không cần người đọc blog):
  1. endoflife.date/api/<slug>.json   — lịch phát hành/EOL (cộng đồng, có truy vết)
  2. api.github.com/repos/<repo>/releases — bản phát hành thật của repo

NGUYÊN TẮC
  - Script KHÔNG tự sửa versions.csv. Nó chỉ báo: dòng nào lệch, lệch gì.
    Sửa số là quyết định của người (mọi thay đổi vẫn phải vào ERRATA).
  - Không mạng → báo SKIP, không làm đỏ build.
"""
import argparse
import csv
import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.paths import FACTS, WATCH_ALIAS, read_csv_dicts  # noqa: E402

WATCH = os.path.join(FACTS, 'watchlist.csv')
VERSIONS = os.path.join(FACTS, 'versions.csv')
UA = {'User-Agent': 'system-craft-freshness/1.0'}
# api.github.com không token = 60 request/giờ → 38 dòng sẽ bị SKIP nếu chạy nhiều lần.
# Đặt GITHUB_TOKEN trong môi trường để hết SKIP (không cần quyền gì thêm).
if os.environ.get('GITHUB_TOKEN'):
    UA['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def read_csv(path):
    return [row for row in read_csv_dicts(path) if row.get('product')]


def check_eol(slug, cycle):
    data = get_json(f'https://endoflife.date/api/{slug}.json')
    for c in data:
        if str(c.get('cycle')) == str(cycle):
            return {'latest': c.get('latest'), 'date': c.get('latestReleaseDate'),
                    'eol': c.get('eol'), 'lts': c.get('lts')}
    return {'latest': None, 'date': None, 'eol': None, 'note': 'cycle not found'}


def check_gh(repo):
    d = get_json(f'https://api.github.com/repos/{repo}/releases/latest')
    return {'latest': d.get('tag_name'), 'date': (d.get('published_at') or '')[:10]}


def norm(v):
    """So sánh trên LÕI SỐ của phiên bản, không trên nhãn.
    25.0.5+8 ≡ 25.0.5 · apache-iceberg-1.12.0 ≡ 1.12.0 · v0.9.0 ≡ 0.9.0
    Nhãn ngày (2026-07-28) so nguyên chuỗi."""
    s = str(v or '').strip().lower()
    m = re.search(r'\d{4}-\d{2}-\d{2}', s)
    if m:
        return m.group(0)
    m = re.search(r'(\d+(?:\.\d+)+)', s)
    return m.group(1) if m else s.lstrip('v')


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='json_out')
    ap.add_argument('--sync', action='store_true',
                    help='ghi giá trị ĐANG có trong versions.csv vào watchlist (reset baseline)')
    ap.add_argument('--max-age', type=int, default=0,
                    help='cảnh báo dòng có last_verified cũ hơn N ngày')
    args = ap.parse_args()

    today = date.today()

    if args.sync:
        led = {}
        for r in read_csv(VERSIONS):
            led[(r['product'].strip().lower(), r['cycle'].strip().lower())] = r
            led.setdefault(r['product'].strip().lower(), r)      # fallback tên
        rows = read_csv(WATCH)
        upd = 0
        for w in rows:
            pname = WATCH_ALIAS.get(w['product'].strip(), w['product'].strip()).lower()
            lr = led.get((pname, w.get('cycle', '').strip().lower())) or led.get(pname)
            if lr:
                w['known'] = lr['latest_version'].strip()
                w['cycle'] = w.get('cycle') or lr['cycle'].strip()
                w['last_verified'] = today.isoformat()
                upd += 1
        cols = ['product', 'kind', 'ref', 'cycle', 'known', 'last_verified']
        with open(WATCH, 'w', encoding='utf-8', newline='') as f:
            f.write('# WATCHLIST — baseline đồng bộ từ facts/versions.csv (--sync, %s)\n' % today)
            writer = csv.DictWriter(f, fieldnames=cols, lineterminator='\n', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
        print(f'watchlist: đồng bộ {upd} dòng từ versions.csv')
        return 0
    out, drift, warn, skip = [], [], [], 0

    for w in read_csv(WATCH):
        age = None
        if w.get('last_verified'):
            try:
                age = (today - datetime.strptime(w['last_verified'], '%Y-%m-%d').date()).days
            except ValueError:
                pass
        rec = {'product': w['product'], 'kind': w['kind'], 'ref': w.get('ref', ''),
               'known': w.get('known', ''), 'last_verified': w.get('last_verified', ''),
               'age_days': age, 'status': '?'}
        if args.max_age and age is not None and age > args.max_age:
            warn.append(rec)
        try:
            if w['kind'] == 'eol':
                cur = check_eol(w['ref'], w.get('cycle', ''))
            elif w['kind'] == 'gh':
                cur = check_gh(w['ref'])
            else:
                rec['status'] = 'BAD_KIND'
                out.append(rec)
                continue
        except Exception as e:                      # mạng hỏng: không làm đỏ build
            rec['status'] = 'SKIP'
            rec['error'] = str(e)[:120]
            skip += 1
            out.append(rec)
            continue

        rec.update(cur)
        if not cur.get('latest'):
            rec['status'] = 'UNKNOWN'
        elif not norm(rec['known']):
            rec['status'] = 'NO_BASELINE'          # ledger chưa từng có dòng cho sản phẩm này
        elif norm(cur['latest']) != norm(rec['known']):
            rec['status'] = 'DRIFT'
            drift.append(rec)
        else:
            rec['status'] = 'OK'

        print(f"{rec['status']:8s} {rec['product']:34s} known={rec['known']:>14s}  "
              f"now={str(cur.get('latest')):>14s}  ({cur.get('date')})")
        out.append(rec)

    print('\n--- TỔNG ---')
    print(f"kiểm {len(out)} dòng · DRIFT {len(drift)} · SKIP {skip} · cảnh báo quá hạn {len(warn)}")
    for r in drift:
        print(f"  DRIFT  {r['product']:32s} {r['known']} → {r.get('latest')} ({r.get('date')})")

    if args.json_out:
        with open(args.json_out, 'w', encoding='utf-8') as f:
            json.dump({'checked_on': today.isoformat(), 'rows': out,
                       'drift': drift, 'stale': warn}, f, ensure_ascii=False, indent=1)
        print(f"→ {args.json_out}")

    return 1 if drift else 0


if __name__ == '__main__':
    sys.exit(main())
