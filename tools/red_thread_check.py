#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED-THREAD validator — kiểm tra sợi chỉ đỏ liên chương.

Kiểm facts/red-thread.csv:
  1. đúng 145 dòng, đúng danh sách + thứ tự chương của TUYẾN BẢN ĐỒ (map order
     trong content/book/ — sợi chỉ đỏ là thuộc tính của bản đồ, không phải tuyến học;
     tuyến học edu-order được kiểm riêng bởi tools/edu_order_check.py);
  2. chuỗi liền: cau_hoi_ra[N] ≡ cau_hoi_vao[N+1] (kể cả nhịp chót 14.11.2);
  3. câu hỏi không trống, kết thúc bằng '?';
  4. (khi --with-src) mỗi chương trong content/book/ đã có mục "Sợi chỉ đỏ" trong §0
     đúng nguyên văn cau_hoi_vao.

Chạy:  uv run python tools/red_thread_check.py [--with-src]
"""
import csv, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.paths import CONTENT_BOOK as SRC, FACTS, fname_to_chap, read_csv_rows as read_csv  # noqa: E402

RED_THREAD = os.path.join(FACTS, 'red-thread.csv')


def main():
    errs = []

    def key(ch):
        return tuple(int(x) for x in ch.split('.'))

    expect = sorted((fname_to_chap(f) for f in os.listdir(SRC)
                     if f.endswith('.md') and not f.startswith('P15')), key=key)
    if len(expect) != 145:
        errs.append('content/book/ có %d chương (kỳ vọng 145)' % len(expect))

    rt = read_csv(RED_THREAD)
    hdr, body = rt[0], rt[1:]
    if hdr[:2] != ['thu_tu', 'chuong']:
        errs.append('header lạ: %r' % hdr[:2])
    if len(body) != 145:
        errs.append('red-thread.csv có %d dòng (kỳ vọng 145)' % len(body))

    got = [r[1] for r in body]
    for i, (g, e) in enumerate(zip(got, expect), 1):
        if g != e:
            errs.append('dòng %d: chương %s ≠ map-order %s' % (i, g, e))

    for i, r in enumerate(body):
        qin, qout = r[2], r[3]
        if not qin.strip() or not qout.strip():
            errs.append('dòng %s: câu hỏi trống' % r[1])
        for tag, q in (('vào', qin), ('ra', qout)):
            if not q.rstrip().endswith('?'):
                errs.append('%s (%s): không kết thúc bằng "?"' % (r[1], tag))
        if i + 1 < len(body) and qout != body[i + 1][2]:
            errs.append('đứt chuỗi tại %s: q_out ≠ q_in của %s' % (r[1], body[i + 1][1]))

    # tuỳ chọn: đối chiếu §0 trong src
    if '--with-src' in sys.argv:
        pat = re.compile(r'\*\*Sợi chỉ đỏ:\*\*')
        for r in body:
            f = None
            for cand in os.listdir(SRC):
                pass
            # tìm file theo số chương
            ch = r[1]
            part = ch.split('.')[0]
            if part == '0':
                want = 'P0-00-%s-' % ch.split('.')[1]
            elif part == '14':
                want = 'P14-%s-' % ch
            else:
                want = 'P%s-%02d-' % (part, int(ch.split('.')[1]))
            matches = [x for x in os.listdir(SRC) if x.startswith(want)]
            if not matches:
                errs.append('%s: không tìm thấy file src (%s)' % (ch, want))
                continue
            c = open(os.path.join(SRC, matches[0]), encoding='utf-8').read()
            m0 = re.search(r'^## 0\. Nhập môn', c, re.M)
            if not m0:
                errs.append('%s: chưa có §0' % ch)
            elif not pat.search(c[m0.start():]):
                errs.append('%s: §0 thiếu mục Sợi chỉ đỏ' % ch)
            elif r[2].strip() not in c:
                errs.append('%s: §0 không chứa nguyên văn cau_hoi_vao' % ch)

    if errs:
        print('RED-THREAD: FAIL — %d lỗi' % len(errs))
        for e in errs[:30]:
            print('  -', e)
        sys.exit(1)
    n = len(body)
    print('RED-THREAD: PASS — %d/%d chương, chuỗi 146 nhịp liền, khớp tuyến bản đồ.' % (n, n))


if __name__ == '__main__':
    main()
