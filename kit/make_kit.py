#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dựng SA-2028.1-KIT ra html · pdf · docx từ các tệp markdown trong thư mục này.
   uv run python kit/make_kit.py
"""
import os, re, sys, datetime, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.paths import DIST  # noqa: E402
from tools.pdf_render import render_pdf_with_fallback  # noqa: E402

ORDER = ['00-DOC-TRUOC.md', '01-MON-1-NEN-TANG.md', '02-MON-2-HE-THONG-THUC.md',
         '02b-MON-3-QUY-MO-BIEN-GIOI.md', '03-SIEU-DAI-CUONG-15-TIET.md',
         '04-NGAN-HANG-DE-THI.md', '05-RUBRIC-VA-CHAM-BAI.md']


def files():
    out = []
    for f in ORDER:
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            out.append(p)
    return out


TITLE = 'SA-2028.1 KIT — BỘ MÔN HỌC'
SUB = ('Biến SYSTEMS ATLAS (145 chương) thành chương trình dạy được: '
       '2 môn bắt buộc + 1 môn tự chọn + 1 môn siêu đại cương + ngân hàng đề + rubric')
DATE = datetime.date.today().isoformat()


def combine():
    parts = []
    for p in files():
        parts.append(open(p, encoding='utf-8').read().strip())
    return '\n\n---\n\n'.join(parts)


CSS = """
@page { size: A4; margin: 18mm 16mm 16mm 16mm;
        @bottom-center { content: counter(page); font-size: 9pt; color: #666; } }
body { font-family: "Noto Serif", "DejaVu Serif", "Times New Roman", serif; font-size: 10.5pt; line-height: 1.45; color: #111; }
h1.title { font-size: 26pt; margin: 60mm 0 4mm 0; letter-spacing: .5px; }
p.sub { font-size: 12pt; color: #444; margin: 0 0 6mm 0; }
p.meta { font-size: 10pt; color: #666; }
h1 { font-size: 17pt; margin: 12mm 0 3mm 0; page-break-before: always; border-bottom: 2px solid #111; padding-bottom: 2mm; }
h2 { font-size: 13pt; margin: 7mm 0 2mm 0; }
h3 { font-size: 11.5pt; margin: 5mm 0 1.5mm 0; }
table { border-collapse: collapse; width: 100%; font-size: 8.8pt; margin: 3mm 0; }
th, td { border: 1px solid #bbb; padding: 1.4mm 2mm; vertical-align: top; }
th { background: #f0f0f0; text-align: left; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.8pt; background: #f4f4f4; padding: 0 1px; }
pre { background: #f6f6f6; border-left: 3px solid #ccc; padding: 2mm 3mm; font-size: 8.5pt; overflow-wrap: break-word; }
blockquote { border-left: 3px solid #333; margin: 3mm 0; padding: 1mm 0 1mm 4mm; color: #222; background: #fafafa; }
hr { border: 0; border-top: 1px dashed #bbb; margin: 6mm 0; }
ul, ol { margin: 2mm 0 2mm 6mm; }
li { margin: 1mm 0; }
"""


def build_html(md):
    import markdown
    body = markdown.markdown(combine(), extensions=['tables', 'fenced_code', 'sane_lists'])
    head = ('<h1 class="title">%s</h1>\n<p class="sub">%s</p>\n<p class="meta">%s · %d tệp · build %s</p>\n<hr/>\n'
            % (TITLE, SUB, DATE, len(files()), datetime.date.today().isoformat()))
    return ('<!doctype html><html lang="vi"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex, notranslate">'
            '<title>%s</title><style>%s</style></head><body>%s%s</body></html>'
            % (TITLE, CSS.replace('@page', '/*@page*/'), head, body)), head, body


def build_pdf(html_full, path):
    with tempfile.TemporaryDirectory() as td:
        tmp_html = os.path.join(td, 'render.html')
        open(tmp_html, 'w', encoding='utf-8').write(html_full)
        return render_pdf_with_fallback(tmp_html, path, CSS)


# ---------- DOCX ----------
def _runs(par, text, mono=False):
    """**bold**, `code`, *italic*"""
    for tok in re.split(r'(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)', text):
        if not tok:
            continue
        if tok.startswith('**') and tok.endswith('**'):
            r = par.add_run(tok[2:-2]); r.bold = True
        elif tok.startswith('`') and tok.endswith('`'):
            r = par.add_run(tok[1:-1]); r.font.name = 'Consolas'; r.font.size = None
        elif tok.startswith('*') and tok.endswith('*') and len(tok) > 2:
            r = par.add_run(tok[1:-1]); r.italic = True
        else:
            par.add_run(tok)


def build_docx(md, path):
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    doc = Document()
    doc.styles['Normal'].font.name = 'Georgia'
    doc.styles['Normal'].font.size = Pt(10.5)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(1.8); s.left_margin = s.right_margin = Cm(1.6)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(TITLE); r.bold = True; r.font.size = Pt(24)
    p = doc.add_paragraph(); _runs(p, SUB)
    doc.add_paragraph('%s · %d tệp · build %s' % (DATE, len(files()), datetime.date.today().isoformat()))
    doc.add_page_break()

    lines = combine().split('\n')
    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s or s in ('---', '***'):
            i += 1; continue
        # bảng
        if s.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[i + 1].strip()):
            header = [c.strip() for c in s.strip('|').split('|')]
            rows = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            t = doc.add_table(rows=1, cols=len(header)); t.style = 'Light Grid Accent 1'
            for k, h in enumerate(header):
                cell = t.rows[0].cells[k]; cell.text = ''
                _runs(cell.paragraphs[0], h)
                for run in cell.paragraphs[0].runs:
                    run.bold = True
            for row in rows:
                cells = t.add_row().cells
                for k, c in enumerate(row[:len(header)]):
                    cells[k].text = ''
                    _runs(cells[k].paragraphs[0], c)
            continue
        if s.startswith('```'):
            buf = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                buf.append(lines[i]); i += 1
            i += 1
            p = doc.add_paragraph()
            r = p.add_run('\n'.join(buf)); r.font.name = 'Consolas'; r.font.size = Pt(8.5)
            continue
        m = re.match(r'^(#{1,4})\s+(.*)$', s)
        if m:
            lvl = len(m.group(1))
            h = doc.add_heading(level=min(lvl, 4))
            _runs(h, m.group(2))
            i += 1; continue
        if s.startswith('> '):
            buf = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip().lstrip('>').strip()); i += 1
            p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.6)
            _runs(p, ' '.join(buf))
            for r in p.runs:
                r.italic = True
            continue
        m = re.match(r'^([-*])\s+(.*)$', s)
        if m:
            p = doc.add_paragraph(style='List Bullet'); _runs(p, m.group(2)); i += 1; continue
        m = re.match(r'^(\d+)\.\s+(.*)$', s)
        if m:
            p = doc.add_paragraph(style='List Number'); _runs(p, m.group(2)); i += 1; continue
        p = doc.add_paragraph(); _runs(p, s); i += 1
    doc.save(path)


def main():
    out_dir = os.path.join(DIST, 'SA-2028.1-KIT')
    os.makedirs(out_dir, exist_ok=True)
    md = combine()
    base = 'SA-2028.1-KIT'
    open(os.path.join(out_dir, f'{base}.md'), 'w', encoding='utf-8').write(
        '# %s\n\n> %s\n> %s · %s\n\n---\n\n%s\n' % (TITLE, SUB, DATE, 'build ' + datetime.date.today().isoformat(), md))
    html_full, head, body = build_html(md)
    open(os.path.join(out_dir, f'{base}.html'), 'w', encoding='utf-8').write(html_full)
    build_pdf(html_full, os.path.join(out_dir, f'{base}.pdf'))
    build_docx(md, os.path.join(out_dir, f'{base}.docx'))
    for f in [f'{base}.md', f'{base}.html', f'{base}.pdf', f'{base}.docx']:
        p = os.path.join(out_dir, f)
        print('%-24s %.1f KB' % (f, os.path.getsize(p) / 1024))


if __name__ == '__main__':
    main()
