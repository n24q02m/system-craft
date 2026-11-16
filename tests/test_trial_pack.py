import os

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_trial_00c_pdf_pack_and_scorecard_ready():
    tdir = os.path.join(ROOT, "trial-00c")
    pdf_path = os.path.join(tdir, "GOI-THU-NGHIEM-3-CHUONG.pdf")
    card_path = os.path.join(tdir, "PHIEU-CHAM-3-CHI-SO.md")

    assert os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0, "Missing trial PDF"
    assert os.path.exists(card_path) and os.path.getsize(card_path) > 0, "Missing trial scorecard"

    doc = pymupdf.open(pdf_path)
    pages = doc.page_count
    toc = doc.get_toc()
    assert 8 <= pages <= 35, f"Trial PDF page count out of range: {pages}"
    assert toc and toc[0][2] >= 2, f"First bookmark points to TOC page 1: {toc[:2]}"
    full_txt = "\n".join(doc[i].get_text("text") for i in range(pages))
    doc.close()

    for needle in ("P15-00", "0.1", "0.2", "1.1", "SA-2028.1"):
        assert needle in full_txt, f"Missing {needle} in trial PDF"

    card = open(card_path, encoding="utf-8").read()
    for needle in (
        "§0.0c",
        "rời atlas để hiểu từ",
        "số câu hỏi lại",
        "tự nêu được quyết định",
        "Option S",
        "30.000 từ",
        "Giữ nguyên khung",
        "≥2 cụm",
    ):
        assert needle in card, f"Missing '{needle}' in PHIEU-CHAM-3-CHI-SO.md"
