#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared HTML -> PDF renderer with Windows Edge fallback and PyMuPDF bookmark injection."""
import os
import re
import shutil
import subprocess
import tempfile

from bs4 import BeautifulSoup
import pymupdf

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]


def _find_browser():
    for exe in ("msedge", "chrome"):
        hit = shutil.which(exe)
        if hit:
            return hit
    for p in EDGE_PATHS:
        if os.path.exists(p):
            return p
    return None


def _norm_txt(s):
    s = re.sub(r"\s+", " ", (s or "")).strip().lower()
    return s


def _extract_headings_from_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    toc = soup.find("nav", class_="toc")
    last_toc_norm = ""
    if toc is not None:
        links = toc.find_all("a")
        if links:
            last_toc_norm = _norm_txt(links[-1].get_text(" ", strip=True))
    for nav in soup.find_all("nav"):
        nav.decompose()
    for hdr in soup.find_all("header"):
        hdr.decompose()
    out = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        txt = re.sub(r"\s+", " ", tag.get_text(" ", strip=True)).strip()
        if txt:
            out.append((int(tag.name[1]), txt))
    return out, last_toc_norm


def _inject_bookmarks(pdf_path, headings, last_toc_norm=""):
    if not headings:
        return 0
    doc = pymupdf.open(pdf_path)
    if doc.page_count == 0:
        doc.close()
        return 0
    page_norms = [_norm_txt(doc[i].get_text("text")) for i in range(doc.page_count)]

    cur_page = 0
    if last_toc_norm and doc.page_count > 1:
        toc_needle = last_toc_norm[:48]
        toc_words = " ".join(last_toc_norm.split()[:5])
        for pno, pn in enumerate(page_norms):
            if toc_needle in pn or (len(toc_words) >= 8 and toc_words in pn):
                cur_page = min(pno + 1, doc.page_count - 1)
                break

    toc = []
    prev_lvl = 0
    for raw_lvl, title in headings:
        needle_full = _norm_txt(title)
        needle_short = needle_full[:48]
        needle_words = " ".join(needle_full.split()[:5])
        matched = None
        for pno in range(cur_page, doc.page_count):
            pn = page_norms[pno]
            if needle_full in pn or (len(needle_short) >= 8 and needle_short in pn) or (
                len(needle_words) >= 8 and needle_words in pn
            ):
                matched = pno
                break
        if matched is not None:
            cur_page = matched
        lvl = 1 if prev_lvl == 0 else min(raw_lvl, prev_lvl + 1)
        prev_lvl = lvl
        toc.append([lvl, title, cur_page + 1])

    doc.set_toc(toc)
    tmp_out = pdf_path + ".toc.tmp.pdf"
    doc.save(tmp_out, garbage=2, deflate=True)
    doc.close()
    os.replace(tmp_out, pdf_path)
    return len(toc)


def render_pdf_with_fallback(html_path, pdf_path, print_css=""):
    """Render html_path to pdf_path via WeasyPrint if usable, else headless Edge + PyMuPDF TOC."""
    os.makedirs(os.path.dirname(os.path.abspath(pdf_path)), exist_ok=True)
    html_text = open(html_path, encoding="utf-8").read()

    # 1. Try WeasyPrint first (works natively on Linux/macOS or Windows with GTK3)
    try:
        from weasyprint import HTML
        from weasyprint.css import CSS as WCSS

        no_cover_bm = WCSS(string="header.cover h1, nav.toc h2 { bookmark-level: none; }")
        stylesheets = [no_cover_bm] + ([WCSS(string=print_css)] if print_css else [])
        HTML(string=html_text, base_url=os.path.dirname(os.path.abspath(html_path))).write_pdf(
            pdf_path, stylesheets=stylesheets
        )
        # Ensure Cover/TOC headings on page 1 never leak as first bookmark
        wdoc = pymupdf.open(pdf_path)
        wtoc = wdoc.get_toc()
        filtered = [row for row in wtoc if not (row[2] <= 2 and ("SYSTEMS ATLAS" in row[1] or row[1].strip().lower() == "mục lục"))]
        if filtered and len(filtered) != len(wtoc):
            base_lvl = filtered[0][0]
            norm_toc = [[max(1, r[0] - base_lvl + 1), r[1], r[2]] for r in filtered]
            wdoc.set_toc(norm_toc)
            wtmp = pdf_path + ".weasy.tmp.pdf"
            wdoc.save(wtmp, garbage=2, deflate=True)
            wdoc.close()
            os.replace(wtmp, pdf_path)
        else:
            wdoc.close()
        return "weasyprint"
    except (ImportError, OSError, RuntimeError):
        pass

    # 2. Fallback: Chromium/Edge headless print-to-pdf + PyMuPDF bookmark injection
    browser = _find_browser()
    if not browser:
        raise RuntimeError("Neither WeasyPrint native libs nor Edge/Chrome binary available for PDF render")

    injected_html = html_text
    if print_css and "</head>" in html_text:
        injected_html = html_text.replace("</head>", f"<style>{print_css}</style></head>", 1)

    with tempfile.TemporaryDirectory() as td:
        tmp_html = os.path.join(td, "render.html")
        open(tmp_html, "w", encoding="utf-8").write(injected_html)
        uri = "file:///" + tmp_html.replace(os.sep, "/")
        cmd = [
            browser,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={os.path.abspath(pdf_path)}",
            uri,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        if res.returncode != 0 or not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            raise RuntimeError(f"Headless browser PDF failed (rc={res.returncode}): {res.stderr[:300]}")

    headings, last_toc_norm = _extract_headings_from_html(html_text)
    _inject_bookmarks(pdf_path, headings, last_toc_norm=last_toc_norm)
    return "edge+pymupdf"
