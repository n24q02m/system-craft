import os
import re
import sys

import docx
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import edu_order_check as eoc  # noqa: E402

SYS101_STARS = ["0.2", "1.1", "1.2", "1.4", "1.7", "2.1", "2.3", "2.4", "3.1", "3.10", "4.1"]


def _extract_chapters_from_syllabus(md_path):
    txt = open(md_path, encoding="utf-8").read()
    m = re.search(r"## 2\. Lịch 15 tuần.*?(?=^\*\*|## 3\.)", txt, re.S | re.M)
    assert m, f"Missing 15-week table in {md_path}"
    chaps = []
    for row in m.group().splitlines():
        if not row.startswith("|") or row.startswith(("| Tuần", "|---")):
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) >= 2:
            # Handle compressed notation like 5.1–5.2·5.4 or 10.3–10.4 or 14.1.1–14.1.3
            col = cells[1]
            # First expand explicit dotted ranges like 14.1.1–14.1.3 or 10.3–10.4 or 8.1–8.3 or 5.15–5.16
            for rng in re.finditer(r"(\d+\.\d+\.)(\d+)[–-]\1(\d+)", col):
                prefix, a, b = rng.group(1), int(rng.group(2)), int(rng.group(3))
                for k in range(a, b + 1):
                    chaps.append(f"{prefix}{k}")
                col = col.replace(rng.group(0), " ")
            for rng in re.finditer(r"\b(\d+)\.(\d+)[–-]\1\.(\d+)\b", col):
                p, a, b = int(rng.group(1)), int(rng.group(2)), int(rng.group(3))
                for k in range(a, b + 1):
                    chaps.append(f"{p}.{k}")
                col = col.replace(rng.group(0), " ")
            for tok in re.findall(r"\b\d+\.\d+(?:\.\d+)?\b", col):
                chaps.append(tok)
    # preserve unique order
    seen = []
    for c in chaps:
        if c not in seen:
            seen.append(c)
    return seen


def test_kit_syllabus_coverage_and_no_overlap():
    all_files = eoc.chapter_files()
    cmap = {eoc.file_to_chapter(fn): fn for fn in all_files}
    assert len(cmap) == 145

    doc_truoc = open(os.path.join(ROOT, "kit", "00-DOC-TRUOC.md"), encoding="utf-8").read()
    assert "| **34** |" not in doc_truoc
    assert "SA-2028.1" in doc_truoc
    assert "15/15" in doc_truoc or "15 bộ lab" in doc_truoc
    assert "02b" in doc_truoc

    s1 = _extract_chapters_from_syllabus(os.path.join(ROOT, "kit", "01-MON-1-NEN-TANG.md"))
    s2 = _extract_chapters_from_syllabus(os.path.join(ROOT, "kit", "02-MON-2-HE-THONG-THUC.md"))
    s3 = _extract_chapters_from_syllabus(os.path.join(ROOT, "kit", "02b-MON-3-QUY-MO-BIEN-GIOI.md"))

    assert len(s1) == 45, f"SYS101={len(s1)}: {s1}"
    assert len(s2) == 45, f"SYS102={len(s2)}: {s2}"
    assert len(s3) == 45, f"SYS103={len(s3)}: {s3}"
    assert set(s1).isdisjoint(s2)
    assert set(s1).isdisjoint(s3)
    assert set(s2).isdisjoint(s3)
    rem = set(cmap) - (set(s1) | set(s2) | set(s3))
    assert len(rem) == 10
    assert all(r.startswith("14.") for r in rem)

    # Check SYS103 prereqs lie inside SYS101|SYS102|SYS103
    allowed = set(s1) | set(s2) | set(s3)
    for ch in s3:
        refs = eoc.doc_truoc_refs(cmap[ch]) or []
        bad = [r for r in refs if r not in allowed]
        assert bad == [], f"SYS103 chapter {ch} has dangling prereq outside 3 courses: {bad}"


def test_build_kit_4_formats():
    kdir = os.path.join(ROOT, "dist", "SA-2028.1-KIT")
    for ext in ("md", "html", "docx", "pdf"):
        p = os.path.join(kdir, f"SA-2028.1-KIT.{ext}")
        assert os.path.exists(p) and os.path.getsize(p) > 0, f"Missing {p}"
    md_txt = open(os.path.join(kdir, "SA-2028.1-KIT.md"), encoding="utf-8").read()
    assert "# MÔN 3 — QUY MÔ & BIÊN GIỚI" in md_txt
    d = docx.Document(os.path.join(kdir, "SA-2028.1-KIT.docx"))
    assert len(d.paragraphs) > 100
    pdf = pymupdf.open(os.path.join(kdir, "SA-2028.1-KIT.pdf"))
    assert pdf.page_count >= 15
    assert "SYS103" in "\n".join(pdf[i].get_text("text") for i in range(pdf.page_count))
    pdf.close()


def test_slides_11_backbone_chapters():
    sdir = os.path.join(ROOT, "kit", "slides")
    for ext in ("md", "html", "pdf"):
        p = os.path.join(sdir, f"SYS101-11-chuong-xuong-song.{ext}")
        assert os.path.exists(p) and os.path.getsize(p) > 0, f"Missing {p}"
    md_txt = open(os.path.join(sdir, "SYS101-11-chuong-xuong-song.md"), encoding="utf-8").read()
    slides = [s.strip() for s in re.split(r"^---\s*$", md_txt, flags=re.M) if s.strip()]
    assert 66 <= len(slides) <= 95, f"Slide count={len(slides)}"
    for star in SYS101_STARS:
        assert re.search(rf"\b{re.escape(star)}\b", md_txt), f"Missing ★ chapter {star} in slides"
    html_txt = open(os.path.join(sdir, "SYS101-11-chuong-xuong-song.html"), encoding="utf-8").read()
    assert "http://" not in html_txt and "https://" not in html_txt
    pdf = pymupdf.open(os.path.join(sdir, "SYS101-11-chuong-xuong-song.pdf"))
    assert pdf.page_count >= 66
    pdf.close()
