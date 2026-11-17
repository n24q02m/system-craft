import pathlib
import re
from html import unescape

ROOT = pathlib.Path(__file__).resolve().parent.parent

ASTRO_BUILD_COMMAND = "bun run --cwd site build"
CI_GENERATOR_COMMANDS = (
    "uv run python tools/build_glossary.py",
    "uv run python tools/package_release.py",
    "uv run python kit/make_kit.py",
    "uv run python kit/slides/build_slides.py",
    "uv run python tools/build_trial_pack.py",
)
TEXT_SUFFIXES = {".md", ".html", ".txt", ".csv", ".json", ".xml"}


def _read(relative_path):
    path = ROOT / relative_path
    assert path.is_file(), f"Missing {relative_path}"
    return path.read_text(encoding="utf-8")


def _normalized_text(relative_path):
    text = _read(relative_path)
    if (ROOT / relative_path).suffix.lower() == ".html":
        text = unescape(re.sub(r"<[^>]+>", " ", text))
    return " ".join(text.replace("`", "").split())


def _ci_commands(text):
    prefixes = ("uv run python", "uv sync", "bun install", "bun run")
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith(prefixes)
    ]


def _yaml_value(line, key):
    prefix = f"{key}:"
    if not line.startswith(prefix):
        return None
    return line[len(prefix):].strip().strip("\"'")


def _dependabot_updates(text):
    updates = []
    current = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- package-ecosystem:"):
            current = {
                "ecosystem": _yaml_value(line[2:], "package-ecosystem"),
                "directory": None,
                "interval": None,
            }
            updates.append(current)
            continue
        if current is None:
            continue
        directory = _yaml_value(line, "directory")
        if directory is not None:
            current["directory"] = directory
            continue
        interval = _yaml_value(line, "interval")
        if interval is not None:
            current["interval"] = interval
    return updates


def test_ci_generators_precede_astro_build_and_dependabot_schedule():
    ci_txt = _read(".github/workflows/ci.yml")
    commands = _ci_commands(ci_txt)

    build_positions = [
        idx for idx, command in enumerate(commands)
        if command == ASTRO_BUILD_COMMAND
    ]
    assert len(build_positions) == 1, (
        f"Expected one Astro build command in ci.yml, got {len(build_positions)}"
    )
    build_idx = build_positions[0]
    for generator in CI_GENERATOR_COMMANDS:
        positions = [
            idx for idx, command in enumerate(commands)
            if command == generator
        ]
        assert positions, f"Missing generator command in ci.yml: {generator}"
        assert max(positions) < build_idx, (
            f"Generator command must precede Astro build: {generator}"
        )

    frozen_commands = [command for command in commands if "--frozen" in command]
    assert "uv sync --frozen --dev" in frozen_commands, (
        "ci.yml must pin Python dependencies with uv sync --frozen"
    )
    assert "bun install --cwd site --frozen-lockfile" in frozen_commands, (
        "ci.yml must pin Astro dependencies with --frozen-lockfile"
    )
    for command in (
        "uv run python tools/red_thread_check.py --with-src",
        "uv run python tools/maintenance_check.py",
    ):
        assert command in commands, f"Missing CI validator command: {command}"

    dependabot_txt = _read(".github/dependabot.yml")
    assert re.search(r"(?m)^version:\s*2\s*$", dependabot_txt), (
        "dependabot.yml must use version 2"
    )
    updates = _dependabot_updates(dependabot_txt)
    assert len(updates) == 3, f"Expected 3 Dependabot updates, got {len(updates)}"
    configured = {
        (update["ecosystem"], update["directory"], update["interval"])
        for update in updates
    }
    assert configured == {
        ("uv", "/", "weekly"),
        ("npm", "/site", "weekly"),
        ("github-actions", "/", "weekly"),
    }, f"Unexpected Dependabot weekly ecosystems: {configured}"


def test_docs_and_kit_corrections_are_present():
    kit_texts = {
        "kit/00-DOC-TRUOC.md": _normalized_text("kit/00-DOC-TRUOC.md"),
        "dist/SA-2028.1-KIT/SA-2028.1-KIT.md": _normalized_text(
            "dist/SA-2028.1-KIT/SA-2028.1-KIT.md"
        ),
        "dist/SA-2028.1-KIT/SA-2028.1-KIT.html": _normalized_text(
            "dist/SA-2028.1-KIT/SA-2028.1-KIT.html"
        ),
    }
    for label, txt in kit_texts.items():
        assert "bộ slide 30 chương xương sống SYS101–103" in txt, (
            f"Missing corrected 30-chapter SYS101–103 overview in {label}"
        )
        assert "30 chương ★ của cả ba môn SYS101–103" in txt, (
            f"Missing corrected 30-star SYS101–103 statement in {label}"
        )
        assert re.search(r"11 của SYS101 \+ 10 của SYS102 \+ 9 của SYS103", txt), (
            f"Missing corrected 11+10+9 breakdown in {label}"
        )
        assert "11 chương xương sống" not in txt, (
            f"Stale 11-chapter overview remains in {label}"
        )
        assert "11 chương ★ của SYS101" not in txt, (
            f"Stale SYS101-only star statement remains in {label}"
        )

    guide_texts = {
        "docs/00-CACH-DUNG-GOI.md": _normalized_text("docs/00-CACH-DUNG-GOI.md"),
        "dist/SA-2028.1-LEARNER/00-CACH-DUNG-GOI.md": _normalized_text(
            "dist/SA-2028.1-LEARNER/00-CACH-DUNG-GOI.md"
        ),
    }
    for label, txt in guide_texts.items():
        assert "50 văn kiện" in txt, f"Missing corrected 50-document count in {label}"
        assert "44 văn kiện" not in txt, f"Stale 44-document count remains in {label}"
        assert "L09–L11" in txt, f"Missing corrected L09–L11 lab range in {label}"
        assert "L9–L11" not in txt, f"Stale L9–L11 lab range remains in {label}"
        assert "kit/04-NGAN-HANG-DE-THI.md" in txt, (
            f"Missing kit exam-bank pointer in {label}"
        )
        assert "Option S" not in txt, f"Option S must stay out of {label}"

    question_bank = ROOT / "kit" / "04-NGAN-HANG-DE-THI.md"
    assert question_bank.is_file() and question_bank.stat().st_size > 0, (
        "Missing kit/04-NGAN-HANG-DE-THI.md"
    )

    for relative_path in (
        "dist/SA-2028.1-LEARNER/DRAFT-tham-chieu.md",
        "site/src/pages/vi/book/index.astro",
        "site/dist/vi/book/index.html",
    ):
        txt = _read(relative_path)
        assert "50 văn kiện" in txt, (
            f"Missing corrected 50-document count in {relative_path}"
        )
        assert "44 văn kiện" not in txt, (
            f"Stale 44-document count remains in {relative_path}"
        )

    runbook = _read("docs/MAINTENANCE-RUNBOOK.md")
    assert "§0.0c" in runbook and "viết thêm `Option S`" in runbook, (
        "USER-GATE §0.0c runbook marker is missing"
    )
    scorecard = _read("trial-00c/PHIEU-CHAM-3-CHI-SO.md")
    assert "§0.0c" in scorecard and "không sinh Option S" in scorecard, (
        "USER-GATE §0.0c scorecard marker is missing"
    )
    trial_builder = _read("tools/build_trial_pack.py")
    assert "§0.0c" in trial_builder and "không sinh Option S" in trial_builder, (
        "USER-GATE §0.0c generator marker is missing"
    )

    for relative_path in (
        "README.md",
        "docs/00-CACH-DUNG-GOI.md",
        "kit/00-DOC-TRUOC.md",
    ):
        assert "Option S" not in _read(relative_path), (
            f"Option S must stay out of public source document {relative_path}"
        )

    dist_dir = ROOT / "dist"
    assert dist_dir.is_dir(), "Missing generated dist/ directory"
    bad_names = []
    bad_contents = []
    for path in sorted(dist_dir.rglob("*")):
        relative_path = path.relative_to(ROOT).as_posix()
        normalized_name = re.sub(r"[\s_-]+", " ", path.name.lower())
        if "option s" in normalized_name:
            bad_names.append(relative_path)
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            txt = path.read_text(encoding="utf-8", errors="replace")
            if "Option S" in txt:
                bad_contents.append(relative_path)
    assert bad_names == [], f"Option S artifacts found in dist/: {bad_names}"
    assert bad_contents == [], f"Option S text found in dist/: {bad_contents}"
