import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import paths  # noqa: E402


SKIP_SHA = {
    "P14-14.8.1-ietf-process.md",
    "P0-00-1-he-quy-chieu.md",
    "P0-00-2-tien-de.md",
    "P0-00-3-lens-dong-tu.md",
}


def test_source_inventory_matches_frozen_baseline():
    all_p = [
        os.path.join(paths.CONTENT_BOOK, fn)
        for fn in os.listdir(paths.CONTENT_BOOK)
        if fn.startswith("P") and fn.endswith(".md")
    ]
    assert len(all_p) >= 193
    chapters = paths.chapter_files()
    assert len(chapters) == 145
    fixture_path = os.path.join(ROOT, "tests", "fixtures", "baseline_chapters_sha256.json")
    expected = json.loads(open(fixture_path, encoding="utf-8").read())
    assert len(expected) == 145
    for p in chapters:
        name = os.path.basename(p)
        if name in SKIP_SHA:
            continue  # Erratum E-1 and public sanitization of legacy plan refs verified in test_facts_and_errata.py
        actual = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert actual == expected[name], f"Unexpected chapter drift in {name}"
