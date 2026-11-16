#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build self-contained HTML and 16:9 widescreen PDFs for SYS101, SYS102, and SYS103 slide decks."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import markdown  # noqa: E402
from tools.pdf_render import render_pdf_with_fallback  # noqa: E402

DECKS = [
    ("SYS101-11-chuong-xuong-song", "SYS101 — Bộ Slide 11 Chương Xương Sống (★)", "SYS101"),
    ("SYS102-10-chuong-xuong-song", "SYS102 — Bộ Slide 10 Chương Xương Sống (★)", "SYS102"),
    ("SYS103-09-chuong-xuong-song", "SYS103 — Bộ Slide 09 Chương Xương Sống (★)", "SYS103"),
]

SLIDE_CSS = """
@page { size: 254mm 142.9mm; margin: 7mm 11mm 7mm 11mm; }
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0; background: #ffffff; color: #16181d;
  font-family: "DejaVu Sans", "Segoe UI", Arial, sans-serif;
  font-size: 10.8pt; line-height: 1.32;
}
.deck { width: 100%; }
section.slide {
  padding: 2mm 1.5mm 1mm 1.5mm;
  page-break-after: always; break-after: page;
  page-break-inside: avoid; break-inside: avoid;
  position: relative;
}
section.slide:last-child { page-break-after: auto; break-after: auto; }
section.slide h1 {
  font-size: 20pt; color: #0b5fff; border-bottom: 3px solid #0b5fff;
  padding-bottom: 2.5mm; margin: 4mm 0 4mm 0;
}
section.slide h2 {
  font-size: 14.2pt; color: #0f172a; border-bottom: 2px solid #cbd5e1;
  padding-bottom: 1.5mm; margin: 0 0 2.8mm 0;
}
blockquote {
  border-left: 4px solid #0b5fff; background: #f1f5f9;
  margin: 2mm 0; padding: 1.8mm 3.5mm; color: #1e293b; font-size: 10.2pt;
}
table {
  border-collapse: collapse; width: 100%; margin: 1.8mm 0; font-size: 9.4pt; line-height: 1.24;
}
th, td { border: 1px solid #cbd5e1; padding: 1.1mm 2mm; text-align: left; vertical-align: top; }
th { background: #e2e8f0; color: #0f172a; font-weight: 700; }
tr:nth-child(even) td { background: #f8fafc; }
code {
  font-family: "Consolas", "DejaVu Sans Mono", monospace;
  background: #f1f5f9; padding: 0.2mm 1mm; border-radius: 3px; font-size: 9.4pt;
}
pre {
  background: #0f172a; color: #e2e8f0; padding: 2.4mm 3.2mm; border-radius: 5px;
  font-size: 9.2pt; line-height: 1.25; overflow-x: auto; margin: 2mm 0;
}
pre code { background: transparent; color: inherit; padding: 0; }
ul, ol { margin: 2mm 0 2mm 5.5mm; padding: 0; }
li { margin: 1mm 0; }
.footer {
  margin-top: 2mm; font-size: 8pt; color: #64748b; text-align: right;
}
"""


def build_deck(stem, title, course):
    md_path = os.path.join(HERE, f"{stem}.md")
    html_path = os.path.join(HERE, f"{stem}.html")
    pdf_path = os.path.join(HERE, f"{stem}.pdf")

    raw = open(md_path, encoding="utf-8").read()
    slides_md = [s.strip() for s in re.split(r"^---\s*$", raw, flags=re.M) if s.strip()]
    conv = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    blocks = []
    total = len(slides_md)
    for i, smd in enumerate(slides_md, 1):
        frag = conv.reset().convert(smd)
        blocks.append(f'<section class="slide">\n{frag}\n<div class="footer">{course} (SA-2028.1) · Slide {i}/{total}</div>\n</section>')

    html_doc = (
        "<!doctype html>\n<html lang=\"vi\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"robots\" content=\"noindex, nofollow, noarchive, nosnippet, noimageindex, notranslate\">\n"
        f"<title>{title}</title>\n"
        f"<style>{SLIDE_CSS}</style>\n</head>\n<body><div class=\"deck\">\n"
        + "\n".join(blocks)
        + "\n</div></body>\n</html>\n"
    )
    open(html_path, "w", encoding="utf-8", newline="\n").write(html_doc)
    backend = render_pdf_with_fallback(html_path, pdf_path, SLIDE_CSS)
    print(f"SLIDES {course} ({backend}): {total} slides -> {os.path.basename(html_path)} & {os.path.basename(pdf_path)}")
    return total


def build_slides():
    counts = {}
    for stem, title, course in DECKS:
        counts[course] = build_deck(stem, title, course)
    return counts


if __name__ == "__main__":
    build_slides()
