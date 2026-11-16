import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import build  # noqa: E402


def test_build_module_exposes_f1_helpers_and_version():
    assert getattr(build, "EDITION_VER", None) == "SA-2028.1"
    bridges = build.load_edu_bridges()
    assert len(bridges) == 10
    assert "14.3.1" in bridges
    assert callable(getattr(build, "preflight", None))
    assert callable(getattr(build, "render_pdf_with_fallback", None))


def test_assemble_edu_has_200_units_qa_before_appendix_and_10_bridges(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "OUT_MD", str(tmp_path / "edu.md"))
    files, parts, _done, _todo, _words = build.assemble("edu")
    names = [os.path.basename(f) for f, _txt, _w, _wr in parts]
    assert len(parts) == 200
    assert names.index("P15-03-L12-p12.md") == names.index("P15-02-Q12-p12.md") + 1
    assert names.index("P15-03-L13-p13.md") == names.index("P15-02-Q13-p13.md") + 1
    assert names.index("P15-03-L14-p14.md") == names.index("P15-02-Q14-p14.md") + 1
    assert names.index("P15-02-QA-nang-cao.md") < names.index("_PART-9.md")
    bridged_texts = [txt for _f, txt, _w, _wr in parts if "> **Nhịp nối (tuyến học)**" in txt]
    assert len(bridged_texts) == 10


def test_assemble_draft_has_zero_bridges_and_all_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "OUT_MD", str(tmp_path / "draft.md"))
    _files, parts, done, todo, _words = build.assemble("draft")
    assert done == 145
    assert todo == 0
    assert len(parts) == 195
    bridged_texts = [txt for _f, txt, _w, _wr in parts if "> **Nhịp nối (tuyến học)**" in txt]
    assert len(bridged_texts) == 0
