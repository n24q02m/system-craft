#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared repository paths and helper utilities for System Craft tooling."""
import csv
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
CONTENT_BOOK = os.path.join(CONTENT, "book")
CONTENT_CASES = os.path.join(CONTENT, "cases")
CONTENT_GENERATED = os.path.join(CONTENT, "generated")
CONTENT_DIAGRAMS = os.path.join(CONTENT, "diagrams")
FACTS = os.path.join(ROOT, "facts")
KIT = os.path.join(ROOT, "kit")
LABS = os.path.join(ROOT, "labs")
DIST = os.path.join(ROOT, "dist")
DOCS = os.path.join(ROOT, "docs")
SITE = os.path.join(ROOT, "site")
TRIAL = os.path.join(ROOT, "trial-00c")


def sort_key(path):
    """Numeric tuple sort key for chapter and P15 filenames."""
    nums = [int(x) for x in re.findall(r"\d+", os.path.basename(path))]
    nums = nums[:4] + [0] * (4 - len(nums[:4]))
    return tuple(nums)


def fname_to_chap(fname):
    """Map P0-00-1-x.md -> 0.1, P14-14.1.2-x.md -> 14.1.2, P1-03-x.md -> 1.3."""
    base = os.path.basename(fname)
    m = re.match(r"P0-00-(\d)-", base)
    if m:
        return "0." + m.group(1)
    m = re.match(r"P14-([0-9.]+?)(?:-|$)", base)
    if m:
        return m.group(1)
    m = re.match(r"P(\d+)-(\d+)", base)
    return f"{int(m.group(1))}.{int(m.group(2))}" if m else ""


def chapter_files(as_basenames=False):
    """Return sorted paths (or basenames) of P0-P14 chapters in content/book."""
    files = sorted(
        (
            f
            for f in glob.glob(os.path.join(CONTENT_BOOK, "P*.md"))
            if not os.path.basename(f).startswith("P15")
        ),
        key=sort_key,
    )
    return [os.path.basename(f) for f in files] if as_basenames else files


def edu_files():
    """Return sorted paths of P15 learning-layer files in content/book."""
    return sorted(glob.glob(os.path.join(CONTENT_BOOK, "P15*.md")), key=sort_key)


def read_csv_rows(path):
    """Read CSV rows while skipping '#' comment lines and empty rows."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        lines = [l for l in f if l.strip() and not l.lstrip().startswith("#")]
    return [r for r in csv.reader(lines) if r and r[0].strip()]


def read_csv_dicts(path):
    """Read CSV rows as dicts while skipping '#' comment lines."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        lines = [l for l in f if l.strip() and not l.lstrip().startswith("#")]
    return list(csv.DictReader(lines))
