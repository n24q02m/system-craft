import os
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.audit_release import _find_broken_refs, _valid_chapters, verify_release_dir  # noqa: E402


def test_find_broken_refs_catches_real_breaks_without_false_positives():
    valid = _valid_chapters(["# 2.4 — VFS", "# 4.8 — API", "# 14.1.1 — Chips"])
    sample = "\n".join([
        "# 3.4 — Go Runtime (1.23 → 1.27)",
        "Ví dụ 1.000 → 1.900 → 432.000",
        "Học từ 2026.11 → 2026.13 và WCAG 1.0 (1999) → 2.0",
        "Xem (→4.8/2.4) và nhánh →14.1.",
        "Lỗi thật (→9.8/2.4) và nhánh → 14.99.",
    ])
    broken = _find_broken_refs(sample, valid)
    assert [b[1] for b in broken] == ["9.8", "14.99"]


def test_sa_2028_1_learner_release_complete_and_verified():
    dist_dir = os.path.join(ROOT, "dist", "SA-2028.1-LEARNER")
    res = verify_release_dir(dist_dir)
    assert res["h1s"] == 201
    assert res["labs"] == 15
    assert res["qa_files"] == 1
    assert res["tu_cham"] == 433
    assert res["nhip_noi"] == 10
    assert res["broken_refs"] == 0
    assert len(res["volumes"]) == 5
    for manifest in ("FREEZE-MANIFEST.md", "QA-RECEIPT.md"):
        assert os.path.exists(os.path.join(dist_dir, manifest))
    guide = open(os.path.join(dist_dir, "00-CACH-DUNG-GOI.md"), encoding="utf-8").read()
    assert "44 văn kiện" not in guide and "DRAFT-tham-chiếu.md" not in guide and "PHU-LUC-NGHIEM-THU-433" not in guide
    draft_md = open(os.path.join(dist_dir, "DRAFT-tham-chieu.md"), encoding="utf-8").read()
    assert "last_verified 2026-10-30" not in draft_md.splitlines()[:6]
    dpdf = pymupdf.open(os.path.join(ROOT, "dist", "DRAFT", "SYSTEMS-ATLAS-DRAFT.pdf"))
    dtoc = dpdf.get_toc()
    dpdf.close()
    assert dtoc and dtoc[0][2] >= 5, f"DRAFT PDF first bookmark on cover/TOC: {dtoc[:2]}"
