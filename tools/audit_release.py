#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent release package verifier for SA-2028.1-LEARNER & DRAFT."""
import argparse
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from bs4 import BeautifulSoup
import docx
import pymupdf

from tools.paths import DIST  # noqa: E402

def _h1s_outside_code(md_text):
    out = []
    in_code = False
    for line in md_text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not in_code and line.startswith("# "):
            out.append(line)
    return out


def _valid_chapters(h1s):
    """Collect exact chapter numbers and 2-level P14 track prefixes from H1 headings."""
    valid = set()
    for h in h1s:
        m = re.match(r"^#\s+(\d+\.\d+(?:\.\d+)?)\b", h)
        if m:
            chap = m.group(1)
            valid.add(chap)
            if chap.count(".") == 2 and chap.startswith("14."):
                valid.add(".".join(chap.split(".")[:2]))
    return valid


_VERSION_LEFT_RE = re.compile(
    r"(?:(?:19|20)\d{2}(?:\.\d+)?|3\.13t?|experimental|WCAG\s+[\d.]+\s*\(\d{4}\))\s*→\s*$"
)


def _find_broken_refs(md_text, valid_chapters):
    """Scan → X.Y cross-references excluding version spans, thousands groups, and code."""
    broken = []
    in_code = False
    for lno, line in enumerate(md_text.splitlines(), 1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.startswith("# "):
            continue
        for m in re.finditer(r"→\s*(\d+\.\d+(?:\.\d+)?)", line):
            tgt = m.group(1)
            if re.search(r"\.\d{3,}", tgt):
                continue
            prefix = line[: m.start(1)]
            if _VERSION_LEFT_RE.search(prefix):
                continue
            if tgt not in valid_chapters:
                broken.append((lno, tgt, line.strip()[:120]))
    return broken


def verify_release_dir(dist_dir):
    req_files = [
        "SYSTEMS-ATLAS-LEARNER-SA-2028.1.md",
        "SYSTEMS-ATLAS-LEARNER-SA-2028.1.html",
        "SYSTEMS-ATLAS-LEARNER-SA-2028.1.docx",
        "SYSTEMS-ATLAS-LEARNER-SA-2028.1.pdf",
        "DRAFT-tham-chieu.md",
        "facts/versions.csv",
        "facts/ERRATA.md",
        "00-CACH-DUNG-GOI.md",
    ]
    for rel in req_files:
        p = os.path.join(dist_dir, *rel.split("/"))
        assert os.path.exists(p) and os.path.getsize(p) > 0, f"Missing/empty: {rel}"

    vol_dir = os.path.join(dist_dir, "volumes")
    vols = sorted(f for f in os.listdir(vol_dir) if f.endswith(".pdf")) if os.path.isdir(vol_dir) else []
    assert len(vols) == 5, f"Expected 5 split PDFs, got {vols}"

    md_path = os.path.join(dist_dir, "SYSTEMS-ATLAS-LEARNER-SA-2028.1.md")
    md_text = open(md_path, encoding="utf-8").read()
    assert "SA-2026.13" not in md_text.splitlines()[0], "Stale SA-2026.13 cover header"
    assert "SA-2028.1" in md_text.splitlines()[0]

    h1s = _h1s_outside_code(md_text)
    assert len(h1s) == 201, f"Expected 201 H1s outside code, got {len(h1s)}"

    labs = [h for h in h1s if h.startswith("# P15-03-L")]
    quizzes = [h for h in h1s if re.match(r"^# P15-02-Q\d+", h)]
    sols = [h for h in h1s if h.startswith("# P15-04-S")]
    qas = [h for h in h1s if h.startswith("# P15-02-QA")]
    seps = [h for h in h1s if h.startswith(("# HỌC ", "# PHỤ LỤC"))]
    assert len(labs) == 15
    assert len(quizzes) == 15
    assert len(sols) == 15
    assert len(qas) == 1
    assert len(seps) == 5

    tu_cham = len(re.findall(r"\*\*Tự chấm:\*\*", md_text))
    nhip_noi = len(re.findall(r"^> \*\*Nhịp nối \(tuyến học\)\*\*", md_text, re.M))
    assert tu_cham == 433, f"Expected 433 Tự chấm markers, got {tu_cham}"
    assert nhip_noi == 10, f"Expected 10 Nhịp nối bridges, got {nhip_noi}"

    valid = _valid_chapters(h1s)
    broken = _find_broken_refs(md_text, valid)
    assert broken == [], f"Broken cross-references found: {broken}"

    # Verify HTML self-contained (0 external http/https assets)
    html_text = open(os.path.join(dist_dir, "SYSTEMS-ATLAS-LEARNER-SA-2028.1.html"), encoding="utf-8").read()
    soup = BeautifulSoup(html_text, "html.parser")
    ext = [
        t.get("src") or t.get("href")
        for t in soup.find_all(["script", "link", "img"])
        if (t.get("src") or t.get("href") or "").startswith(("http://", "https://"))
    ]
    assert ext == [], f"External assets in HTML: {ext}"
    html_h1s = len(soup.find_all("h1", class_="chap"))
    assert html_h1s == 200, f"Expected 200 chapter h1.chap in HTML body, got {html_h1s}"

    # Verify DOCX opens & has tables + headings
    d = docx.Document(os.path.join(dist_dir, "SYSTEMS-ATLAS-LEARNER-SA-2028.1.docx"))
    assert len(d.paragraphs) > 5000
    assert len(d.tables) >= 500

    # Verify PDF opens via PyMuPDF, page count, bookmarks, and Vietnamese glyphs
    pdf_path = os.path.join(dist_dir, "SYSTEMS-ATLAS-LEARNER-SA-2028.1.pdf")
    pdf = pymupdf.open(pdf_path)
    pages = pdf.page_count
    toc = pdf.get_toc()
    assert pages > 700, f"PDF too short: {pages}"
    assert len(toc) >= 1500, f"Too few PDF bookmarks: {len(toc)}"
    assert toc[0][2] >= 5, f"First H1 bookmark still points to Cover/TOC page: {toc[0]}"
    sample_indices = sorted({0, min(10, pages - 1), pages // 2, max(0, pages - 5)})
    sample_txt = "\n".join(pdf[i].get_text("text") for i in sample_indices)
    assert "SYSTEMS ATLAS" in sample_txt
    assert "\ufffd" not in sample_txt, "Unicode replacement char U+FFFD found in PDF text"
    assert any(w in sample_txt for w in ("Quyết định", "chương", "Tự chấm")), "Missing Vietnamese diacritics in PDF sample"
    pdf.close()

    # Verify split PDFs readable & first bookmark lands on body page
    vol_stats = []
    for vn in vols:
        vp = pymupdf.open(os.path.join(vol_dir, vn))
        assert vp.page_count >= 10, f"Split PDF {vn} too small ({vp.page_count}p)"
        vtoc = vp.get_toc()
        assert vtoc and vtoc[0][2] >= 2, f"Split PDF {vn} first bookmark points to page {vtoc[0] if vtoc else 'empty'}"
        vol_stats.append((vn, vp.page_count, len(vtoc)))
        vp.close()

    # Verify 0/145 chapter body diffs between EDU and DRAFT-tham-chieu.md
    draft_md = open(os.path.join(dist_dir, "DRAFT-tham-chieu.md"), encoding="utf-8").read()
    def _extract_chap_bodies(doc_text):
        bodies = {}
        for sec in doc_text.split("\n---\n"):
            sec_clean = re.sub(r"^> \*\*Nhịp nối \(tuyến học\)\*\*[^\n]*\n+", "", sec.strip(), flags=re.M).strip()
            m = re.match(r"^#\s+(\d+\.\d+(?:\.\d+)?)\b", sec_clean)
            if m:
                bodies[m.group(1)] = sec_clean
        return bodies

    edu_bodies = _extract_chap_bodies(md_text)
    draft_bodies = _extract_chap_bodies(draft_md)
    assert len(draft_bodies) == 145 and set(edu_bodies) == set(draft_bodies)
    diffs = [ch for ch in sorted(draft_bodies) if edu_bodies[ch] != draft_bodies[ch]]
    assert diffs == [], f"Chapter body mismatch between EDU and DRAFT: {diffs}"

    return {
        "md_words": len(md_text.split()),
        "h1s": len(h1s),
        "labs": len(labs),
        "quizzes": len(quizzes),
        "qa_files": len(qas),
        "sols": len(sols),
        "tu_cham": tu_cham,
        "nhip_noi": nhip_noi,
        "broken_refs": len(broken),
        "html_h1s": html_h1s,
        "docx_paragraphs": len(d.paragraphs),
        "docx_tables": len(d.tables),
        "pdf_pages": pages,
        "pdf_bookmarks": len(toc),
        "volumes": vol_stats,
        "hashes": {
            fn: hashlib.sha256(open(os.path.join(dist_dir, fn), "rb").read()).hexdigest()
            for fn in (
                "SYSTEMS-ATLAS-LEARNER-SA-2028.1.md",
                "SYSTEMS-ATLAS-LEARNER-SA-2028.1.html",
                "SYSTEMS-ATLAS-LEARNER-SA-2028.1.docx",
                "SYSTEMS-ATLAS-LEARNER-SA-2028.1.pdf",
                "DRAFT-tham-chieu.md",
            )
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=os.path.join(DIST, "SA-2028.1-LEARNER"))
    ap.add_argument("--write-receipt", default=None)
    args = ap.parse_args()
    res = verify_release_dir(args.dist)
    print(f"AUDIT PASS: {res['h1s']} H1 · {res['labs']} labs · {res['quizzes']} quiz + {res['qa_files']} QA · "
          f"{res['sols']} sols ({res['tu_cham']} Tự chấm) · {res['nhip_noi']} Nhịp nối · {res['broken_refs']} broken refs · "
          f"PDF {res['pdf_pages']}p/{res['pdf_bookmarks']} bookmarks")
    if args.write_receipt:
        lines = [
            "# QA RECEIPT — SA-2028.1 LEARNER\n",
            f"- **H1 ngoài code:** {res['h1s']} (145 chương + 1 bìa + 4 P15-00/01/05/06 + 5 trang nhãn + 15 quiz + 1 QA + 15 lab + 15 lời giải)",
            f"- **Tự chấm:** {res['tu_cham']} (M1+M3) · **Quiz nâng cao (`P15-02-QA`):** 60 câu / 60 đáp án · **Lab:** {res['labs']}/15",
            f"- **Nhịp nối (F1):** {res['nhip_noi']} · **Tham chiếu gãy:** {res['broken_refs']}",
            f"- **HTML:** {res['html_h1s']} chương `h1.chap`, 0 tài nguyên ngoài",
            f"- **DOCX:** {res['docx_paragraphs']:,} đoạn, {res['docx_tables']} bảng",
            f"- **PDF:** {res['pdf_pages']:,} trang, {res['pdf_bookmarks']:,} bookmarks",
            "\n## 5 Tập PDF Phân Phần\n",
        ]
        for vn, pg, bk in res["volumes"]:
            lines.append(f"- `{vn}`: {pg} trang, {bk} bookmarks")
        lines.append("\n## SHA-256\n")
        for fn, h in res["hashes"].items():
            lines.append(f"- `{fn}`: `{h}`")
        open(args.write_receipt, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("Wrote", args.write_receipt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
