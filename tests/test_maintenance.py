import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_maintenance_classifies_all_watchlist_tiers_and_cadence_offline(tmp_path):
    from tools.freshness_check import WATCH, read_csv
    from tools.maintenance_check import TIER_CADENCE_DAYS, classify_product, evaluate_maintenance

    watch_rows = read_csv(WATCH)
    assert len(watch_rows) >= 38
    tiers_seen = set()
    for w in watch_rows:
        tier = classify_product(w["product"])
        assert tier in TIER_CADENCE_DAYS, f"Invalid tier {tier} for {w['product']}"
        tiers_seen.add(tier)
    # Every active software tier (fire2, fire1, warm) is represented in watchlist
    assert {"🔥🔥", "🔥", "🌡"}.issubset(tiers_seen)

    # Synthetic offline fixture: AI tool stale at 8 days, edge infra DRIFT, datastore OK at 45 days, standard overdue at 200 days
    ref_today = datetime.date(2026, 11, 16)
    fixture = {
        "rows": [
            {"product": "vLLM", "known": "v0.33.0rc3", "latest": "v0.33.0rc3", "status": "OK", "last_verified": "2026-11-08"},
            {"product": "OpenSSL", "known": "4.1.0", "latest": "4.1.1", "status": "DRIFT", "last_verified": "2026-11-15"},
            {"product": "PostgreSQL", "known": "18.7", "latest": "18.7", "status": "OK", "last_verified": "2026-10-01"},
            {"product": "FIPS 203/204/205", "known": "2024-08", "latest": "2024-08", "status": "OK", "last_verified": "2026-04-01"},
        ]
    }
    fx_path = tmp_path / "fresh.json"
    fx_path.write_text(json.dumps(fixture), encoding="utf-8")

    report = evaluate_maintenance(json.loads(fx_path.read_text(encoding="utf-8"))["rows"], today=ref_today)
    assert len(report["drift"]) == 1 and report["drift"][0]["product"] == "OpenSSL"
    stale_names = {r["product"] for r in report["stale"]}
    assert "vLLM" in stale_names  # 🔥🔥 max_age 7d exceeded (8d)
    assert "FIPS 203/204/205" in stale_names  # 🧊 max_age 180d exceeded (229d)
    assert "PostgreSQL" not in stale_names  # 🌡 46d <= 90d quarterly cadence
    assert classify_product("MCP (Model Context Protocol)") == "🔥🔥"
    assert classify_product("ROCm") == "🔥🔥"

    no_base_report = evaluate_maintenance(
        [{"product": "MCP spec", "status": "NO_BASELINE", "last_verified": "2026-11-16"}],
        today=ref_today,
    )
    assert len(no_base_report["missing_baseline"]) == 1
    assert len(no_base_report["ok"]) == 0


def test_maintenance_runbook_documents_f3_tiers_and_workflow():
    doc_path = os.path.join(ROOT, "docs", "MAINTENANCE-RUNBOOK.md")
    assert os.path.exists(doc_path)
    txt = open(doc_path, encoding="utf-8").read()
    for needle in ("🔥🔥", "🔥", "🌡", "🧊", "sync_ledger.py", "freshness_check.py", "maintenance_check.py", "ERRATA.md"):
        assert needle in txt, f"Missing '{needle}' in MAINTENANCE-RUNBOOK.md"


def test_maintenance_cli_strict_exits_nonzero_on_no_baseline(tmp_path):
    fx = tmp_path / "fx.json"
    fx.write_text(json.dumps({"rows": [{"product": "MCP spec", "status": "NO_BASELINE", "last_verified": "2026-11-16"}]}), encoding="utf-8")
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "maintenance_check.py"), "--input-json", str(fx), "--strict"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert r.returncode == 1
    assert "NO_BASELINE=1" in r.stdout
