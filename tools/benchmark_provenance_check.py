#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F4 Validator: verify primary-source provenance in facts/benchmarks.csv across all 30 ★ chapters."""
import argparse
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import paths  # noqa: E402

REQUIRED_COLS = [
    "id",
    "chapter",
    "metric",
    "value",
    "unit",
    "source_kind",
    "primary_source",
    "verified_date",
    "notes",
]
ALLOWED_KINDS = {"physics", "math_law", "ietf_rfc", "nist_fips", "vendor_spec", "kernel_doc", "paper", "sre_ref"}
ALL_30_STARS = {
    "0.2", "1.1", "1.2", "1.4", "1.7", "2.1", "2.3", "2.4", "3.1", "3.10", "4.1",
    "5.2", "5.7", "5.12", "5.14", "6.5", "8.2", "8.3", "9.1", "9.7", "10.3",
    "8.4", "8.5", "8.7", "11.1", "11.5", "12.2", "12.5", "13.1", "14.10.2",
}


def validate(strict=False):
    bcsv = os.path.join(paths.FACTS, "benchmarks.csv")
    if not os.path.exists(bcsv):
        raise FileNotFoundError(f"Missing {bcsv}")

    with open(bcsv, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != REQUIRED_COLS:
            raise ValueError(f"Unexpected benchmarks.csv headers: {reader.fieldnames} != {REQUIRED_COLS}")
        rows = [r for r in reader if any((v or "").strip() for v in r.values())]

    valid_chaps = {paths.fname_to_chap(fp) for fp in paths.chapter_files()}
    ids = set()
    chaps = set()
    errs = []

    for i, r in enumerate(rows, 2):
        rid = (r["id"] or "").strip()
        ch = (r["chapter"] or "").strip()
        src = (r["primary_source"] or "").strip()
        kind = (r["source_kind"] or "").strip()
        dt = (r["verified_date"] or "").strip()

        if not rid or rid in ids:
            errs.append(f"Row {i}: duplicate/empty id '{rid}'")
        ids.add(rid)
        if ch not in valid_chaps:
            errs.append(f"Row {i}: unknown chapter '{ch}'")
        chaps.add(ch)
        if kind not in ALLOWED_KINDS:
            errs.append(f"Row {i}: invalid source_kind '{kind}'")
        if not src or any(bad in src.upper() for bad in ("UNVERIFIED", "TODO", "TBD")):
            errs.append(f"Row {i}: invalid primary_source '{src}'")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dt):
            errs.append(f"Row {i}: invalid verified_date '{dt}'")

    if len(rows) < 45:
        errs.append(f"Too few benchmark rows: {len(rows)} < 45")
    missing_stars = sorted(ALL_30_STARS - chaps)
    if missing_stars:
        errs.append(f"Missing ★ chapters in benchmarks.csv: {missing_stars}")

    if strict and errs:
        raise AssertionError("\n".join(errs))
    return len(rows), len(chaps), errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    n_rows, n_chaps, errs = validate(strict=args.strict)
    if errs:
        for e in errs:
            print("FAIL:", e)
        return 1
    print(f"F4 BENCHMARKS: PASS — {n_rows} constants across {n_chaps} chapters (all 30★ covered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
