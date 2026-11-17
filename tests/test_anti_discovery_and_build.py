import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import build  # noqa: E402
from kit import make_kit  # noqa: E402

NOINDEX_TOKEN = "noindex, nofollow, noarchive, nosnippet, noimageindex, notranslate"
AI_BOTS = [
    "GPTBot",
    "OAI-SearchBot",
    "ChatGPT-User",
    "ClaudeBot",
    "Claude-Web",
    "anthropic-ai",
    "Google-Extended",
    "CCBot",
    "Bytespider",
    "PerplexityBot",
    "Applebot-Extended",
    "meta-externalagent",
    "Diffbot",
]


def test_astro_config_and_robots_anti_discovery():
    cfg = (ROOT / "site" / "astro.config.mjs").read_text(encoding="utf-8")
    assert 'base: "/system-craft"' in cfg
    assert "engineering-lessons" not in cfg

    robots = ROOT / "site" / "public" / "robots.txt"
    assert robots.exists(), "Missing site/public/robots.txt"
    rtxt = robots.read_text(encoding="utf-8")
    for bot in AI_BOTS:
        assert f"User-agent: {bot}" in rtxt, f"Missing AI bot block: {bot}"
    # Must NOT block all crawlers via User-agent: * / Disallow: / or Google cannot read noindex meta
    assert "User-agent: *\nDisallow: /" not in rtxt.replace("\r\n", "\n")


def test_site_dist_html_has_noindex_no_og_no_sitemap():
    dist = ROOT / "site" / "dist"
    assert (dist / "index.html").exists(), "Run bun run --cwd site build first"
    assert (dist / "robots.txt").exists()

    html_files = sorted(dist.rglob("*.html"))
    assert len(html_files) >= 15
    for hf in html_files:
        txt = hf.read_text(encoding="utf-8")
        assert NOINDEX_TOKEN in txt, f"Missing noindex meta in {hf.relative_to(dist)}"
        assert 'property="og:' not in txt and "property='og:" not in txt, f"Found og: tag in {hf.name}"
        assert 'name="twitter:' not in txt, f"Found twitter: tag in {hf.name}"

    assert list(dist.rglob("*sitemap*.xml")) == []
    assert list(dist.glob("rss.xml")) == []
    assert list(dist.glob("feed.xml")) == []


def test_python_html_generators_include_noindex():
    sample_parts = [("P0-00-1.md", "# 0.1 Sample\n\nBody\n", 4, True)]
    stats = {"profile": "draft", "chapters": 1, "done": 1, "todo": 0, "words": 4, "dec": 0, "inc": 0}
    book_html = build.render_html_doc(sample_parts, stats)
    assert NOINDEX_TOKEN in book_html

    kit_html, _, _ = make_kit.build_html("")
    assert NOINDEX_TOKEN in kit_html

    slides_py = (ROOT / "kit" / "slides" / "build_slides.py").read_text(encoding="utf-8")
    assert NOINDEX_TOKEN in slides_py


def test_build_import_does_not_write_root_draft(tmp_path):
    root_draft = ROOT / "SYSTEMS-ATLAS-DRAFT.md"
    root_docx = ROOT / "SYSTEMS-ATLAS-DRAFT.docx"
    assert not root_draft.exists(), "Stale SYSTEMS-ATLAS-DRAFT.md present at repo root"

    try:
        build.assemble("draft", write_md=False)
        assert not root_draft.exists(), "assemble(..., write_md=False) wrote root draft"

        build.assemble("draft")
        assert not root_draft.exists(), "assemble('draft') without out_dir wrote root draft"

        build.assemble("draft", out_dir=str(tmp_path))
        assert (tmp_path / "SYSTEMS-ATLAS-DRAFT.md").exists()
        assert not root_draft.exists(), "assemble('draft', out_dir=...) leaked root draft"

        sample_parts = [("P0-00-1.md", "# 0.1 Sample\n\n#### Sub\n\n<figure><figcaption>Diagram cap</figcaption></figure>\n", 5, True)]
        stats = {"profile": "cases", "chapters": 1, "done": 1, "todo": 0, "words": 5, "dec": 0, "inc": 0}
        out_docx = tmp_path / "out.docx"
        build.build_docx(sample_parts, stats, docx_path=str(out_docx))
        assert out_docx.exists()
        assert not root_docx.exists(), "build_docx(..., docx_path=...) wrote root docx"
    finally:
        if root_draft.exists():
            root_draft.unlink()
        if root_docx.exists():
            root_docx.unlink()
