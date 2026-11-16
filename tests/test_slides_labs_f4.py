import csv
import json
import pathlib
import re
import subprocess
import sys

import pymupdf

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SYS101_STARS = {"0.2", "1.1", "1.2", "1.4", "1.7", "2.1", "2.3", "2.4", "3.1", "3.10", "4.1"}
SYS102_STARS = {"5.2", "5.7", "5.12", "5.14", "6.5", "8.2", "8.3", "9.1", "9.7", "10.3"}
SYS103_STARS = {"8.4", "8.5", "8.7", "11.1", "11.5", "12.2", "12.5", "13.1", "14.10.2"}
ALL_30_STARS = SYS101_STARS | SYS102_STARS | SYS103_STARS


def _check_deck(stem: str, stars: set[str], min_slides: int):
    sdir = ROOT / "kit" / "slides"
    md_p = sdir / f"{stem}.md"
    html_p = sdir / f"{stem}.html"
    pdf_p = sdir / f"{stem}.pdf"
    assert md_p.exists() and html_p.exists() and pdf_p.exists(), f"Missing slide artifact(s) for {stem}"

    md_txt = md_p.read_text(encoding="utf-8")
    slides = [s.strip() for s in re.split(r"^---\s*$", md_txt, flags=re.M) if s.strip()]
    assert len(slides) >= min_slides, f"{stem} has too few slides: {len(slides)}"
    for star in sorted(stars):
        assert re.search(rf"\b{re.escape(star)}\b", md_txt), f"Missing ★ chapter {star} in {stem}"

    html_txt = html_p.read_text(encoding="utf-8")
    assert "noindex, nofollow, noarchive, nosnippet, noimageindex, notranslate" in html_txt
    assert "http://" not in html_txt and "https://" not in html_txt

    pdf = pymupdf.open(str(pdf_p))
    try:
        assert pdf.page_count == len(slides), (
            f"{stem} PDF page count ({pdf.page_count}) != slide count ({len(slides)}) — slide overflow/split!"
        )
        sample = "\n".join(pdf[i].get_text("text") for i in range(min(5, pdf.page_count)))
        assert "\ufffd" not in sample
    finally:
        pdf.close()


def test_sys101_sys102_sys103_slide_decks_built_1_to_1():
    _check_deck("SYS101-11-chuong-xuong-song", SYS101_STARS, 70)
    _check_deck("SYS102-10-chuong-xuong-song", SYS102_STARS, 60)
    _check_deck("SYS103-09-chuong-xuong-song", SYS103_STARS, 54)


def test_devcontainer_and_verify_labs_fast():
    dc_json = ROOT / ".devcontainer" / "devcontainer.json"
    dc_df = ROOT / ".devcontainer" / "Dockerfile"
    assert dc_json.exists() and dc_df.exists()

    meta = json.loads(dc_json.read_text(encoding="utf-8"))
    assert "build" in meta or "image" in meta
    assert "postCreateCommand" in meta
    df_txt = dc_df.read_text(encoding="utf-8")
    assert "gcc" in df_txt and ("python" in df_txt.lower() or "uv" in df_txt.lower())

    verifier = ROOT / "labs" / "verify_labs.py"
    assert verifier.exists()
    r = subprocess.run(
        [sys.executable, str(verifier), "--fast"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0, f"verify_labs.py --fast failed:\n{r.stdout}\n{r.stderr}"


def test_f4_benchmarks_csv_and_provenance_check():
    bcsv = ROOT / "facts" / "benchmarks.csv"
    checker = ROOT / "tools" / "benchmark_provenance_check.py"
    assert bcsv.exists() and checker.exists()

    with open(bcsv, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f)]
    assert len(rows) >= 45, f"Expected >= 45 F4 benchmark rows, got {len(rows)}"

    seen_chaps = set()
    for r in rows:
        seen_chaps.add(r["chapter"].strip())
        assert r["primary_source"].strip() and "UNVERIFIED" not in r["primary_source"]
        assert r["verified_date"].strip()
    assert ALL_30_STARS.issubset(seen_chaps), f"Missing ★ chapters in benchmarks.csv: {ALL_30_STARS - seen_chaps}"

    r = subprocess.run(
        [sys.executable, str(checker), "--strict"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0, f"benchmark_provenance_check.py failed:\n{r.stdout}\n{r.stderr}"
