#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export the 6 Vietnamese production Case Studies as Volume V in 4 formats (MD, HTML, DOCX, PDF)."""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import build  # noqa: E402
from tools import paths  # noqa: E402


def _parse_frontmatter(raw):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", raw, re.S)
    if not m:
        return {}, raw
    fm_txt, body = m.group(1), m.group(2).strip()
    meta = {}
    for line in fm_txt.splitlines():
        kv = re.match(r"^([a-zA-Z0-9_]+):\s*(.+)$", line.strip())
        if not kv:
            continue
        k, v = kv.group(1), kv.group(2).strip()
        if v.startswith('"') and v.endswith('"'):
            meta[k] = v[1:-1]
        elif v.startswith("[") and v.endswith("]"):
            meta[k] = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
        elif v.isdigit():
            meta[k] = int(v)
        else:
            meta[k] = v
    return meta, body


def _load_case_links():
    by_case = {}
    link_csv = os.path.join(paths.FACTS, "chapter-case-links.csv")
    for r in paths.read_csv_dicts(link_csv):
        by_case.setdefault(r["case_slug"], []).append(r)
    return by_case


def export_volume_v(out_dir=None, want_pdf=True):
    out_dir = out_dir or os.path.join(paths.DIST, "SA-2028.1-LEARNER", "cases")
    os.makedirs(out_dir, exist_ok=True)
    case_dir = os.path.join(paths.CONTENT_CASES, "vi")
    by_case = _load_case_links()

    loaded = []
    for fn in os.listdir(case_dir):
        if not fn.endswith(".md"):
            continue
        slug = fn[:-3]
        fpath = os.path.join(case_dir, fn)
        meta, body = _parse_frontmatter(open(fpath, encoding="utf-8").read())
        order = int(meta.get("order", 99))
        loaded.append((order, slug, fpath, meta, body))
    loaded.sort(key=lambda x: x[0])

    parts = []
    total_words = 0
    for order, slug, fpath, meta, body in loaded:
        title = meta.get("title", slug)
        desc = meta.get("description", "")
        field = meta.get("field", "SYS")
        topics = ", ".join(meta.get("topics", [])) if isinstance(meta.get("topics"), list) else str(meta.get("topics", ""))
        links = by_case.get(slug, [])
        link_lines = []
        if links:
            link_lines = ["\n\n## Liên kết Chương Sổ tay (Systems Atlas)\n", "| Chương | Điểm nối kỹ thuật |", "|---|---|"]
            for lk in links:
                link_lines.append(f"| `{lk['chapter']}` | {lk['vi_relation']} |")

        md_doc = (
            f"# Case {order} — {title}\n\n"
            f"> **Lĩnh vực:** `{field}` · **Chủ đề:** {topics}\n>\n> {desc}\n\n"
            f"{body}" + ("\n".join(link_lines) if link_lines else "")
        )
        words = len(md_doc.split())
        total_words += words
        parts.append((fpath, md_doc, words, True))

    base_name = "SYSTEMS-ATLAS-VOLUME-5-CASES"
    out_md = os.path.join(out_dir, f"{base_name}.md")
    out_html = os.path.join(out_dir, f"{base_name}.html")
    out_docx = os.path.join(out_dir, f"{base_name}.docx")
    out_pdf = os.path.join(out_dir, f"{base_name}.pdf")

    header = (
        "# SYSTEMS ATLAS (SA-2028.1) — TẬP V: 6 CASE STUDIES THỰC CHIẾN\n\n"
        f"> Tuyển tập {len(parts)} hệ thống đã vận hành (học máy, tìm kiếm, edge AI, chuỗi thời gian, bài học vận hành) · {total_words:,} từ.\n\n---\n\n"
    )
    open(out_md, "w", encoding="utf-8", newline="\n").write(header + "\n\n---\n\n".join(p[1] for p in parts) + "\n")

    stats = dict(profile="edu", chapters=len(parts), done=len(parts), todo=0, words=total_words, edu=0, dec=0, inc=0)
    html_text = build.render_html_doc(
        parts,
        stats,
        title_override="SYSTEMS ATLAS (SA-2028.1) — TẬP V: 6 CASE STUDIES THỰC CHIẾN",
    )
    open(out_html, "w", encoding="utf-8", newline="\n").write(html_text)

    old_docx, old_html, old_pdf = build.OUT_DOCX, build.OUT_HTML, build.OUT_PDF
    try:
        build.OUT_DOCX = out_docx
        build.OUT_HTML = out_html
        build.OUT_PDF = out_pdf
        build.build_docx(parts, stats)
        engine = build.build_pdf(out_html, out_pdf) if want_pdf else "skipped"
    finally:
        build.OUT_DOCX, build.OUT_HTML, build.OUT_PDF = old_docx, old_html, old_pdf

    return dict(cases=len(parts), words=total_words, out_dir=out_dir, engine=engine)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()
    res = export_volume_v(out_dir=args.out_dir, want_pdf=not args.no_pdf)
    print(f"VOLUME V CASES: {res['cases']} cases · {res['words']:,} words · PDF ({res['engine']}) -> {res['out_dir']}")


if __name__ == "__main__":
    main()
