import os
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import paths  # noqa: E402

SYS101_STARS = {"0.2", "1.1", "1.2", "1.4", "1.7", "2.1", "2.3", "2.4", "3.1", "3.10", "4.1"}
SYS102_STARS = {"5.2", "5.7", "5.12", "5.14", "6.5", "8.2", "8.3", "9.1", "9.7", "10.3"}
SYS103_STARS = {"8.4", "8.5", "8.7", "11.1", "11.5", "12.2", "12.5", "13.1", "14.10.2"}
ALL_30_STARS = SYS101_STARS | SYS102_STARS | SYS103_STARS


def test_diagrams_csv_and_30_star_svgs_valid():
    dcsv = ROOT / "facts" / "diagrams.csv"
    assert dcsv.exists(), "Missing facts/diagrams.csv — run uv run python tools/generate_diagrams.py"
    rows = paths.read_csv_dicts(str(dcsv))
    assert len(rows) >= 30

    chapters_seen = set()
    marker_ids = set()
    for r in rows:
        chap = r["chapter"].strip()
        svg_path = ROOT / "content" / "diagrams" / r["svg_file"].strip()
        assert svg_path.exists(), f"Missing diagram SVG file: {svg_path}"
        txt = svg_path.read_text(encoding="utf-8")
        scrubbed = txt.replace('xmlns="http://www.w3.org/2000/svg"', "")
        assert "http://" not in scrubbed and "https://" not in scrubbed
        assert "<script" not in txt.lower()

        root_el = ET.fromstring(txt)
        assert root_el.tag.endswith("svg")
        assert root_el.attrib.get("viewBox")
        assert root_el.attrib.get("aria-label")
        for el in root_el.iter():
            if el.tag.endswith("marker") and "id" in el.attrib:
                mid = el.attrib["id"]
                assert mid not in marker_ids, f"Duplicate SVG marker ID across diagrams: {mid}"
                marker_ids.add(mid)
        chapters_seen.add(chap)

    assert ALL_30_STARS.issubset(chapters_seen), f"Missing ★ chapters in diagrams.csv: {ALL_30_STARS - chapters_seen}"


def test_build_py_injects_diagrams_into_html_and_shares_diagram_css():
    import build

    assert hasattr(build, "load_diagrams"), "build.py missing load_diagrams()"
    assert hasattr(build, "inject_chapter_diagrams_html"), "build.py missing inject_chapter_diagrams_html()"
    diags = build.load_diagrams()
    assert len(diags) >= 30

    ch11_path = next(f for f in paths.chapter_files() if os.path.basename(f).startswith("P1-01-"))
    ch11_txt = open(ch11_path, encoding="utf-8").read()
    html_out = build.render_html_doc([(ch11_path, ch11_txt, len(ch11_txt.split()), True)], {
        "profile": "edu", "chapters": 1, "done": 1, "todo": 0, "words": 1000, "edu": 0, "dec": 0, "inc": 0,
    })
    assert '<figure class="diagram"' in html_out
    assert "<svg " in html_out
    assert ".diagram svg" in html_out


def test_astro_dist_renders_svgs_and_5_calculators():
    dist = ROOT / "site" / "dist"
    for star in ("1.1", "8.2", "12.2", "14.10.2"):
        html_p = dist / "vi" / "book" / star / "index.html"
        assert html_p.exists()
        htxt = html_p.read_text(encoding="utf-8")
        assert '<figure class="diagram"' in htxt, f"Missing injected SVG diagram in Astro chapter {star}"
        assert f"ch-{star}.svg" in htxt

    for lang in ("vi", "en"):
        tpage = dist / lang / "tools" / "index.html"
        assert tpage.exists(), f"Missing calculator tools page: {lang}/tools/index.html"
        txt = tpage.read_text(encoding="utf-8")
        assert "noindex, nofollow, noarchive, nosnippet, noimageindex, notranslate" in txt
        for cid in ("calc-latency", "calc-raid", "calc-bdp", "calc-little", "calc-llm"):
            assert cid in txt, f"Missing calculator '{cid}' in {lang}/tools/index.html"
