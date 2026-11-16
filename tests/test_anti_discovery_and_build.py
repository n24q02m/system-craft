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
