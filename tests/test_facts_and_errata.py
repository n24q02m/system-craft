import csv
import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import paths  # noqa: E402

PUBLIC_SANITIZED = {
    "P14-14.8.1-ietf-process.md",
    "P0-00-1-he-quy-chieu.md",
    "P0-00-2-tien-de.md",
    "P0-00-3-lens-dong-tu.md",
}


def test_erratum_e1_fixed_and_other_chapters_unchanged():
    all_ch = paths.chapter_files()
    assert len(all_ch) == 145
    expected = json.loads(
        open(os.path.join(ROOT, "tests", "fixtures", "baseline_chapters_sha256.json"), encoding="utf-8").read()
    )
    for p in all_ch:
        name = os.path.basename(p)
        txt = open(p, encoding="utf-8").read()
        assert "→9.8" not in txt, f"Broken cross-ref still present in {name}"
        assert "1.1RFC" not in txt, f"Missing space typo still present in {name}"
        if name == "P14-14.8.1-ietf-process.md":
            assert "(→4.8/2.4)" in txt
            assert "TLS 1.0/1.1 RFC" in txt
        elif name in PUBLIC_SANITIZED:
            assert "SA-2028.1" in txt or "facts/coverage" in txt
        else:
            actual = hashlib.sha256(open(p, "rb").read()).hexdigest()
            assert actual == expected[name], f"Unauthorized modification in {name}"


def test_p15_00_has_cs2023_table_and_no_stale_notes():
    p15_00 = open(os.path.join(paths.CONTENT_BOOK, "P15-00-tang-hoc-cach-dung.md"), encoding="utf-8").read()
    assert "SA-2028.1" in p15_00
    assert "CS2023" in p15_00
    assert "270 giờ" in p15_00
    assert " worth " not in p15_00


def test_versions_csv_closed_no_unverified_and_coverage_passes():
    vpath = os.path.join(ROOT, "facts", "versions.csv")
    with open(vpath, encoding="utf-8-sig", newline="") as f:
        lines = [l for l in f if not l.lstrip().startswith("#")]
    rows = list(csv.DictReader(lines))
    assert len(rows) >= 70
    unverified = [r["product"] for r in rows if r.get("audit_verdict") == "UNVERIFIED"]
    assert unverified == [], f"Found UNVERIFIED rows: {unverified}"
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "ledger_coverage_check.py"), "--strict"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert r.returncode == 0, f"ledger_coverage_check --strict failed:\n{r.stdout}\n{r.stderr}"
