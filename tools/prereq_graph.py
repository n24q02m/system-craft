#!/usr/bin/env python3
"""Trích đồ thị tiên quyết (prerequisite graph) từ cross-ref thật trong content/book/.

Đồ thị tiên quyết là dữ kiện cho P15-01 (3 lộ trình persona) và cho kiểm ràng buộc
EDU-ORDER (không chương nào được đứng trước tiên quyết của nó).

Quy ước tên file content/book/:
  P0-00-N-…     → chương 0.N
  P{c}-{nn}-…   → chương c.nn        (c = 1..13, nn zero-pad 2 số)
  P14-14.a.b-…  → chương 14.a.b

Dạng tham chiếu được bắt:
  →x.y · →x.y.z   (mũi tên, khung A/B)
  P0-00-N         (P0 tham chiếu nhau)

Ý nghĩa cạnh A→B: "B là ngữ cảnh/nền nên có khi đọc A" (A phụ thuộc B).

Chạy:  uv run python tools/prereq_graph.py
Ra:    facts/prereq-edges.csv     (src,ref,ref_chapter,count)
       facts/prereq-indegree.csv  (chapter,in_edges,unique_sources)
"""
import os
import re
import glob
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from tools.paths import CONTENT_BOOK as SRC, FACTS  # noqa: E402

REF_RE = re.compile(r'→\s*(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)')
P0REF_RE = re.compile(r'\bP0-00-(\d)\b')
FILE_RE = re.compile(r'^P(\d+)-')


def chapter_id(path):
    base = os.path.basename(path)
    m = FILE_RE.match(base)
    if not m:
        return None
    cluster = int(m.group(1))
    nums = [int(x) for x in re.findall(r'\d+', base)]
    if cluster == 0:
        return f'0.{nums[2]}'              # P0-00-1 → 0.1
    if cluster == 14:
        return f'14.{nums[2]}.{nums[3]}'   # P14-14.1.2 → 14.1.2
    return f'{cluster}.{nums[1]}'          # P5-01-…  → 5.1


def main():
    files = sorted(glob.glob(os.path.join(SRC, 'P*.md')))
    ch_ids = {chapter_id(f) for f in files} - {None}
    # cụm ảo: "14.4" nếu không phải chương nhưng là tiền tố của chương 14.4.x
    virtual = set()
    for r in ch_ids:
        if r.count('.') == 2:
            virtual.add(r.rsplit('.', 1)[0])
    targets = ch_ids | virtual

    edges = defaultdict(int)
    for f in files:
        sid = chapter_id(f)
        txt = open(f, encoding='utf-8').read()
        for m in REF_RE.finditer(txt):
            ref = m.group(1)
            if ref in ch_ids:
                head = ref
            elif ref in virtual:
                head = ref + ' (cụm)'
            else:
                head = None
            if head and head.split(' (')[0] != sid:
                edges[(sid, head)] += 1
        for m in P0REF_RE.finditer(txt):
            head = f'0.{m.group(1)}'
            if head in ch_ids and head != sid:
                edges[(sid, head)] += 1

    with open(os.path.join(FACTS, 'prereq-edges.csv'), 'w', encoding='utf-8') as o:
        o.write('src,ref,ref_chapter,count\n')
        for (s, r), c in sorted(edges.items()):
            o.write(f'{s},{r},{r.split(" (")[0]},{c}\n')

    indeg = defaultdict(int)
    srcs = defaultdict(set)
    for (s, r), c in edges.items():
        indeg[r] += c
        srcs[r].add(s)
    with open(os.path.join(FACTS, 'prereq-indegree.csv'), 'w', encoding='utf-8') as o:
        o.write('chapter,in_edges,unique_sources\n')
        for ch in sorted(indeg, key=lambda k: (-indeg[k], k)):
            o.write(f'{ch},{indeg[ch]},{len(srcs[ch])}\n')

    total = sum(edges.values())
    print(f'edges: {len(edges)} cạnh riêng biệt · {total} lượt tham chiếu · {len(indeg)} đích (gồm cụm ảo)')
    print('Top 20 chương/cụm được tham chiếu nhiều nhất (nền tảng):')
    for ch in sorted(indeg, key=lambda k: (-indeg[k], k))[:20]:
        print(f'  {ch:12s} {indeg[ch]:4d} lượt từ {len(srcs[ch]):3d} chương')


if __name__ == '__main__':
    main()
