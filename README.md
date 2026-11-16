# system-craft

Technical engineering notes, bilingual essays, and static build tooling.

- Web: <https://n24q02m.github.io/system-craft/>
- Guide: [docs/00-CACH-DUNG-GOI.md](docs/00-CACH-DUNG-GOI.md)

## Layout

- `content/book/` — markdown source chapters
- `content/cases/` — bilingual engineering notes (`vi/`, `en/`)
- `facts/` — reference tables and verification metadata
- `kit/` — syllabus notes and slide sources
- `labs/` — local measurement scripts and Docker verification
- `site/` — Astro static site
- `tools/` — verification and multi-format exporters (`.md`, `.html`, `.docx`, `.pdf`)
- `docs/` — usage and maintenance notes

## Build

```sh
uv sync --dev
uv run pytest -v
bun run --cwd site build
```
