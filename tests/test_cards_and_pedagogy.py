import json
import pathlib
import re
import sys

import docx
import pymupdf

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_cards_flashcards_and_3_indexes_generated():
    gen = ROOT / "content" / "generated"
    cards_md = gen / "cards-145.md"
    fc_json = gen / "flashcards.json"
    idx_dec = gen / "INDEX-DECISIONS.md"
    idx_inc = gen / "INDEX-INCIDENTS.md"
    idx_cs = gen / "INDEX-CS2023.md"

    for p in (cards_md, fc_json, idx_dec, idx_inc, idx_cs):
        assert p.exists(), f"Missing generated artifact: {p} — run uv run python tools/build_cards.py"

    cards_txt = cards_md.read_text(encoding="utf-8")
    card_heads = re.findall(r"^## Card ", cards_txt, flags=re.M)
    assert len(card_heads) == 145, f"Expected 145 ref cards, got {len(card_heads)}"

    fc = json.loads(fc_json.read_text(encoding="utf-8"))
    assert fc["self_check_count"] == 433, f"Expected 433 self-checks, got {fc['self_check_count']}"
    assert fc["qa_count"] == 60, f"Expected 60 QA cards, got {fc['qa_count']}"
    assert fc["total"] == 493 and len(fc["cards"]) == 493

    assert len(re.findall(r"^\| `D-\d+", idx_dec.read_text(encoding="utf-8"), flags=re.M)) >= 139
    assert len(re.findall(r"^\| `I-\d+", idx_inc.read_text(encoding="utf-8"), flags=re.M)) >= 68
    cs_rows = re.findall(r"^\| `\d+\.\d+(?:\.\d+)?` \|", idx_cs.read_text(encoding="utf-8"), flags=re.M)
    assert len(cs_rows) == 145, f"Expected 145 CS2023 index rows, got {len(cs_rows)}"


def test_p15_05_and_p15_06_pedagogy_files():
    p05 = ROOT / "content" / "book" / "P15-05-ranh-gioi-va-tradeoff.md"
    p06 = ROOT / "content" / "book" / "P15-06-dieu-tra-su-co.md"
    assert p05.exists() and p06.exists()

    t05 = p05.read_text(encoding="utf-8")
    assert "Khi nào SAI" in t05
    for tier in ("Startup", "Scale-up", "Enterprise"):
        assert tier in t05, f"Missing scale regime '{tier}' in P15-05"
    assert "CHƯA VIẾT" not in t05

    t06 = p06.read_text(encoding="utf-8")
    triage_cases = re.findall(r"^## Triage [1-5]\b", t06, flags=re.M)
    assert len(triage_cases) == 5, f"Expected 5 Triage walkthroughs in P15-06, got {triage_cases}"
    assert "CHƯA VIẾT" not in t06


def test_volume_5_cases_4_formats_exported():
    cases_dir = ROOT / "dist" / "SA-2028.1-LEARNER" / "cases"
    base = "SYSTEMS-ATLAS-VOLUME-5-CASES"
    for ext in ("md", "html", "docx", "pdf"):
        p = cases_dir / f"{base}.{ext}"
        assert p.exists() and p.stat().st_size > 1000, f"Missing/empty Volume 5 export: {p}"

    md_txt = (cases_dir / f"{base}.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^# Case ", md_txt, flags=re.M)) == 6

    html_txt = (cases_dir / f"{base}.html").read_text(encoding="utf-8")
    assert "noindex, nofollow, noarchive, nosnippet, noimageindex, notranslate" in html_txt

    doc = docx.Document(str(cases_dir / f"{base}.docx"))
    assert len(doc.paragraphs) >= 60

    pdf = pymupdf.open(str(cases_dir / f"{base}.pdf"))
    assert pdf.page_count >= 6
    txt = "\n".join(pdf[i].get_text("text") for i in range(min(3, pdf.page_count)))
    assert "\ufffd" not in txt
    pdf.close()


def test_astro_cards_indexes_and_triage_routes_built():
    dist = ROOT / "site" / "dist"
    for rel in ("vi/cards/index.html", "vi/indexes/index.html", "vi/triage/index.html"):
        p = dist / rel
        assert p.exists(), f"Missing Astro Task 4 route: {rel}"
        txt = p.read_text(encoding="utf-8")
        assert "noindex, nofollow, noarchive, nosnippet, noimageindex, notranslate" in txt

    cards_html = (dist / "vi" / "cards" / "index.html").read_text(encoding="utf-8")
    assert "Card 0.1" in cards_html or "145" in cards_html
    assert "fc-viewer" in cards_html

    idx_html = (dist / "vi" / "indexes" / "index.html").read_text(encoding="utf-8")
    assert "INDEX-DECISIONS" in idx_html and "INDEX-INCIDENTS" in idx_html and "INDEX-CS2023" in idx_html

    triage_html = (dist / "vi" / "triage" / "index.html").read_text(encoding="utf-8")
    assert "Triage 1" in triage_html and "Startup" in triage_html


def test_volume_v_docx_cover_and_diagram_captions(tmp_path):
    from tools import export_cases_volume

    res = export_cases_volume.export_volume_v(out_dir=str(tmp_path), want_pdf=False)
    assert res["cases"] == 6

    docx_path = tmp_path / "SYSTEMS-ATLAS-VOLUME-5-CASES.docx"
    assert docx_path.exists()
    doc = docx.Document(str(docx_path))
    full_text = "\n".join(p.text for p in doc.paragraphs)

    assert "src/" not in full_text
    assert "Tuyến học: facts/edu-order.csv" not in full_text
    assert "SYSTEMS ATLAS" in full_text
    assert "CASE STUDIES" in full_text
    assert "content/cases/vi/*.md" in full_text

    expected_captions = []
    for case_md in sorted((ROOT / "content" / "cases" / "vi").glob("*.md")):
        txt = case_md.read_text(encoding="utf-8")
        for cap in re.findall(r"<figcaption>(.*?)</figcaption>", txt, flags=re.S):
            cleaned = " ".join(cap.split())
            if cleaned:
                expected_captions.append(cleaned)

    assert len(expected_captions) >= 25
    assert "[Sơ đồ:" in full_text
    for cap in expected_captions:
        assert cap in full_text, f"Missing diagram caption in Volume V DOCX: {cap}"
