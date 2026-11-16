#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PERSONA WALKTHROUGH — kiểm định lộ trình học theo tuần.

Mô phỏng mỗi persona đọc lộ trình của mình theo tuần; trong tuần đọc mọi mục
theo thứ tự tuyến EDU (facts/edu-order.csv). Mô phỏng ĐỌC TỐI ĐA: mọi hàng
morong đều đọc, mọi hàng nhay đều "đọc nhanh §0–§2".

Khi một chương được đọc (đủ hoặc nhanh), mọi chương trong "Đọc trước" (§0)
 phải đã được đọc trước đó — nếu không là ĐỨT KHÁNI NIỆM. Hàng nhay được miễn
kiểm tiên quyết của chính nó (bản chất là đọc nhanh) nhưng vẫn tính là đã đọc
cho các chương sau.

Ngữ nghĩa nghiệm thu:
  - persona (a) — người mới: NGHIÊM NGẶT, 0 đứt khái niệm ở mọi tuần
    (bao gồm 2 tuần đầu không đứt khái niệm);
  - persona (b)/(c) — lộ trình chuyên gia: khoảng hở là CHỦ ĐÍCH (bù bằng
    kinh nghiệm / "đọc khi cần" — Ba tốc độ đọc, P15-00 §4) → chỉ báo cáo.

Chạy:  uv run python tools/persona_walkthrough.py [--quiet]
"""
import csv, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from tools.paths import CONTENT_BOOK as SRC, FACTS, fname_to_chap  # noqa: E402

LP = os.path.join(FACTS, 'learning-paths.csv')
EO = os.path.join(FACTS, 'edu-order.csv')


def f2ch(fn):
    return fname_to_chap(fn) or None


def chkey(ch):
    return tuple(int(x) for x in ch.split('.'))


def load_line():
    order = []
    for line in open(EO, encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        order.append(f2ch(line.split(',')[0].strip()))
    return order


def load_paths():
    paths = {}
    with open(LP, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            p, tuan, ch, loai = [x.strip() for x in next(csv.reader([line]))]
            paths.setdefault(p, []).append((int(tuan), ch, loai))
    return paths


_DT = {}

def doc_truoc(ch):
    """Các chương trong 'Đọc trước' của §0 (dải A–B được giãn)."""
    if ch in _DT:
        return _DT[ch]
    for fn in sorted(os.listdir(SRC)):
        if not (fn.endswith('.md') and f2ch(fn) == ch):
            continue
        c = open(os.path.join(SRC, fn), encoding='utf-8').read()
        m0 = re.search(r'^## 0\. Nhập môn.*?(?=^## 1\.)', c, re.S | re.M)
        dt = re.search(r'\*\*Đọc trước:\*\* (.+)', m0.group())
        refs = set()
        if dt:
            raw = dt.group(1)
            refs = set(re.findall(r'\b(\d+\.\d+(?:\.\d+)?)\b', raw))
            for a, b in re.findall(r'\b(\d+\.\d+(?:\.\d+)?)\s*[–—-]\s*(\d+\.\d+(?:\.\d+)?)\b', raw):
                ka, kb = chkey(a), chkey(b)
                if len(ka) == len(kb) == 2 and ka[0] == kb[0]:
                    refs |= {'%d.%d' % (ka[0], i) for i in range(ka[1], kb[1] + 1)}
                elif len(ka) == 3 and len(kb) == 3 and ka[:2] == kb[:2]:
                    refs |= {'%d.%d.%d' % (ka[0], ka[1], i) for i in range(ka[2], kb[2] + 1)}
        _DT[ch] = sorted(refs, key=chkey)
        return _DT[ch]
    _DT[ch] = None
    return None


def simulate(p, rows, line_pos):
    """Trả (danh sách đứt khái niệm, số chương duy nhất đã đọc)."""
    weeks = {}
    for tuan, ch, loai in rows:
        weeks.setdefault(tuan, []).append((ch, loai))
    read, gaps = {}, []
    for tuan in sorted(weeks):
        for ch, loai in sorted(weeks[tuan], key=lambda x: line_pos.get(x[0], 9999)):
            if loai != 'nhay':                     # đọc đủ → kiểm tiên quyết
                for r in doc_truoc(ch) or []:
                    if r not in read:
                        gaps.append((tuan, ch, r))
            read[ch] = tuan                          # đọc đủ hay nhanh đều tính
    return gaps, len(read)


def main():
    quiet = '--quiet' in sys.argv
    line = load_line()
    line_pos = {ch: i for i, ch in enumerate(line)}
    paths = load_paths()

    # chương trong lộ trình phải tồn tại trong tuyến
    for p, rows in paths.items():
        for _, ch, _ in rows:
            if ch not in line_pos:
                print('[lỗi] %s: chương %s không có trong tuyến EDU' % (p, ch))
                sys.exit(1)

    fail = False
    for p in sorted(paths):
        gaps, n_read = simulate(p, paths[p], line_pos)
        if p == 'a':
            ok = not gaps
            print('persona (a) — người mới, 16 tuần · %d/145 chương · %s'
                  % (n_read, 'KHÔNG đứt khái niệm ở tuần nào ✓' if ok
                     else 'ĐỨT KHÁNI NIỆM:'))
            if not ok:
                fail = True
                for tuan, ch, r in gaps:
                    print('  - tuần %2d · %-8s cần %-8s' % (tuan, ch, r))
        else:
            print('persona (%s) — chuyên gia · %d/145 chương · %d khoảng hở "Đọc trước" (chủ đích — bù bằng kinh nghiệm/đọc khi cần)'
                  % (p, n_read, len(gaps)))
            if not quiet:
                by_week = {}
                for tuan, ch, r in gaps:
                    by_week.setdefault(tuan, []).append('%s←%s' % (ch, r))
                for tuan in sorted(by_week):
                    print('    tuần %2d: %s' % (tuan, ' · '.join(by_week[tuan])))

    if fail:
        print('PERSONA-WALKTHROUGH: FAIL — persona (a) còn đứt khái niệm.')
        sys.exit(1)
    print('PERSONA-WALKTHROUGH: PASS — persona (a) 0 đứt khái niệm (mọi tuần, '
          'mô phỏng đọc tối đa); (b)/(c) chuyên gia — khoảng hở chủ đích đã báo cáo.')


if __name__ == '__main__':
    main()
