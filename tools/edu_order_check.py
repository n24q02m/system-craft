#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EDU-ORDER CHECK — nghiệm thu tuyến học LEARNER EDITION.

Kiểm 3 ràng buộc với facts/edu-order.csv:
  1. Đủ 145 file chương, đúng một lần mỗi file (khớp content/book/P0–P14).
  2. TIÊN QUYẾT: mọi chương tham chiếu trong "Đọc trước" (§0) phải đứng TRƯỚC
     chương đó trong tuyến (kể cả tham chiếu tới phụ lục "đọc khi cần").
  3. Báo cáo NHỊP CẮT của sợi chỉ đỏ: các cặp liền kề trong tuyến không phải
     cặp liền kề trong chuỗi bản đồ (facts/red-thread.csv) — chỉ để đối chiếu,
     không fail.

Cách dùng:
    uv run python tools/edu_order_check.py            # kiểm + in báo cáo
    uv run python tools/edu_order_check.py --quiet    # chỉ PASS/FAIL
"""
import csv, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from tools.paths import CONTENT_BOOK as SRC, FACTS, chapter_files as _chapter_paths, fname_to_chap  # noqa: E402

RT = os.path.join(FACTS, 'red-thread.csv')
EO = os.path.join(FACTS, 'edu-order.csv')


def file_to_chapter(fn):
    """P0-00-1-*.md → 0.1 · P14-14.5.2-*.md → 14.5.2 · P3-11-*.md → 3.11."""
    return fname_to_chap(fn) or None


def chapter_files():
    return _chapter_paths(as_basenames=True)


def doc_truoc_refs(fn):
    """Các chương được nêu trong 'Đọc trước' của §0."""
    c = open(os.path.join(SRC, fn), encoding='utf-8').read()
    m0 = re.search(r'^## 0\. Nhập môn.*?(?=^## 1\.)', c, re.S | re.M)
    if not m0:
        return None
    dt = re.search(r'\*\*Đọc trước:\*\* (.+)', m0.group())
    if not dt:
        return []
    return re.findall(r'\b(\d+\.\d+(?:\.\d+)?)\b', dt.group(1))


def main():
    quiet = '--quiet' in sys.argv

    rows = [l for l in open(EO, encoding='utf-8').read().splitlines()
            if l.strip() and not l.startswith('#')]
    order, phan = [], {}
    for r in rows:
        cells = [x.strip() for x in r.split(',')]
        order.append(cells[0])
        phan[cells[0]] = cells[1] if len(cells) > 1 else ''

    src_files = chapter_files()
    errs, warns = [], []

    # (1) đủ & đúng một lần
    if sorted(order) != sorted(src_files):
        thieu = set(src_files) - set(order)
        thua = [f for f in order if f not in set(src_files)]
        dup = [f for f in set(order) if order.count(f) > 1]
        errs.append('tệp không khớp content/book/: thiếu %s · thừa %s · lặp %s'
                    % (sorted(thieu) or '∅', thua or '∅', dup or '∅'))

    # map chương -> vị trí trong tuyến
    pos = {fn: i for i, fn in enumerate(order)}
    chap_of = {fn: file_to_chapter(fn) for fn in order}

    # (2) tiên quyết "Đọc trước"
    for fn in order:
        ch = chap_of[fn]
        refs = doc_truoc_refs(fn)
        if refs is None:
            errs.append('%s: không có §0' % ch)
            continue
        for r in refs:
            # tìm file của chương r
            tgt = next((f for f in order if chap_of[f] == r), None)
            if tgt is None:
                errs.append('%s: "Đọc trước" nêu %s — không tìm thấy chương' % (ch, r))
            elif pos[tgt] > pos[fn]:
                errs.append('%s: tiên quyết %s đứng SAU trong tuyến (nhịp cắt phải vá)' % (ch, r))

    # (3) nhịp cắt sợi chỉ đỏ (chỉ báo cáo)
    rt = [r['chuong'] for r in csv.DictReader(
        l for l in open(RT, encoding='utf-8') if not l.startswith('#'))]
    rt_pos = {ch: i for i, ch in enumerate(rt)}
    cuts = []
    seq = [chap_of[fn] for fn in order if chap_of[fn] in rt_pos]
    for a, b in zip(seq, seq[1:]):
        if rt_pos[b] != rt_pos[a] + 1:
            cuts.append('%s → %s (bỏ qua %s)' % (
                a, b, '→'.join(rt[rt_pos[a] + 1:rt_pos[b]]) or 'cuối chuỗi'))

    if not quiet:
        # thống kê phần học
        stat = {}
        for fn in order:
            p = phan.get(fn, '?')
            stat[p] = stat.get(p, 0) + 1
        print('Phần học:', ' · '.join('%s=%d' % kv for kv in sorted(stat.items())))
        print('Nhịp cắt sợi chỉ đỏ (%d chỗ — cặp liền kề tuyến ≠ liền kề chuỗi):' % len(cuts))
        for c in cuts:
            print('  -', c)

    if errs:
        print('EDU-ORDER: FAIL — %d lỗi' % len(errs))
        for e in errs[:40]:
            print('  -', e)
        sys.exit(1)
    n = len(order)
    print('EDU-ORDER: PASS — %d/%d chương · tiên quyết "Đọc trước" hoà toàn · %d nhịp cắt đã đối chiếu.'
          % (n, len(src_files), len(cuts)))


if __name__ == '__main__':
    main()
