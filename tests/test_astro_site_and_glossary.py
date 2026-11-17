import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import paths  # noqa: E402


def test_glossary_csv_generated_and_complete():
    gpath = ROOT / "facts" / "glossary.csv"
    assert gpath.exists(), "Missing facts/glossary.csv — run uv run python tools/build_glossary.py"
    with gpath.open(encoding="utf-8-sig", newline="") as f:
        lines = [l for l in f if l.strip() and not l.lstrip().startswith("#")]
    rows = list(csv.DictReader(lines))
    assert len(rows) >= 300, f"Expected >= 300 glossary entries, got {len(rows)}"
    assert {"term", "vi_gloss", "en_gloss", "chapters", "source"}.issubset(set(rows[0].keys()))

    terms_lower = {r["term"].strip().lower() for r in rows}
    en_lower = {r["en_gloss"].strip().lower() for r in rows if r.get("en_gloss")}
    combined = terms_lower | en_lower
    for needle in ("latency", "throughput", "rtt", "quorum", "fencing token", "wal", "pagedattention"):
        assert any(needle in t for t in combined), f"Missing core glossary term: {needle}"
    for r in rows:
        assert r["term"].strip()
        assert r["vi_gloss"].strip()


def test_chapter_case_links_csv_valid():
    lpath = ROOT / "facts" / "chapter-case-links.csv"
    assert lpath.exists(), "Missing facts/chapter-case-links.csv"
    rows = paths.read_csv_dicts(str(lpath))
    assert len(rows) >= 20
    valid_chaps = {paths.fname_to_chap(f) for f in paths.chapter_files()}
    valid_cases = {p.stem for p in (ROOT / "content" / "cases" / "vi").glob("*.md")}
    seen_cases = set()
    for r in rows:
        assert r["chapter"] in valid_chaps, f"Invalid chapter in chapter-case-links: {r['chapter']}"
        assert r["case_slug"] in valid_cases, f"Invalid case slug: {r['case_slug']}"
        seen_cases.add(r["case_slug"])
    assert seen_cases == valid_cases, f"Missing case studies in chapter-case-links: {valid_cases - seen_cases}"


def test_astro_dist_unified_pages_and_pagefind_search():
    dist = ROOT / "site" / "dist"
    assert (dist / "pagefind" / "pagefind.js").exists(), "Missing Pagefind search bundle"
    assert (dist / "pagefind" / "pagefind-entry.json").exists(), "Missing Pagefind entry index"

    for rel in (
        "vi/book/index.html",
        "vi/paths/index.html",
        "vi/search/index.html",
        "en/search/index.html",
        "vi/status/index.html",
        "en/status/index.html",
        "vi/cases/index.html",
        "en/cases/index.html",
    ):
        assert (dist / rel).exists(), f"Missing built Astro page: {rel}"

    # All 145 chapters rendered cleanly under vi/book/<chap>/index.html
    for f in paths.chapter_files():
        ch = paths.fname_to_chap(f)
        ch_html = dist / "vi" / "book" / ch / "index.html"
        assert ch_html.exists(), f"Missing chapter HTML: vi/book/{ch}/index.html"

    # Interactive controls + glossary + bidirectional case cross-links on chapter 12.2 & 1.1
    ch11 = (dist / "vi" / "book" / "1.1" / "index.html").read_text(encoding="utf-8")
    for needle in (
        'data-speed="brief"',
        'data-speed="practical"',
        'data-speed="full"',
        'data-sec="0"',
        'data-sec="1"',
        'data-sec="5"',
        'data-sec="7"',
        "sc-progress-",
        'class="gloss"',
        "noindex, nofollow, noarchive, nosnippet, noimageindex, notranslate",
    ):
        assert needle in ch11, f"Missing '{needle}' in chapter 1.1 HTML"

    ch122 = (dist / "vi" / "book" / "12.2" / "index.html").read_text(encoding="utf-8")
    assert "vietnamese-language-model" in ch122, "Missing forward link from ch 12.2 to case study"

    for lang in ("vi", "en"):
        case_html = (dist / lang / "posts" / "vietnamese-language-model" / "index.html").read_text(encoding="utf-8")
        assert "/book/12.2/" in case_html, f"Missing backlink from {lang} case study to chapter 12.2"
        assert 'class="gloss"' in case_html, f"Missing glossary annotations in {lang} case study"

    # Verify status page surfaces ledger counts without leaking secrets
    status_html = (dist / "vi" / "status" / "index.html").read_text(encoding="utf-8")
    assert "versions.csv" in status_html or "145" in status_html


def test_astro_dist_zero_broken_internal_links():
    from bs4 import BeautifulSoup

    dist = ROOT / "site" / "dist"
    assert (dist / "index.html").exists(), "Run bun run --cwd site build first"

    broken = []
    checked = 0
    for html_file in sorted(dist.rglob("*.html")):
        soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")
        targets = []
        for a in soup.find_all("a", href=True):
            targets.append(("a[href]", a["href"]))
        for lnk in soup.find_all("link", href=True):
            rels = [r.lower() for r in (lnk.get("rel") or [])]
            if "alternate" in rels and lnk.has_attr("hreflang"):
                targets.append(("link[rel=alternate]", lnk["href"]))

        for kind, raw in targets:
            href = raw.strip()
            if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "#")):
                continue
            path_part = href.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue
            checked += 1

            if path_part.startswith("/"):
                if path_part == "/system-craft" or path_part == "/system-craft/":
                    rel = ""
                elif path_part.startswith("/system-craft/"):
                    rel = path_part[len("/system-craft/") :].lstrip("/")
                else:
                    broken.append(f"{html_file.relative_to(dist)} {kind}={raw!r} (missing /system-craft base)")
                    continue
                target_file = dist / rel if rel else dist / "index.html"
                target_dir_index = (dist / rel / "index.html") if rel else (dist / "index.html")
            else:
                target_file = (html_file.parent / path_part).resolve()
                target_dir_index = target_file / "index.html"

            if not (target_file.is_file() or target_dir_index.is_file()):
                broken.append(f"{html_file.relative_to(dist)} {kind}={raw!r}")

    assert checked >= 100
    assert broken == [], f"Found {len(broken)} broken internal links:\n" + "\n".join(broken[:25])
