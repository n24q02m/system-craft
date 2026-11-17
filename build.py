#!/usr/bin/env python3
"""SYSTEMS ATLAS build: content/book/P*.md (nguồn chân lý) -> DRAFT.md + .html + .docx + .pdf
Một nguồn, nhiều đầu ra. Chạy: uv run python build.py [--profile edu] [--out-dir dist] [--split-parts] [--no-pdf]"""
import csv, os, re, sys, glob, datetime, subprocess, tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from tools.paths import (
    CONTENT_BOOK as SRC,
    CONTENT_DIAGRAMS,
    FACTS,
    SITE,
    chapter_files,
    edu_files,
    fname_to_chap,
    read_csv_dicts,
    read_csv_rows,
    sort_key,
)
from tools.pdf_render import render_pdf_with_fallback

EDITION_VER = 'SA-2028.1'

# Một nguồn, nhiều đầu ra — kể cả hai ấn phẩm (DRAFT tra cứu / EDU tuyến học) cùng sinh từ content/book/
OUTS = {
    'draft': dict(md='SYSTEMS-ATLAS-DRAFT.md', html='SYSTEMS-ATLAS-DRAFT.html',
                  docx='SYSTEMS-ATLAS-DRAFT.docx', pdf='SYSTEMS-ATLAS-DRAFT.pdf'),
    'edu':   dict(md='SYSTEMS-ATLAS-EDU.md',   html='SYSTEMS-ATLAS-EDU.html',
                  docx='SYSTEMS-ATLAS-EDU.docx',   pdf='SYSTEMS-ATLAS-EDU.pdf'),
}
PROFILE = 'draft'
OUT_DIR = None
OUT_MD = OUT_HTML = OUT_DOCX = OUT_PDF = None

def set_profile(p, out_dir=None):
    """Chọn ấn phẩm: 'draft' (mặc định, nguyên hành vi cũ) hoặc 'edu' (tuyến học)."""
    global PROFILE, OUT_DIR, OUT_MD, OUT_HTML, OUT_DOCX, OUT_PDF
    PROFILE = p
    OUT_DIR = os.path.abspath(out_dir) if out_dir else BASE
    os.makedirs(OUT_DIR, exist_ok=True)
    OUT_MD   = os.path.join(OUT_DIR, OUTS[p]['md'])
    OUT_HTML = os.path.join(OUT_DIR, OUTS[p]['html'])
    OUT_DOCX = os.path.join(OUT_DIR, OUTS[p]['docx'])
    OUT_PDF  = os.path.join(OUT_DIR, OUTS[p]['pdf'])

# ---------- self-healing deps ----------
def _ensure(mods):
    missing = []
    for m in mods:
        try: __import__(m)
        except ImportError: missing.append(m)
    if missing:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', *missing],
                           check=True, timeout=300)
        except Exception as e:
            print(f"[warn] pip install failed ({missing}): {e}")
    ok = {}
    for m in mods:
        try: __import__(m); ok[m] = True
        except ImportError: ok[m] = False
    return ok

# ---------- assembly ----------
def csv_rows(name):
    try:
        with open(os.path.join(FACTS, name), encoding='utf-8') as f:
            return sum(1 for _ in f) - 1
    except FileNotFoundError:
        return 0

def cluster_of(path):
    m = re.match(r'P(\d+)', os.path.basename(path))
    return int(m.group(1)) if m else -1

def load_edu_order():
    """Đọc facts/edu-order.csv — cột 1 tên file chương, cột 2 phan_hoc (1-4 lõi, 9 phụ lục)."""
    path = os.path.join(FACTS, 'edu-order.csv')
    try:
        rows = [l.strip() for l in open(path, encoding='utf-8')
                if l.strip() and not l.strip().startswith('#')]
    except FileNotFoundError:
        return None, {}
    files, phan = [], {}
    for r in rows:
        cells = [c.strip() for c in r.split(',')]
        if cells[0]:
            files.append(os.path.join(SRC, cells[0]))
            if len(cells) > 1 and cells[1]:
                phan[cells[0]] = cells[1]
    return files, phan


PART_META = {                       # nhãn phần học trong ấn phẩm tuyến học
    '1': ('HỌC 1 — MÁY & MÃ',
          'P0 Bản đồ → P1 Vật lý & phần cứng → P2 Kernel → P3 Runtime',
          'Từ transistor đến tiến trình — code chạy trên vật chất.'),
    '2': ('HỌC 2 — DỮ LIỆU & GIAO TIẾP',
          'P4 Giao thức & hợp đồng API → P5 Lưu trữ & dữ liệu → P6 Client/Edge → P7 Frontend',
          'Từ tiến trình đơn máy đến sản phẩm nhiều người dùng.'),
    '3': ('HỌC 3 — PHÂN TÁN, CLOUD, AN NINH, VẬN HÀNH',
          'P8 Hệ phân tán → P9 Cloud & delivery → P10 An ninh → P11 SRE',
          'Từ một máy đến một hệ thống nhiều người cùng tin.'),
    '4': ('HỌC 4 — AI & BIÊN GIỚI',
          'P12 AI → P13 Pattern hệ thống lớn → P14 lõi (15 chương)',
          'Trí tuệ nhân tạo, quy mô lớn, và các biên giới ngành.'),
    '9': ('PHỤ LỤC — ĐỌC KHI CẦN',
          'P14 chuyên sâu: RF di động · game · robot · chuẩn RFC · ngôn ngữ lập trình · mật mã nâng cao',
          'Đọc theo nhu cầu — không chặn tuyến; mỗi chương tự nêu "Đọc trước" của nó.'),
}


def load_edu_bridges():
    """F1: đọc facts/red-thread-edu-bridges.csv -> {chương_đích: văn_bản_nối}."""
    path = os.path.join(FACTS, 'red-thread-edu-bridges.csv')
    out = {}
    for r in read_csv_rows(path):
        if len(r) >= 3 and r[1].strip() and r[1].strip() != 'den_chuong':
            out[r[1].strip()] = r[2].strip()
    return out

def preflight():
    """Ba cổng kiểm định: freshness · red_thread_edu · ledger_coverage. Cổng F1 chặn build."""
    for tool, hard in (('freshness_check.py', False),
                       ('red_thread_edu_check.py', True),
                       ('ledger_coverage_check.py', False)):
        tp = os.path.join(BASE, 'tools', tool)
        if not os.path.exists(tp):
            continue
        r = subprocess.run([sys.executable, tp], capture_output=True, text=True, encoding='utf-8', errors='replace')
        tail = ((r.stdout or '').strip().split('\n') or [''])[-1]
        print('[gate] %-28s %s' % (tool, tail))
        if hard and r.returncode != 0:
            sys.exit('[gate] CHẶN BUILD: ' + tool)

def part_separator(p, basenames, phan):
    """Trang nhãn phần học (markdown) — chèn khi tuyến đổi phần học."""
    title, arc, note = PART_META[p]
    n = sum(1 for b in basenames if phan.get(b, '1') == p)
    return '# %s\n\n> **%d chương** · %s\n> %s\n' % (title, n, arc, note)

def assemble(profile='draft', out_dir=None, write_md=True):
    chapters = sorted(chapter_files(), key=sort_key)
    edu = edu_files()
    if profile == 'edu':
        order, phan = load_edu_order()
        use_order = bool(order and sorted(order) == sorted(chapters) and len(order) == len(chapters))
        if use_order:
            chapters = order                      # tuyến học hợp lệ — dùng EDU-ORDER
        else:
            print('[warn] facts/edu-order.csv không khớp content/book/ (thiếu/thừa/dup) — dùng thứ tự mặc định')
        front = [f for f in edu if re.match(r'P15-(00|01)(?!-Q)', os.path.basename(f))]
        quizzes, labs, tail, sols = {}, {}, [], {}
        qa_file = None
        for f in edu:
            bn = os.path.basename(f)
            m = re.match(r'P15-02-Q(\d+)', bn)
            n = re.match(r'P15-03-L(\d+)', bn)
            q = re.match(r'P15-04-S(\d+)', bn)
            if bn.startswith('P15-02-QA'):
                qa_file = f                       # quiz nâng cao M3 → trước Phụ lục
            elif m:
                quizzes[int(m.group(1))] = f      # quiz cụm N → chèn sau cụm N
            elif n:
                labs[int(n.group(1))] = f         # lab cụm N → chèn sau quiz cụm N
            elif q:
                sols[int(q.group(1))] = f         # lời giải cụm N → sau lab cụm N
            elif f not in front:
                tail.append(f)
        last_pos = {}
        for i, f in enumerate(chapters):
            if phan.get(os.path.basename(f), '1') == '9':
                continue                          # phụ lục "đọc khi cần" — không neo quiz
            last_pos[cluster_of(f)] = i           # chương LÕI cuối cùng của mỗi cụm
        files = list(front)
        extra = {}                                # đường dẫn tổng hợp → văn bản (trang nhãn + F1 bridges)
        qa_inserted = False
        prev_phan = None
        for i, f in enumerate(chapters):
            if use_order:
                p = phan.get(os.path.basename(f), '1')
                if p != prev_phan:                # tuyến đổi phần học → chèn trang nhãn
                    if p == '9' and qa_file and not qa_inserted:
                        files.append(qa_file)
                        qa_inserted = True
                    sep = os.path.join(SRC, '_PART-%s.md' % p)
                    extra[sep] = part_separator(p, [os.path.basename(x) for x in chapters], phan)
                    files.append(sep)
                    prev_phan = p
            files.append(f)
            c = cluster_of(f)
            if last_pos.get(c) == i:
                if c in quizzes:
                    files.append(quizzes[c])       # checkpoint đọc xong cụm
                if c in labs:
                    files.append(labs[c])          # lab tay theo sau quiz của cụm
                if c in sols:
                    files.append(sols[c])          # lời giải sau lab của cụm
        if qa_file and not qa_inserted:
            files.append(qa_file)
        BRIDGES = load_edu_bridges()
        for f in chapters:
            ch = fname_to_chap(os.path.basename(f))
            if ch in BRIDGES:
                head = '> **Nhịp nối (tuyến học)** — %s\n\n' % BRIDGES[ch]
                extra[f] = head + open(f, encoding='utf-8').read()
        for c in sorted(quizzes):
            if c not in last_pos:
                print('[warn] quiz cụm %d không có chương lõi để neo' % c)
        files += tail
    else:
        files = chapters + edu                     # DRAFT: tầng học nằm cuối như phụ lục
        extra = {}
    N_DEC, N_INC = csv_rows('coverage-decisions.csv'), csv_rows('coverage-incidents.csv')
    today = datetime.date.today().isoformat()
    total_words = 0; done = 0; todo = 0
    parts = []
    for f in files:
        txt = extra.get(f) or open(f, encoding='utf-8').read()
        words = len(txt.split()); total_words += words
        bn = os.path.basename(f)
        status_line = next((l for l in txt.split('\n') if 'Trạng thái' in l), '')
        if bn.startswith('_PART'):
            written = True
        elif bn.startswith('P15'):
            written = 'CHƯA VIẾT' not in status_line
        else:
            written = not (('CHƯA VIẾT' in status_line) or ('SEED' in status_line and words < 4000) or words < 600)
            done += written; todo += (not written)  # chỉ chương P0–P14 mới tính done/todo
        parts.append((f, txt, words, written))
    edu_note = f' · Tầng học (P15): {len(edu)} văn kiện' if edu else ''
    if profile == 'edu':
        header = f'''# SYSTEMS ATLAS — LEARNER EDITION (EDU) · {EDITION_VER} rev {today}

> **Tuyến học** theo `facts/edu-order.csv` · 4 phần học + phụ lục "đọc khi cần" · Số chương: {len(chapters)}/145 · Tổng từ: {total_words:,}{edu_note}
> Một nguồn với DRAFT (`content/book/`), khác nhau cách lắp: EDU = tuyến học + quiz chèn cạnh cụm.
> Phủ: {N_DEC} quyết định + {N_INC} sự cố (`facts/coverage-*.csv`)

---

'''
    else:
        v_csv = os.path.join(FACTS, 'versions.csv')
        latest_ver = today
        if os.path.exists(v_csv):
            with open(v_csv, encoding='utf-8-sig', newline='') as vf:
                dates = [r.get('last_verified', '').strip() for r in csv.DictReader(vf) if r.get('last_verified', '').strip()]
                if dates:
                    latest_ver = max(dates)
        header = f'''# SYSTEMS ATLAS — BẢN DỰNG (DRAFT) · {EDITION_VER} rev {today}

> **Một nguồn duy nhất** sinh từ `content/book/P*.md` · Số chương: {len(chapters)}/145 · Đã viết: {done} · Chưa viết: {todo} · Tổng từ: {total_words:,}{edu_note}
> Dữ kiện: `facts/versions.csv` (last_verified {latest_ver}) · Phủ: `facts/coverage-decisions.csv` ({N_DEC} quyết định) + `facts/coverage-incidents.csv` ({N_INC} sự cố)

---

'''
    md_path = os.path.join(os.path.abspath(out_dir), OUTS.get(profile, OUTS['draft'])['md']) if out_dir else OUT_MD
    if write_md and md_path:
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, 'w', encoding='utf-8') as o:
            o.write(header)
            for f, txt, words, written in parts:
                o.write(txt.rstrip() + '\n\n---\n\n')
    return files, parts, done, todo, total_words

# ---------- HTML ----------
def load_diagrams():
    """Đọc facts/diagrams.csv + content/diagrams/*.svg -> {chapter: [(file, sec, svg_raw, cap_vi), ...]}."""
    d_csv = os.path.join(FACTS, 'diagrams.csv')
    out = {}
    for r in read_csv_dicts(d_csv):
        chap = (r.get('chapter') or '').strip()
        svg_file = (r.get('svg_file') or '').strip()
        sec = (r.get('anchor_section') or '2').strip()
        cap = (r.get('caption_vi') or '').strip()
        svg_path = os.path.join(CONTENT_DIAGRAMS, svg_file)
        if chap and svg_file and os.path.exists(svg_path):
            svg_raw = open(svg_path, encoding='utf-8').read().strip()
            out.setdefault(chap, []).append((svg_file, sec, svg_raw, cap))
    return out

def inject_chapter_diagrams_html(chap, html_frag, diagrams=None):
    """Chèn <figure class='diagram'> SVG vào section § tương ứng của chương HTML."""
    diags = (load_diagrams() if diagrams is None else diagrams).get(chap) or []
    if not diags:
        return html_frag
    for svg_file, sec, svg_raw, cap in diags:
        fig = f'\n<figure class="diagram" data-diag="{svg_file}">\n{svg_raw}\n<figcaption>{cap}</figcaption>\n</figure>\n'
        pat = re.compile(rf'(<h2>\s*{re.escape(str(sec))}\.[^<]*</h2>)', re.I)
        if pat.search(html_frag):
            html_frag = pat.sub(lambda m: m.group(1) + fig, html_frag, count=1)
        else:
            html_frag = html_frag + fig
    return html_frag

def _load_shared_diagram_css():
    p = os.path.join(SITE, 'src', 'styles', 'diagram.css')
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''

CSS = '''
:root { --ink:#1a1c1f; --muted:#5b6470; --line:#d8dde3; --line-strong:#b2c1c9; --accent:#0b5fff; --accent-soft:#e4edf5; --surface-2:#eef2f5; --warn:#8a5b12; --warn-soft:#f8f0df; --ok:#1f5f45; --ok-soft:#e2efe9; --bg:#fbfbfd; --card:#ffffff; --code:#f4f6f9; }
* { box-sizing:border-box; }
body { font-family:"Noto Serif","DejaVu Serif","Times New Roman",serif; color:var(--ink);
       background:var(--bg); margin:0; line-height:1.65; font-size:16px; }
.page { max-width:860px; margin:0 auto; padding:28px 20px 80px; }
header.cover { border-bottom:3px solid var(--ink); padding:38px 0 26px; margin-bottom:34px; }
header.cover h1 { font-size:34px; margin:0 0 10px; letter-spacing:.5px; }
header.cover .meta { color:var(--muted); font-size:14px; font-family:"DejaVu Sans","Segoe UI",Arial,sans-serif; }
h1.chap { font-size:24px; border-top:1px solid var(--line); padding-top:26px; margin-top:44px;
          font-family:"DejaVu Sans","Segoe UI",Arial,sans-serif; }
div.chap-lead { page-break-before: always; break-before: page; page-break-inside: avoid; break-inside: avoid; margin-top: 32px; }
div.chap-lead blockquote.nhip-noi { margin: 0 0 10px; background: #eef4ff; color: var(--ink); border-left: 4px solid var(--accent); }
div.chap-lead h1.chap { page-break-before: avoid; break-before: avoid; margin-top: 8px; padding-top: 10px; border-top: 0; }
h2 { font-size:18px; margin-top:26px; font-family:"DejaVu Sans","Segoe UI",Arial,sans-serif; }
h3 { font-size:15.5px; margin-top:18px; font-family:"DejaVu Sans","Segoe UI",Arial,sans-serif; }
blockquote { margin:12px 0; padding:10px 16px; border-left:4px solid var(--accent);
             background:var(--card); color:var(--muted); font-size:14.5px;
             font-family:"DejaVu Sans","Segoe UI",Arial,sans-serif; }
blockquote p { margin:4px 0; }
table { border-collapse:collapse; width:100%; margin:14px 0; font-size:14px;
        font-family:"DejaVu Sans",Arial,sans-serif; background:var(--card); }
th, td { border:1px solid var(--line); padding:6px 10px; text-align:left; vertical-align:top; }
th { background:#eef2f7; }
tr:nth-child(even) td { background:#f7f9fb; }
pre { background:var(--code); border:1px solid var(--line); border-radius:6px; padding:12px 14px;
      overflow-x:auto; font-size:13px; line-height:1.5; }
code { font-family:"DejaVu Sans Mono",Consolas,monospace; font-size:13px; }
p code, li code, td code { background:var(--code); padding:1px 5px; border-radius:4px; }
hr { border:0; border-top:1px dashed var(--line); margin:34px 0; }
ul, ol { padding-left:26px; }
a { color:var(--accent); text-decoration:none; }
nav.toc { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:18px 22px; margin-bottom:40px; }
nav.toc h2 { margin:0 0 10px; font-size:16px; }
nav.toc ol { font-size:13.5px; font-family:"DejaVu Sans",Arial,sans-serif; column-count:2; column-gap:34px; }
nav.toc li { margin:2px 0; break-inside:avoid; }
nav.toc li a.part { font-weight:700; letter-spacing:.3px; }
.stub { color:#9aa3ad; font-style:italic; }
@media print { body { background:#fff; } h1.chap { page-break-before:always; } div.chap-lead { page-break-before:always; break-before:page; page-break-inside:avoid; break-inside:avoid; } div.chap-lead h1.chap { page-break-before:avoid; break-before:avoid; } nav.toc ol { column-count:1; } }
'''

def render_html_doc(parts, stats, title_override=None):
    import markdown as _md
    md = _md.Markdown(extensions=['tables', 'fenced_code'])
    diagrams = load_diagrams()
    diag_css = _load_shared_diagram_css()
    body = []
    toc = []
    idx = 0
    for f, txt, words, written in parts:
        idx += 1
        html = md.reset().convert(txt)
        bn = os.path.basename(f)
        if bn.startswith('P') and not bn.startswith('P15'):
            html = inject_chapter_diagrams_html(fname_to_chap(bn), html, diagrams)
        lines = txt.split('\n')
        title = next((l[2:].strip() for l in lines if l.startswith('# ')), os.path.basename(f))
        cid = f'ch-{idx:03d}'
        # anchor the first h1
        html = re.sub(r'<h1>', f'<h1 class="chap" id="{cid}">', html, count=1)
        if not re.search(r'<h1 class="chap"', html):
            html = f'<h1 class="chap" id="{cid}">{title}</h1>\n' + html
        # keep any leading Nhịp nối bridge attached on the same page as h1.chap
        html = re.sub(
            r'^(<blockquote>\s*<p><strong>Nhịp nối \(tuyến học\)</strong>.*?</p>\s*</blockquote>\s*<h1 class="chap"[^>]*>.*?</h1>)',
            lambda m: '<div class="chap-lead">' + m.group(1).replace('<blockquote>', '<blockquote class="nhip-noi">', 1) + '</div>',
            html,
            count=1,
            flags=re.S,
        )
        toc.append((cid, title, written, os.path.basename(f)))
        body.append(html)
    def _li(item):
        c, t, w, bn = item
        if bn.startswith('_PART'):
            return f'<li><a href="#{c}" class="part">{t}</a></li>'
        cls = '' if w else ' class="stub"'
        return f'<li><a href="#{c}"{cls}>{t}</a></li>'
    edu_layer = any(os.path.basename(f).startswith('P15') for f, _, _, _ in parts)
    toc_html = ('<nav class="toc"><h2>Mục lục — ' + str(len(parts)) + (' mục</h2><ol>' if edu_layer else ' chương</h2><ol>')
                + ''.join(_li(x) for x in toc) + '</ol></nav>')
    today = datetime.date.today().isoformat()
    if stats.get('profile') == 'edu':
        cover_title = title_override or f'SYSTEMS ATLAS — LEARNER EDITION ({EDITION_VER})'
        cover_meta = (f'{EDITION_VER} · Tuyến học: <code>facts/edu-order.csv</code> · {stats["chapters"]} chương · '
                      f'{stats["words"]:,} từ · Tầng học: {stats.get("edu", 0)} văn kiện · rev {today}<br>'
                      'Cùng nguồn với DRAFT (<code>content/book/</code>) — khác cách lắp: tuyến học thay vì bản đồ ngành')
    elif stats.get('profile') == 'cases':
        cover_title = title_override or f'SYSTEMS ATLAS ({EDITION_VER}) — TẬP V: {stats["chapters"]} CASE STUDIES THỰC CHIẾN'
        cover_meta = (f'{EDITION_VER} · Tập V: {stats["chapters"]} Case Studies Thực chiến · '
                      f'{stats["words"]:,} từ · rev {today}<br>'
                      'Nguồn: <code>content/cases/vi/*.md</code> — phân tích kiến trúc và nguyên tắc vận hành hệ thống thật')
    else:
        cover_title = title_override or f'SYSTEMS ATLAS ({EDITION_VER})'
        edu_note = (f' · Tầng học (P15): {stats.get("edu", 0)} văn kiện' if stats.get('edu') else '')
        cover_meta = (f'Bản dựng (DRAFT) · {EDITION_VER} rev {today} · {stats["chapters"]} chương ·'
                      f'đã viết {stats["done"]} / chưa viết {stats["todo"]} · {stats["words"]:,} từ{edu_note}<br>'
                      f'Nguồn: <code>content/book/P*.md</code> · Phủ: {stats["dec"]} quyết định + {stats["inc"]} sự cố (facts/*.csv)')
    return f'''<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex, notranslate">
<title>{cover_title} ({today})</title>
<style>{CSS}\n{diag_css}</style></head>
<body><div class="page">
<header class="cover">
<h1>{cover_title}</h1>
<div class="meta">{cover_meta}</div>
</header>
{toc_html}
{''.join(body)}
</div></body></html>'''

def build_html(parts, stats, html_path=None):
    doc = render_html_doc(parts, stats)
    out = html_path or OUT_HTML
    open(out, 'w', encoding='utf-8').write(doc)
    return doc

# ---------- DOCX ----------
def build_docx(parts, stats, docx_path=None):
    import docx
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from bs4 import BeautifulSoup

    doc = Document()
    # base styles
    st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(6)
    for h, sz in [('Heading 1', 17), ('Heading 2', 13), ('Heading 3', 11.5), ('Heading 4', 10.5)]:
        s = doc.styles[h]; s.font.name = 'Calibri'; s.font.size = Pt(sz)
        s.font.color.rgb = RGBColor(0x1a, 0x1c, 0x1f)
    for sec in doc.sections:
        sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = sec.bottom_margin = Cm(2.0)

    today = datetime.date.today().isoformat()
    if stats.get('profile') == 'edu':
        cover_head = f'SYSTEMS ATLAS — LEARNER EDITION ({EDITION_VER})'
        cover_sub = (f'{EDITION_VER} · Tuyến học: facts/edu-order.csv · {stats["chapters"]} chương · {stats["words"]:,} từ · '
                     f'Tầng học: {stats.get("edu", 0)} văn kiện · rev {today}\n'
                     'Cùng nguồn với DRAFT (content/book/) — khác cách lắp: tuyến học thay vì bản đồ ngành')
    elif stats.get('profile') == 'cases':
        cover_head = f'SYSTEMS ATLAS ({EDITION_VER}) — TẬP V: {stats["chapters"]} CASE STUDIES THỰC CHIẾN'
        cover_sub = (f'{EDITION_VER} · Tập V: {stats["chapters"]} Case Studies Thực chiến · {stats["words"]:,} từ · rev {today}\n'
                     'Nguồn: content/cases/vi/*.md — phân tích kiến trúc và nguyên tắc vận hành hệ thống thật')
    else:
        cover_head = f'SYSTEMS ATLAS ({EDITION_VER})'
        edu_note = (f'\nTầng học (P15): {stats.get("edu", 0)} văn kiện' if stats.get('edu') else '')
        cover_sub = (f'Bản dựng (DRAFT) · {EDITION_VER} rev {today}\n'
                     f'{stats["chapters"]} chương · đã viết {stats["done"]} / chưa viết {stats["todo"]} · {stats["words"]:,} từ\n'
                     f'Nguồn: content/book/P*.md — một nguồn, nhiều đầu ra (md/html/docx/pdf){edu_note}')
    t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run(cover_head); r.bold = True; r.font.size = Pt(30)
    t2 = doc.add_paragraph(); t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = t2.add_run(cover_sub)
    r2.font.size = Pt(11); r2.font.color.rgb = RGBColor(0x5b, 0x64, 0x70)

    # TOC (static)
    doc.add_page_break()
    doc.add_heading('Mục lục', level=1)
    for i, (f, txt, words, written) in enumerate(parts, 1):
        lines = txt.split('\n')
        title = next((l[2:].strip() for l in lines if l.startswith('# ')), os.path.basename(f))
        p = doc.add_paragraph()
        rr = p.add_run(f'{title}')
        if os.path.basename(f).startswith('_PART'):
            rr.bold = True                            # nhãn phần học trong mục lục
        if not written: rr.font.color.rgb = RGBColor(0x9a, 0xa3, 0xad); rr.italic = True

    def add_runs(par, node, mono=False, bold=False, italic=False):
        from bs4 import NavigableString, Tag
        if isinstance(node, NavigableString):
            run = par.add_run(str(node))
            run.bold = bold; run.italic = italic
            if mono: run.font.name = 'Consolas'; run.font.size = Pt(9.5)
            return
        if not isinstance(node, Tag): return
        b = bold or node.name in ('strong', 'b')
        i = italic or node.name in ('em', 'i')
        m = mono or node.name == 'code'
        if node.name == 'br':
            par.add_run('\n'); return
        for ch in node.children:
            add_runs(par, ch, m, b, i)

    def add_block(el):
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        name = el.name
        if name in ('h1', 'h2', 'h3', 'h4'):
            lvl = int(name[1])
            p = doc.add_heading('', level=lvl)
            add_runs(p, el)
        elif name == 'p':
            p = doc.add_paragraph()
            add_runs(p, el)
        elif name == 'blockquote':
            for sub in el.find_all(['p'], recursive=False) or [el]:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.8)
                add_runs(p, sub)
                for r in p.runs: r.font.color.rgb = RGBColor(0x5b, 0x64, 0x70)
        elif name == 'pre':
            code = el.get_text()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            for j, line in enumerate(code.split('\n')):
                if j: p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.5)
                r = p.add_run(line if line else ' ')
                r.font.name = 'Consolas'; r.font.size = Pt(8.5)
        elif name == 'ul':
            for li in el.find_all('li', recursive=False):
                p = doc.add_paragraph(style='List Bullet'); add_runs(p, li)
        elif name == 'ol':
            for li in el.find_all('li', recursive=False):
                p = doc.add_paragraph(style='List Number'); add_runs(p, li)
        elif name == 'table':
            rows = el.find_all('tr')
            if not rows: return
            ncol = max(len(r.find_all(['td', 'th'])) for r in rows) or 1
            tb = doc.add_table(rows=0, cols=ncol); tb.style = 'Table Grid'
            for r in rows:
                cells = r.find_all(['td', 'th'])
                row = tb.add_row()
                for c in range(ncol):
                    cell = row.cells[c]
                    cell.text = ''
                    par = cell.paragraphs[0]
                    if c < len(cells):
                        add_runs(par, cells[c])
                        for run in par.runs: run.font.size = Pt(9)
                        if cells[c].name == 'th':
                            for run in par.runs: run.bold = True
        elif name == 'figure':
            cap = el.find('figcaption')
            svg = el.find('svg')
            aria = (svg.get('aria-label') or '').strip() if svg else ''
            cap_txt = ' '.join(cap.get_text(' ', strip=True).split()) if cap else ''
            label = cap_txt or ' '.join(aria.split())
            if label:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.6)
                r = p.add_run(f'[Sơ đồ: {label}]')
                r.italic = True
                r.font.color.rgb = RGBColor(0x5b, 0x64, 0x70)
        elif name == 'hr':
            p = doc.add_paragraph(); p.add_run('—').font.color.rgb = RGBColor(0xaa, 0xaa, 0xaa)

    import markdown as _md
    mdconv = _md.Markdown(extensions=['tables', 'fenced_code'])
    for k, (f, txt, words, written) in enumerate(parts):
        html = mdconv.reset().convert(txt)
        soup = BeautifulSoup(html, 'html.parser')
        if k: doc.add_page_break()
        for el in soup.children:
            if getattr(el, 'name', None):
                add_block(el)
    out = docx_path or OUT_DOCX
    if not out:
        raise ValueError('docx_path or OUT_DOCX must be set before calling build_docx')
    doc.save(out)

# ---------- PDF ----------
PRINT_CSS = '''
@page { size: A4; margin: 18mm 16mm 18mm 16mm;
        @bottom-center { content: counter(page); font-size: 9px; color: #777; } }
h1.chap { page-break-before: always; }
div.chap-lead { page-break-before: always; break-before: page; page-break-inside: avoid; break-inside: avoid; }
div.chap-lead h1.chap { page-break-before: avoid; break-before: avoid; }
body { font-size: 10.5pt; }
nav.toc ol { column-count: 2; }
pre { white-space: pre-wrap; word-break: break-word; }
table { table-layout: fixed; word-wrap: break-word; }
'''

def build_pdf(html_path=None, pdf_path=None):
    return render_pdf_with_fallback(html_path or OUT_HTML, pdf_path or OUT_PDF, PRINT_CSS)

SPLIT_VOLS = [
    ('1', f'{EDITION_VER}-LEARNER-P1-MayVaMa.pdf', f'SYSTEMS ATLAS ({EDITION_VER}) — TẬP 1: MÁY & MÃ'),
    ('2', f'{EDITION_VER}-LEARNER-P2-DuLieuVaGiaoTiep.pdf', f'SYSTEMS ATLAS ({EDITION_VER}) — TẬP 2: DỮ LIỆU & GIAO TIẾP'),
    ('3', f'{EDITION_VER}-LEARNER-P3-PhanTanCloudAnNinhVanHanh.pdf', f'SYSTEMS ATLAS ({EDITION_VER}) — TẬP 3: PHÂN TÁN, CLOUD, AN NINH, VẬN HÀNH'),
    ('4', f'{EDITION_VER}-LEARNER-P4-AIVaBienGioi.pdf', f'SYSTEMS ATLAS ({EDITION_VER}) — TẬP 4: AI & BIÊN GIỚI'),
    ('9', f'{EDITION_VER}-LEARNER-P5-PhuLuc.pdf', f'SYSTEMS ATLAS ({EDITION_VER}) — TẬP 5: PHỤ LỤC ĐỌC KHI CẦN'),
]

def build_split_pdfs(parts, stats, out_dir):
    """Xuất 5 tập PDF phân phần theo edu-order từ cùng bộ `parts`."""
    buckets = {k: [] for k, _, _ in SPLIT_VOLS}
    cur = '1'
    for item in parts:
        bn = os.path.basename(item[0])
        m = re.match(r'_PART-(\d)\.md$', bn)
        if m and m.group(1) in buckets:
            cur = m.group(1)
        buckets[cur].append(item)
    vols_dir = os.path.join(out_dir, 'volumes')
    os.makedirs(vols_dir, exist_ok=True)
    generated = []
    with tempfile.TemporaryDirectory() as td:
        for k, pdf_name, title in SPLIT_VOLS:
            sub_parts = buckets[k]
            sub_stats = dict(stats,
                             chapters=sum(1 for f, _, _, _ in sub_parts if not os.path.basename(f).startswith(('P15', '_PART'))),
                             edu=sum(1 for f, _, _, _ in sub_parts if os.path.basename(f).startswith('P15')),
                             words=sum(w for _, _, w, _ in sub_parts))
            html_doc = render_html_doc(sub_parts, sub_stats, title_override=title)
            tmp_html = os.path.join(td, f'vol_{k}.html')
            open(tmp_html, 'w', encoding='utf-8').write(html_doc)
            out_pdf = os.path.join(vols_dir, pdf_name)
            engine = build_pdf(tmp_html, out_pdf)
            generated.append((out_pdf, engine))
            print(f"SPLIT → volumes/{pdf_name} ({engine})")
    return generated

# ---------- main ----------
def main():
    want_pdf = '--no-pdf' not in sys.argv
    split_parts = '--split-parts' in sys.argv
    skip_pre = '--skip-preflight' in sys.argv
    out_dir = None
    if '--out-dir' in sys.argv:
        i = sys.argv.index('--out-dir')
        if i + 1 < len(sys.argv):
            out_dir = sys.argv[i + 1]
    profile = 'draft'
    if '--profile' in sys.argv:
        i = sys.argv.index('--profile')
        if i + 1 < len(sys.argv):
            profile = sys.argv[i + 1]
    if profile not in OUTS:
        print(f'[warn] profile lạ: {profile} — dùng draft'); profile = 'draft'
    set_profile(profile, out_dir=out_dir)
    if not skip_pre:
        preflight()
    files, parts, done, todo, words = assemble(profile)
    n_edu = sum(1 for f, _, _, _ in parts if os.path.basename(f).startswith('P15'))
    n_sep = sum(1 for f, _, _, _ in parts if os.path.basename(f).startswith('_PART'))
    stats = dict(profile=profile, chapters=len(files) - n_edu - n_sep, done=done, todo=todo, words=words,
                 edu=n_edu,
                 dec=csv_rows('coverage-decisions.csv'), inc=csv_rows('coverage-incidents.csv'))
    print(f"MD    → {os.path.basename(OUT_MD)} [{profile}]: {stats['chapters']} chapters, {done} written, {todo} todo, {words:,} words, {n_edu} edu files")
    ok = _ensure(['markdown', 'bs4', 'docx'])
    if ok.get('markdown'):
        build_html(parts, stats)
        print(f"HTML  → {os.path.basename(OUT_HTML)}")
    else:
        print("[warn] bỏ qua HTML (thiếu lib markdown)")
    if ok.get('docx') and ok.get('markdown'):
        try:
            build_docx(parts, stats)
            print(f"DOCX  → {os.path.basename(OUT_DOCX)}")
        except Exception as e:
            print(f"[warn] DOCX failed: {e}")
    if want_pdf and os.path.exists(OUT_HTML):
        engine = build_pdf()
        print(f"PDF   → {os.path.basename(OUT_PDF)} ({engine})")
        if split_parts and profile == 'edu':
            build_split_pdfs(parts, stats, OUT_DIR)

if __name__ == '__main__':
    main()
