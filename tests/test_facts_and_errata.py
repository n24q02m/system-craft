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


def test_versions_no_duplicate_cycles_case_insensitive():
    from tools import sync_ledger

    vpath = os.path.join(ROOT, "facts", "versions.csv")
    rows = paths.read_csv_dicts(vpath)
    seen = set()
    dups = []
    for r in rows:
        key = (r["product"].strip().lower(), r["cycle"].strip().lower())
        if key in seen:
            dups.append(key)
        seen.add(key)

    assert dups == [], f"Duplicate case-insensitive (product, cycle) in versions.csv: {dups}"
    assert ("linux kernel", "7.3 / 6.18 lts") not in seen, "Stale duplicate Linux Kernel cycle still in versions.csv"

    merged = {
        sync_ledger.normalize_key("Linux Kernel", "7.3"): {"product": "Linux Kernel", "cycle": "7.3"},
        sync_ledger.normalize_key("Linux Kernel", "7.3 / 6.18 LTS"): {"product": "Linux Kernel", "cycle": "7.3 / 6.18 LTS"},
    }
    sync_ledger.prune_stale_rows(merged)
    assert ("linux kernel", "7.3") in merged
    assert ("linux kernel", "7.3 / 6.18 lts") not in merged


def test_freshness_skip_computes_age_days(tmp_path, monkeypatch):
    from tools import freshness_check

    assert freshness_check.WATCH_ALIAS.get("MCP spec") == "MCP (Model Context Protocol)"

    watch_csv = tmp_path / "watchlist.csv"
    watch_csv.write_text(
        "product,kind,ref,cycle,known,last_verified\n"
        "Python,eol,python,3.15,3.15.2,2026-10-01\n"
        "MCP spec,gh,modelcontextprotocol/modelcontextprotocol,-,2026-07-28,2026-10-01\n",
        encoding="utf-8",
    )
    versions_csv = tmp_path / "versions.csv"
    versions_csv.write_text(
        "category,product,cycle,latest_version\n"
        "language,Python,3.15,3.15.2\n"
        'ai,MCP (Model Context Protocol),-,2026-07-28\n',
        encoding="utf-8",
    )
    out_json = tmp_path / "fresh.json"

    monkeypatch.setattr(freshness_check, "WATCH", str(watch_csv))
    monkeypatch.setattr(freshness_check, "VERSIONS", str(versions_csv))
    monkeypatch.setattr(freshness_check, "check_eol", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("offline")))
    monkeypatch.setattr(freshness_check, "check_gh", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("offline")))

    monkeypatch.setattr(sys, "argv", ["freshness_check.py", "--json", str(out_json), "--max-age", "7"])
    rc = freshness_check.main()
    assert rc == 0

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert len(data["rows"]) == 2
    for row in data["rows"]:
        assert row["status"] == "SKIP"
        assert isinstance(row.get("age_days"), int) and row["age_days"] > 7
    assert len(data["stale"]) == 2

    # Also verify --sync resolves WATCH_ALIAS and uses csv.DictWriter cleanly
    monkeypatch.setattr(sys, "argv", ["freshness_check.py", "--sync"])
    assert freshness_check.main() == 0
    synced = paths.read_csv_dicts(str(watch_csv))
    mcp_row = next(r for r in synced if r["product"] == "MCP spec")
    assert mcp_row["known"] == "2026-07-28"
