#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build and assemble dist/SA-2028.1-LEARNER and dist/DRAFT end-to-end."""
import argparse
import datetime
import hashlib
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.audit_release import verify_release_dir  # noqa: E402
from tools.paths import DIST, DOCS, FACTS  # noqa: E402


def _run(cmd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run(cmd, cwd=ROOT, env=env)
    if r.returncode != 0:
        sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-only", action="store_true", help="Skip build.py steps and refresh audit/manifest on existing dist/")
    args = ap.parse_args()

    learner_dir = os.path.join(DIST, "SA-2028.1-LEARNER")
    draft_dir = os.path.join(DIST, "DRAFT")
    os.makedirs(learner_dir, exist_ok=True)
    os.makedirs(draft_dir, exist_ok=True)

    today = datetime.date.today().isoformat()
    if not args.verify_only:
        # 1. Build EDU + 5 split PDFs (runs preflight F1/F2/F3 gates)
        _run([sys.executable, "build.py", "--profile", "edu", "--out-dir", learner_dir, "--split-parts"])
        for ext in ("md", "html", "docx", "pdf"):
            src = os.path.join(learner_dir, f"SYSTEMS-ATLAS-EDU.{ext}")
            dst = os.path.join(learner_dir, f"SYSTEMS-ATLAS-LEARNER-SA-2028.1.{ext}")
            if os.path.exists(dst):
                os.remove(dst)
            os.replace(src, dst)

        # 2. Build DRAFT 4 formats & copy reference DRAFT-tham-chieu.md
        _run([sys.executable, "build.py", "--profile", "draft", "--out-dir", draft_dir, "--skip-preflight"])
        shutil.copy2(
            os.path.join(draft_dir, "SYSTEMS-ATLAS-DRAFT.md"),
            os.path.join(learner_dir, "DRAFT-tham-chieu.md"),
        )

        # 3. Bundle facts/ into SA-2028.1-LEARNER/facts/
        dst_facts = os.path.join(learner_dir, "facts")
        if os.path.exists(dst_facts):
            shutil.rmtree(dst_facts)
        shutil.copytree(FACTS, dst_facts)

        # 4. Update 00-CACH-DUNG-GOI.md
        guide_src = os.path.join(DOCS, "00-CACH-DUNG-GOI.md")
        guide = open(guide_src, encoding="utf-8").read()
        guide = guide.replace("2026-11-16", today)
        open(os.path.join(learner_dir, "00-CACH-DUNG-GOI.md"), "w", encoding="utf-8", newline="\n").write(guide)

        # 4b. Export Volume V Case Studies 4 formats + refresh cards/indexes
        _run([sys.executable, "tools/build_cards.py"])
        _run([sys.executable, "tools/export_cases_volume.py", "--out-dir", os.path.join(learner_dir, "cases")])

    # 5. Audit & write QA-RECEIPT.md + FREEZE-MANIFEST.md
    _run([
        sys.executable,
        "tools/audit_release.py",
        "--dist", learner_dir,
        "--write-receipt", os.path.join(learner_dir, "QA-RECEIPT.md"),
    ])
    res = verify_release_dir(learner_dir)
    manifest_lines = [
        "# FREEZE MANIFEST — SYSTEMS ATLAS SA-2028.1 LEARNER\n",
        f"- **Ngày đóng gói:** {today}",
        f"- **Quy mô:** {res['md_words']:,} từ · {res['h1s']} H1 (145 chương + 1 bìa + 4 dẫn/trade-off/triage + 5 trang nhãn phần học + 15 quiz + 1 quiz nâng cao 60 câu + 15 lab + 15 lời giải)",
        f"- **Bài tập & Tự chấm:** {res['tu_cham']} mục Tự chấm (M1+M3) · {res['nhip_noi']} nhịp nối tuyến học · {res['broken_refs']} tham chiếu gãy",
        f"- **PDF:** {res['pdf_pages']:,} trang · {res['pdf_bookmarks']:,} bookmarks · + 5 tập PDF phân phần trong `volumes/`",
        "\n## Tệp phát hành & SHA-256\n",
    ]
    for fn in (
        "SYSTEMS-ATLAS-LEARNER-SA-2028.1.md",
        "SYSTEMS-ATLAS-LEARNER-SA-2028.1.html",
        "SYSTEMS-ATLAS-LEARNER-SA-2028.1.docx",
        "SYSTEMS-ATLAS-LEARNER-SA-2028.1.pdf",
        "DRAFT-tham-chieu.md",
    ):
        p = os.path.join(learner_dir, fn)
        sz = os.path.getsize(p)
        manifest_lines.append(f"- `{fn}` ({sz:,} B): `{res['hashes'][fn]}`")
    manifest_lines.append("\n## 5 Tập PDF Phân Phần (`volumes/`)\n")
    for vn, pg, bk in res["volumes"]:
        vp = os.path.join(learner_dir, "volumes", vn)
        vh = hashlib.sha256(open(vp, "rb").read()).hexdigest()
        manifest_lines.append(f"- `volumes/{vn}` ({os.path.getsize(vp):,} B, {pg} tr., {bk} bk): `{vh}`")
    open(os.path.join(learner_dir, "FREEZE-MANIFEST.md"), "w", encoding="utf-8", newline="\n").write(
        "\n".join(manifest_lines) + "\n"
    )
    print("Packaged dist/SA-2028.1-LEARNER and dist/DRAFT cleanly!")


if __name__ == "__main__":
    main()
