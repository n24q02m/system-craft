import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.paths import CONTENT_BOOK as SRC, FACTS  # noqa: E402
TOOLS = os.path.join(ROOT, "tools")


def test_all_15_labs_recovered():
    labs = sorted(glob.glob(os.path.join(SRC, "P15-03-L*.md")))
    assert len(labs) == 15
    for idx, p in enumerate(labs):
        base = os.path.basename(p)
        assert base.startswith(f"P15-03-L{idx:02d}-p{idx}"), f"Unexpected lab name {base}"
        txt = open(p, encoding="utf-8").read()
        lines = txt.splitlines()
        assert lines[0].startswith(f"# P15-03-L{idx:02d}")
        assert not lines[0].rstrip().endswith("MD")
        assert "Open" not in lines
        assert txt.count("```") % 2 == 0, f"Unbalanced code fence in {base}"


def test_p15_02_qa_recovered_cleanly():
    qa_path = os.path.join(SRC, "P15-02-QA-nang-cao.md")
    assert os.path.exists(qa_path)
    txt = open(qa_path, encoding="utf-8").read()
    lines = txt.splitlines()
    assert lines[0].startswith("# P15-02-QA ")
    assert not lines[0].rstrip().endswith("MD")
    assert "Open" not in lines
    clusters = re.findall(r"^### Cụm P\d+\b", txt, re.M)
    assert len(clusters) == 15
    assert "## Đáp án & giải thích" in txt
    q_part, a_part = txt.split("## Đáp án & giải thích", 1)
    qs = re.findall(r"^A\d+\.\d+\.", q_part, re.M)
    ans = re.findall(r"^\|\s*A\d+\.\d+\s*\|", a_part, re.M)
    assert len(qs) == 60
    assert len(ans) == 60


def test_f1_f2_f3_tools_and_facts_present():
    for rel in (
        "facts/red-thread-edu-bridges.csv",
        "facts/product-candidates.txt",
        "facts/watchlist.csv",
        "tools/red_thread_edu_check.py",
        "tools/ledger_coverage_check.py",
        "tools/freshness_check.py",
    ):
        assert os.path.exists(os.path.join(ROOT, *rel.split("/"))), f"Missing {rel}"
    wtxt = open(os.path.join(FACTS, "watchlist.csv"), encoding="utf-8").read()
    assert "product,kind,ref,cycle,known,last_verified" in wtxt
