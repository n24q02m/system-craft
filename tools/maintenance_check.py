#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F3 Decay-Cadence Maintenance Harness for SYSTEMS ATLAS (SA-2028.1)."""
import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.freshness_check import WATCH, read_csv  # noqa: E402

TIER_CADENCE_DAYS = {
    "🔥🔥": 7,    # AI serving & agent tools — checked every build
    "🔥": 14,     # Edge infra (TLS, container, mesh, K8s, IaC) — every build / biweekly
    "🌡": 90,     # Core datastores, Linux kernel, language runtimes — per quarterly edition
    "🧊": 180,    # Formal standards & laws (FIPS, RFC, GDPR/CRA/NIS2/DORA) — 6-12 months
}

PRODUCT_TIERS = {
    "vllm": "🔥🔥",
    "sglang": "🔥🔥",
    "llama.cpp": "🔥🔥",
    "ollama": "🔥🔥",
    "nvidia dynamo": "🔥🔥",
    "rocm": "🔥🔥",
    "mcp spec": "🔥🔥",
    "mcp (model context protocol)": "🔥🔥",
    "kubernetes": "🔥",
    "docker engine": "🔥",
    "openssl": "🔥",
    "envoy": "🔥",
    "cilium": "🔥",
    "terraform": "🔥",
    "opentofu": "🔥",
    "grpc": "🔥",
    "istio": "🔥",
    "argo cd": "🔥",
    "flux": "🔥",
    "python": "🌡",
    "node.js": "🌡",
    "go": "🌡",
    "rust": "🌡",
    "java (temurin)": "🌡",
    "linux kernel": "🌡",
    "postgresql": "🌡",
    "mysql": "🌡",
    "mongodb": "🌡",
    "redis": "🌡",
    "valkey": "🌡",
    "apache kafka": "🌡",
    "rabbitmq": "🌡",
    "apache cassandra": "🌡",
    "elasticsearch": "🌡",
    "clickhouse": "🌡",
    "sqlite": "🌡",
    "prometheus": "🌡",
    "duckdb": "🌡",
    "apache iceberg": "🌡",
    "apache arrow": "🌡",
}

STANDARD_KEYWORDS = ("fips", "gdpr", "pdpd", "cra", "nis2", "dora", "owasp", "wcag", "rfc", "iso", "eu ai")


def classify_product(name):
    """Map a ledger/watchlist item to its F3 decay tier."""
    key = (name or "").strip().lower()
    if key in PRODUCT_TIERS:
        return PRODUCT_TIERS[key]
    if any(tok in key for tok in STANDARD_KEYWORDS):
        return "🧊"
    return "🔥"


def evaluate_maintenance(rows, today=None, watch_dates=None):
    """Evaluate freshness records against tier-specific decay windows."""
    ref_today = today or datetime.date.today()
    watch_dates = watch_dates or {}
    drift, stale, missing_baseline, skip, ok = [], [], [], [], []

    for row in rows:
        product = row.get("product", "")
        tier = classify_product(product)
        max_days = TIER_CADENCE_DAYS[tier]
        last_ver = row.get("last_verified") or watch_dates.get(product, "")
        age_days = row.get("age_days")
        if age_days is None and last_ver:
            try:
                age_days = (ref_today - datetime.date.fromisoformat(last_ver[:10])).days
            except ValueError:
                age_days = None

        entry = {
            "product": product,
            "tier": tier,
            "max_age_days": max_days,
            "age_days": age_days,
            "status": row.get("status", "UNKNOWN"),
            "known": row.get("known", ""),
            "latest": row.get("latest", ""),
            "last_verified": last_ver,
        }
        if entry["status"] == "DRIFT":
            drift.append(entry)
        elif entry["status"] == "NO_BASELINE":
            missing_baseline.append(entry)
        elif entry["status"] in ("SKIP", "UNKNOWN", "BAD_KIND"):
            skip.append(entry)
        else:
            ok.append(entry)

        if age_days is not None and age_days > max_days:
            stale.append(entry)

    return {
        "checked_on": ref_today.isoformat(),
        "total": len(rows),
        "drift": drift,
        "stale": stale,
        "missing_baseline": missing_baseline,
        "skip": skip,
        "ok": ok,
    }


def main():
    ap = argparse.ArgumentParser(description="F3 tier-cadence maintenance check for SYSTEMS ATLAS")
    ap.add_argument("--input-json", help="Optional JSON produced by tools/freshness_check.py --json")
    ap.add_argument("--json-out", help="Optional output path for structured maintenance report")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if any DRIFT or cadence SLA breach exists")
    args = ap.parse_args()

    watch_dates = {w["product"]: w.get("last_verified", "") for w in read_csv(WATCH)}
    if args.input_json:
        data = json.load(open(args.input_json, encoding="utf-8"))
        rows = data.get("rows", [])
    else:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            tmp_json = tf.name
        try:
            proc = subprocess.run(
                [sys.executable, os.path.join(ROOT, "tools", "freshness_check.py"), "--json", tmp_json],
                cwd=ROOT,
                check=False,
            )
            if proc.returncode not in (0, 1) or not os.path.exists(tmp_json) or os.path.getsize(tmp_json) == 0:
                raise RuntimeError(f"freshness_check.py failed unexpectedly (rc={proc.returncode})")
            data = json.load(open(tmp_json, encoding="utf-8"))
            rows = data.get("rows", [])
        finally:
            if os.path.exists(tmp_json):
                os.remove(tmp_json)

    report = evaluate_maintenance(rows, watch_dates=watch_dates)
    print(
        f"MAINTENANCE ({report['checked_on']}): {report['total']} items · "
        f"DRIFT={len(report['drift'])} · STALE={len(report['stale'])} · "
        f"NO_BASELINE={len(report['missing_baseline'])} · SKIP={len(report['skip'])}"
    )
    for item in report["drift"]:
        print(f"  [DRIFT {item['tier']}] {item['product']}: {item['known']} -> {item['latest']}")
    for item in report["stale"]:
        print(f"  [STALE {item['tier']}] {item['product']}: age={item['age_days']}d > {item['max_age_days']}d")
    for item in report["missing_baseline"]:
        print(f"  [NO_BASELINE {item['tier']}] {item['product']}")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    if args.strict and (report["drift"] or report["stale"] or report["missing_baseline"]):
        return 1
    return 1 if (report["drift"] or report["missing_baseline"]) else 0


if __name__ == "__main__":
    sys.exit(main())
