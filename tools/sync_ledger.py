#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge baseline versions.csv and live endoflife.date / GitHub Releases data."""
import csv
import datetime
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.paths import FACTS, WATCH_ALIAS, read_csv_dicts as _read_csv_rows  # noqa: E402

VERSIONS_CSV = os.path.join(FACTS, "versions.csv")
WATCHLIST_CSV = os.path.join(FACTS, "watchlist.csv")

COLS = [
    "category", "product", "cycle", "latest_version", "latest_release_date",
    "cycle_release_date", "lts", "eol_date", "status_in_ra_2026_10",
    "audit_verdict", "notes", "source", "last_verified",
]

# Full API + manual ledger aligned with restore.py + F2 + watchlist.csv cycles
SOURCES = [
    ("language", "Python", "eol", "python", "3.15"),
    ("language", "Node.js", "eol", "nodejs", "26"),
    ("language", "Go", "eol", "go", "1.27"),
    ("language", "Rust", "eol", "rust", "1.99"),
    ("language", "Java (Temurin)", "eol", "eclipse-temurin", "25"),
    ("datastore", "PostgreSQL", "eol", "postgresql", "18"),
    ("datastore", "MySQL", "eol", "mysql", "26.10"),
    ("datastore", "MongoDB", "eol", "mongodb", "9.0"),
    ("datastore", "Redis", "eol", "redis", "8.10"),
    ("datastore", "Valkey", "eol", "valkey", "9.1"),
    ("datastore", "Apache Cassandra", "eol", "apache-cassandra", "5.0"),
    ("datastore", "Elasticsearch", "eol", "elasticsearch", "9.5"),
    ("datastore", "ClickHouse", "eol", "clickhouse", "26.8"),
    ("datastore", "DuckDB", "gh", "duckdb/duckdb", "-"),
    ("datastore", "SQLite", "eol", "sqlite", "3"),
    ("datastore", "Apache Kafka", "eol", "apache-kafka", "4.4"),
    ("datastore", "RabbitMQ", "eol", "rabbitmq", "4.4"),
    ("datastore", "Apache Iceberg", "gh", "apache/iceberg", "-"),
    ("datastore", "Apache Arrow", "gh", "apache/arrow", "-"),
    ("datastore", "ScyllaDB", "gh", "scylladb/scylladb", "-"),
    ("datastore", "Milvus", "gh", "milvus-io/milvus", "-"),
    ("datastore", "Qdrant", "gh", "qdrant/qdrant", "-"),
    ("datastore", "Weaviate", "gh", "weaviate/weaviate", "-"),
    ("datastore", "NATS", "gh", "nats-io/nats-server", "-"),
    ("datastore", "Apache Pulsar", "gh", "apache/pulsar", "-"),
    ("kernel", "Linux Kernel", "eol", "linux", "7.3"),
    ("infra", "Kubernetes", "eol", "kubernetes", "1.37"),
    ("infra", "Docker Engine", "eol", "docker-engine", "29"),
    ("infra", "Envoy", "eol", "envoy", "1.40"),
    ("infra", "NGINX", "eol", "nginx", "1.29"),
    ("infra", "HAProxy", "gh", "haproxy/haproxy", "-"),
    ("infra", "Cilium", "gh", "cilium/cilium", "-"),
    ("infra", "Gateway API", "gh", "kubernetes-sigs/gateway-api", "-"),
    ("infra", "Istio", "gh", "istio/istio", "-"),
    ("infra", "Prometheus", "eol", "prometheus", "3.15"),
    ("infra", "Grafana", "gh", "grafana/grafana", "-"),
    ("observability", "OpenTelemetry", "gh", "open-telemetry/opentelemetry-collector", "-"),
    ("infra", "Terraform", "gh", "hashicorp/terraform", "-"),
    ("infra", "OpenTofu", "gh", "opentofu/opentofu", "-"),
    ("infra", "Argo CD", "gh", "argoproj/argo-cd", "-"),
    ("infra", "Flux", "gh", "fluxcd/flux2", "-"),
    ("security", "HashiCorp Vault", "gh", "hashicorp/vault", "-"),
    ("security", "Keycloak", "gh", "keycloak/keycloak", "-"),
    ("security", "OpenSSL", "eol", "openssl", "4.1"),
    ("protocol", "gRPC", "gh", "grpc/grpc", "-"),
    ("protocol", "OpenAPI", "gh", "OAI/OpenAPI-Specification", "-"),
    ("runtime", "Deno", "gh", "denoland/deno", "-"),
    ("runtime", "Bun", "gh", "oven-sh/bun", "-"),
    ("runtime", "WASI", "gh", "WebAssembly/WASI", "-"),
    ("frontend", "React / Next / Vite", "gh", "vercel/next.js", "-"),
    ("ai", "vLLM", "gh", "vllm-project/vllm", "-"),
    ("ai", "SGLang", "gh", "sgl-project/sglang", "-"),
    ("ai", "llama.cpp", "gh", "ggml-org/llama.cpp", "-"),
    ("ai", "Ollama", "gh", "ollama/ollama", "-"),
    ("ai", "NVIDIA Dynamo", "gh", "ai-dynamo/dynamo", "-"),
    ("ai", "ROCm", "gh", "ROCm/ROCm", "-"),
    ("ai", "MCP (Model Context Protocol)", "gh", "modelcontextprotocol/modelcontextprotocol", "-"),
]

STALE_COMBINED = {
    ("vllm / sglang", "2026"),
    ("cilium / gateway api", "1.20 / 1.6"),
    ("terraform / opentofu", "1.17 / 1.13"),
    ("linux kernel", "7.3 / 6.18 lts"),
}


def normalize_key(product, cycle):
    """Return case-folded (product, cycle) key for deduplicating ledger rows."""
    return (str(product or "").strip().lower(), str(cycle or "").strip().lower())


def prune_stale_rows(merged):
    """Drop legacy combined rows and GH cycles superseded by cycle='-'."""
    gh_products = {prod.lower() for _, prod, kind, _, cyc in SOURCES if kind == "gh" and cyc == "-"}
    for k in list(merged.keys()):
        prod_k, cyc_k = k
        if k in STALE_COMBINED:
            merged.pop(k, None)
        elif prod_k in gh_products and cyc_k != "-" and not (prod_k == "opentelemetry" and cyc_k == "2026") and not (prod_k == "react / next / vite" and cyc_k == "2026"):
            merged.pop(k, None)


def _get_token():
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok.strip()
    try:
        r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return ""


def _http_json(url, token):
    headers = {"User-Agent": "systems-atlas-sync/1.0", "Accept": "application/vnd.github+json"}
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def _fetch_live(kind, ref, cycle, token):
    if kind == "eol":
        data = _http_json(f"https://endoflife.date/api/{ref}.json", token)
        for item in data:
            if str(item.get("cycle")) == str(cycle):
                return {
                    "latest": str(item.get("latest") or ""),
                    "date": str(item.get("latestReleaseDate") or ""),
                    "cycle_date": str(item.get("releaseDate") or ""),
                    "lts": "true" if item.get("lts") else "false",
                    "eol": str(item.get("eol") or "active"),
                    "source": f"https://endoflife.date/api/{ref}.json",
                }
        return None
    if kind == "gh":
        try:
            d = _http_json(f"https://api.github.com/repos/{ref}/releases/latest", token)
            return {
                "latest": str(d.get("tag_name") or ""),
                "date": str((d.get("published_at") or "")[:10]),
                "source": f"https://api.github.com/repos/{ref}/releases/latest",
            }
        except Exception:
            tags = _http_json(f"https://api.github.com/repos/{ref}/tags?per_page=1", token)
            if tags:
                return {
                    "latest": str(tags[0].get("name") or ""),
                    "date": "",
                    "source": f"https://api.github.com/repos/{ref}/tags?per_page=1",
                }
            return None
    return None


def sync_all():
    today = datetime.date.today().isoformat()
    token = _get_token()
    merged = {}

    for r in _read_csv_rows(VERSIONS_CSV):
        merged[normalize_key(r["product"], r["cycle"])] = {c: r.get(c, "") for c in COLS}

    # Prune legacy combined rows & single-product GH older cycle duplicates superseded by cycle='-'
    prune_stale_rows(merged)

    for cat, prod, kind, ref, cyc in SOURCES:
        key = normalize_key(prod, cyc)
        prev = merged.get(key, {})
        try:
            live = _fetch_live(kind, ref, cyc, token)
        except Exception as exc:
            live = None
            print(f"[ERR] {prod}: {exc}")
        if not live or not live.get("latest"):
            raise RuntimeError(f"Failed live fetch for {prod} ({kind}:{ref}:{cyc})")
        row = {
            "category": prev.get("category") or cat,
            "product": prod,
            "cycle": cyc,
            "latest_version": live["latest"],
            "latest_release_date": live["date"] or prev.get("latest_release_date", ""),
            "cycle_release_date": live.get("cycle_date") or prev.get("cycle_release_date", ""),
            "lts": live.get("lts") or prev.get("lts", "false"),
            "eol_date": live.get("eol") or prev.get("eol_date", "active"),
            "status_in_ra_2026_10": prev.get("status_in_ra_2026_10") or prev.get("latest_version") or "NEW_ROW",
            "audit_verdict": "OK" if live["latest"] == prev.get("latest_version") else "SYNCED_" + today,
            "notes": prev.get("notes") or f"Synced live on {today}",
            "source": live["source"],
            "last_verified": today,
        }
        merged[key] = row
        print(f"OK {prod:30s} {cyc:8s} -> {row['latest_version']} ({row['last_verified']})")

    # Add MCP spec alias note or manual domain entries from restore.py if absent
    manuals = [
        ("ai", "CUDA", "13.x", "cuda-toolkit 13.x", "manual"),
        ("protocol", "GraphQL", "spec", "Oct 2021 + incremental delivery", "manual"),
    ]
    for cat, prod, cyc, ver, src in manuals:
        key = normalize_key(prod, cyc)
        if key not in merged:
            merged[key] = {
                "category": cat, "product": prod, "cycle": cyc, "latest_version": ver,
                "latest_release_date": "", "cycle_release_date": "", "lts": "false",
                "eol_date": "active", "status_in_ra_2026_10": "NEW_ROW",
                "audit_verdict": "MANUAL", "notes": "Specification/toolchain tracked manually per release cycle",
                "source": src, "last_verified": today,
            }

    rows_out = sorted(merged.values(), key=lambda x: (x["category"], x["product"], x["cycle"]))
    with open(VERSIONS_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)
    print(f"\nWrote {len(rows_out)} rows to {VERSIONS_CSV}")

    # Sync watchlist.csv (also matching MCP spec -> MCP (Model Context Protocol))
    if os.path.exists(WATCHLIST_CSV):
        by_pc = {normalize_key(r["product"], r["cycle"]): r for r in rows_out}
        by_p = {}
        for r in rows_out:
            by_p.setdefault(r["product"].strip().lower(), r)
        wrows = _read_csv_rows(WATCHLIST_CSV)
        wcols = ["product", "kind", "ref", "cycle", "known", "last_verified"]
        for w in wrows:
            pname = WATCH_ALIAS.get(w["product"].strip(), w["product"].strip()).lower()
            lr = by_pc.get((pname, w.get("cycle", "").strip().lower())) or by_p.get(pname)
            if lr:
                w["known"] = lr["latest_version"].strip()
                w["cycle"] = w.get("cycle") or lr["cycle"].strip()
                w["last_verified"] = today
        with open(WATCHLIST_CSV, "w", encoding="utf-8", newline="") as f:
            f.write(f"# WATCHLIST — baseline đồng bộ từ facts/versions.csv ({today})\n")
            writer = csv.DictWriter(f, fieldnames=wcols, lineterminator="\n", extrasaction="ignore")
            writer.writeheader()
            writer.writerows(wrows)
        print(f"Synced {len(wrows)} rows in {WATCHLIST_CSV}")


if __name__ == "__main__":
    sync_all()
