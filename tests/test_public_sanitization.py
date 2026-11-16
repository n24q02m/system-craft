import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

FORBIDDEN_FILES = [
    "src",
    "lab-work",
    "archive",
    "INTENT-" + "ANALYSIS.md",
    "PARTITION-" + "ANALYSIS.md",
    "SYSTEMS-ATLAS-" + "PLAN.md",
    "HOW-TO-BUILD-" + "THE-ATLAS.md",
    "facts/" + "audit-2026-" + "11-04",
]

PROHIBITED_TOKENS = [
    "SA-2026" + ".14",
    "SA-2027" + ".1",
    "zi" + "p4",
    "zi" + "p5",
    "S5_" + "3",
    "SYSTEMS-ATLAS-" + "PLAN",
    "HOW-TO-BUILD-" + "THE-ATLAS",
    "INTENT-" + "ANALYSIS",
    "PARTITION-" + "ANALYSIS",
    "archive/" + "audit",
    "audit-2026-" + "11-04",
    "E3-" + "1",
    "E3-" + "2",
    "E3-" + "7",
    "đợt " + "E2",
    "đề xuất " + "D2",
    ".pri" + "vate/",
    ".cla" + "ude/",
    ".jul" + "es",
    "super" + "power",
    "C:\\" + "Users\\",
]


def test_paths_module_and_monorepo_layout():
    from tools import paths

    assert paths.ROOT == str(ROOT)
    assert paths.CONTENT_BOOK.endswith("content" + "\\" + "book") or paths.CONTENT_BOOK.endswith("content/book")
    assert len(paths.chapter_files()) == 145
    assert len(paths.edu_files()) >= 48
    assert not (ROOT / "src").exists()
    assert not (ROOT / "lab-work").exists()
    for rel in FORBIDDEN_FILES:
        assert not (ROOT / rel).exists(), f"Forbidden legacy path still present: {rel}"

    vi_cases = sorted((ROOT / "content" / "cases" / "vi").glob("*.md"))
    en_cases = sorted((ROOT / "content" / "cases" / "en").glob("*.md"))
    assert len(vi_cases) == 6
    assert len(en_cases) == 6
    assert (ROOT / "docs" / "00-CACH-DUNG-GOI.md").exists()


def test_public_tree_zero_prohibited_traces():
    exts = {".py", ".md", ".csv", ".txt", ".json", ".mjs", ".ts", ".astro", ".css", ".c", ".js"}
    hits = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in exts:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith((".git/", ".venv/", "site/node_modules/", "site/dist/", "dist/", "content/generated/")):
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for lno, line in enumerate(txt.splitlines(), 1):
            for tok in PROHIBITED_TOKENS:
                if tok in line:
                    hits.append(f"{rel}:{lno} contains {tok!r}")
    assert hits == [], "Found prohibited public traces:\n" + "\n".join(hits[:20])


def test_readme_is_minimal_and_neutral():
    readme = ROOT / "README.md"
    assert readme.exists(), "Missing README.md"
    lines = readme.read_text(encoding="utf-8").splitlines()
    assert 3 <= len(lines) <= 30, f"README.md should be minimal (<= 30 lines), got {len(lines)}"
    joined = "\n".join(lines).lower()
    for hype in ("img.shields.io", "awesome", "comprehensive guide", "best practices"):
        assert hype not in joined, f"Unexpected discovery/hype token in README: {hype}"
