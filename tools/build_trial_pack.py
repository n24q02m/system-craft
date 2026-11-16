#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble the §0.0c 3-chapter empirical trial pack (trial-00c/) without touching source chapters."""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import build  # noqa: E402
from tools.paths import CONTENT_BOOK, TRIAL  # noqa: E402
from tools.pdf_render import render_pdf_with_fallback  # noqa: E402


SCORECARD_MD = """# PHIẾU CHẤM 3 CHỈ SỐ — THỬ NGHIỆM THỰC NGHIỆM §0.0c

> **Gói đọc thử:** [`GOI-THU-NGHIEM-3-CHUONG.pdf`](./GOI-THU-NGHIEM-3-CHUONG.pdf) (`P15-00` rút gọn + chương `0.1`, `0.2`, `1.1`)  
> **Đối tượng thử (persona a):** Người biết lập trình cơ bản (biến, hàm, vòng lặp) hoặc người ngoài chuyên ngành hệ thống.  
> **Nguyên tắc §0.0c:** Không có số đo thực tế từ phiếu này thì **không mở lại khung sách**, **không sinh Option S**, và **không viết lại 145 chương**.

---

## 1. Bảng ghi 3 chỉ số trên từng người đọc thử

Mỗi người đọc độc lập 3 chương (`0.1`, `0.2`, `1.1`) kèm hướng dẫn ngắn `P15-00` và ghi nhận ngay khi đọc (không giải thích miệng trước):

| Người đọc thử (mã / nền tảng) | Chỉ số 1: số lần **rời atlas để hiểu từ** (Google/AI ngoài sách) | Chỉ số 2: **số câu hỏi lại** tác giả vì đọc không hiểu đoạn viết | Chỉ số 3: **tự nêu được quyết định** của từng chương (`0.1 / 0.2 / 1.1` = ?/3) | Thời gian đọc (phút) | Ghi chú đoạn vướng cụ thể |
|---|---:|---:|:---:|---:|---|
| Người 1 (`...`) | `___` lần | `___` câu | `___ / 3` | `___` | `...` |
| Người 2 (`...`) | `___` lần | `___` câu | `___ / 3` | `___` | `...` |
| Người 3 (`...`) | `___` lần | `___` câu | `___ / 3` | `___` | `...` |

### Cách chấm nhanh Chỉ số 3 ("tự nêu được quyết định")
Sau khi đọc xong mỗi chương, người đọc gấp PDF lại và trả lời 3 câu sau trong ≤2 phút mỗi chương:
- **Chương 0.1:** Khi tranh luận kiến trúc hay chọn công nghệ, **7 trục** dùng để tách điều gì và khi nào buộc phải dừng tối ưu một trục?
- **Chương 0.2:** Kể được ít nhất **3 tiên đề (A1–A10)** có thể sập theo thời gian và cho biết mình kiểm tra dấu hiệu gãy ở đâu?
- **Chương 1.1:** Tại sao gọi `DB query` trong vòng lặp `N+1` lại đắt gấp hàng chục nghìn lần đọc RAM, và 4 quyết định phân bổ độ trễ (`D1–D4`) quyết định thứ tự gì?

---

## 2. Ngưỡng quyết định & Nhánh hành động sau khi có số đo

| Kết quả tổng hợp | Nhánh kích hoạt theo quy chuẩn §0.0c | Việc làm tiếp theo |
|---|---|---|
| Cả 3 chỉ số đạt yêu cầu (tự nêu được quyết định ≥2/3 chương, số lần rời sách và câu hỏi lại ở mức thấp chấp nhận được) | **Giữ nguyên khung** (`Hold` — không sửa thân sách) | Chốt phát hành **SA-2028.1-LEARNER** hiện tại; không viết thêm tầng dẫn chuyện |
| Trượt **chỉ số 3** (người đọc không tự nêu được quyết định dù vẫn hiểu từng câu) trong khi từ vựng/câu hỏi không quá nghẽn | Kích hoạt **Option S** (~`30.000 từ` — 15 *"mùa"* dẫn chuyện, ~2.000 từ/mùa) | Viết bổ sung tầng dẫn chuyện ngoài thân chương; giữ 145 chương làm phần tra cứu |
| Trượt **cả 3 chỉ số ở ≥2 cụm** (người đọc vừa phải rời atlas tra từ liên tục, vừa hỏi lại nhiều câu, vừa không nêu được quyết định) | Mở thảo luận viết lại thân bài người học (*Core Rewrite*) | Đánh giá sửa trực tiếp phần giải thích trong `content/book/P0–P14` theo từng cụm bị trượt |
"""


def build_trial_pack(out_dir=None):
    out_dir = out_dir or TRIAL
    os.makedirs(out_dir, exist_ok=True)

    p15_00_full = open(os.path.join(CONTENT_BOOK, "P15-00-tang-hoc-cach-dung.md"), encoding="utf-8").read()
    # Short guide (~1-2 pages): sections 0–3 before §4 ("Ba tốc độ đọc")
    p15_short = p15_00_full.split("## 4. Ba tốc độ đọc")[0].strip()
    p15_short += "\n\n> *Bản rút gọn cho gói thử nghiệm §0.0c (3 chương: `0.1`, `0.2`, `1.1`). Đọc hết `§1–§3` (~3 phút) rồi đọc tuần tự 3 chương tiếp theo.*\n"

    bridges = build.load_edu_bridges()
    items = [
        ("P15-00-short.md", p15_short),
        ("P0-00-1-he-quy-chieu.md", open(os.path.join(CONTENT_BOOK, "P0-00-1-he-quy-chieu.md"), encoding="utf-8").read()),
        ("P0-00-2-tien-de.md", open(os.path.join(CONTENT_BOOK, "P0-00-2-tien-de.md"), encoding="utf-8").read()),
        ("P1-01-bac-thang-do-tre.md", open(os.path.join(CONTENT_BOOK, "P1-01-bac-thang-do-tre.md"), encoding="utf-8").read()),
    ]
    parts = []
    words_total = 0
    for fn, txt in items:
        ch = build.fname_to_chap(fn)
        if ch in bridges:
            txt = f"> **Nhịp nối (tuyến học)** — {bridges[ch]}\n\n" + txt
        w = len(txt.split())
        words_total += w
        parts.append((os.path.join(CONTENT_BOOK, fn), txt, w, True))

    stats = {
        "profile": "edu",
        "chapters": 3,
        "done": 3,
        "todo": 0,
        "words": words_total,
        "edu": 1,
        "dec": 0,
        "inc": 0,
    }
    html_doc = build.render_html_doc(
        parts,
        stats,
        title_override="SYSTEMS ATLAS (SA-2028.1) — GÓI THỬ NGHIỆM 3 CHƯƠNG (§0.0c)",
    )
    pdf_path = os.path.join(out_dir, "GOI-THU-NGHIEM-3-CHUONG.pdf")
    with tempfile.TemporaryDirectory() as td:
        tmp_html = os.path.join(td, "trial.html")
        open(tmp_html, "w", encoding="utf-8").write(html_doc)
        backend = render_pdf_with_fallback(tmp_html, pdf_path, build.PRINT_CSS)

    card_path = os.path.join(out_dir, "PHIEU-CHAM-3-CHI-SO.md")
    open(card_path, "w", encoding="utf-8", newline="\n").write(SCORECARD_MD)
    print(f"TRIAL-00C ({backend}): {pdf_path} & {card_path}")
    return pdf_path, card_path


if __name__ == "__main__":
    build_trial_pack()
