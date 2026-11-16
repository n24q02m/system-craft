#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate 145 Reference Cards, 433+60 Flashcards JSON, and 3 Appendix Indexes in content/generated/."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import paths  # noqa: E402

CLUSTER_CS2023 = {
    0: ("SEP / SF", "Nền tư duy hệ thống, tiên đề & nhận thức luận"),
    1: ("AR / SF", "Kiến trúc máy tính, CPU, lưu trữ, mạng vật lý & điện năng"),
    2: ("OS / PDC", "Hệ điều hành, bộ nhớ ảo, lập lịch, VFS, I/O & cô lập"),
    3: ("PL / SF", "Đồng thời, quản lý bộ nhớ runtime & giải phẫu tầng phục vụ"),
    4: ("NC / SE", "Giao thức truyền tải, API contracts, gRPC & realtime"),
    5: ("DM / PDC", "Storage engine, RDBMS, KV, queue/stream, lakehouse & vector"),
    6: ("HCI / NC", "Client constraints, local-first CRDT, CDN/edge & IoT"),
    7: ("HCI / SE", "Web rendering, state, INP performance, a11y & bảo mật FE"),
    8: ("PDC / SE", "Đồng thuận Raft, saga/outbox, sharding, resilience & DR"),
    9: ("PDC / SF", "Kubernetes, autoscaling, VPC/mesh, IaC & progressive delivery"),
    10: ("SEC", "Threat model, PQC, AuthN/AuthZ, OWASP, supply chain & tuân thủ"),
    11: ("SE / SEP", "SLI/SLO, OpenTelemetry, chaos, incident, FinOps & ADR"),
    12: ("AI", "LLM serving, RAG, agent/MCP, evals/guardrails & token economics"),
    13: ("SE / DM / AI", "7 playbook kiến trúc theo lớp tải thực chiến"),
    14: ("AR / SEC / PDC", "Biên giới ngành: bán dẫn, RF, DC, ML, HPC, game, chuẩn & mật mã"),
}


def _extract_section(md_text, sec_num):
    m = re.search(rf"^##\s+{sec_num}\.\s+[^\n]*\n(.*?)(?=^##\s+\d+\.|\Z)", md_text, re.S | re.M)
    return m.group(1).strip() if m else ""


def _parse_md_table(sec_text):
    rows = []
    for line in sec_text.splitlines():
        s = line.strip()
        if not s.startswith("|") or s.startswith(("|---", "| # ", "| Thông số", "| Triệu chứng")):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if any(cells) and not all(set(c) <= {"-", ":"} for c in cells):
            rows.append(cells)
    return rows


def build_reference_cards():
    """Build compact 145-chapter Reference Cards -> content/generated/cards-145.md."""
    os.makedirs(paths.CONTENT_GENERATED, exist_ok=True)
    edu_order = paths.read_csv_rows(os.path.join(paths.FACTS, "edu-order.csv"))
    ordered_paths = [os.path.join(paths.CONTENT_BOOK, r[0]) for r in edu_order if r and r[0].endswith(".md")]
    if len(ordered_paths) != 145:
        ordered_paths = paths.chapter_files()

    out = [
        "# SYSTEM CRAFT — 145 THẺ TRA CỨU NHANH (MICROPAEDIA)\n",
        "> Tổng hợp tự động từ `§1 Quyết định`, `§3 Số liệu` và `§5 Hỏng & Chẩn đoán` của toàn bộ 145 chương.\n",
    ]
    count = 0
    for fpath in ordered_paths:
        chap = paths.fname_to_chap(fpath)
        txt = open(fpath, encoding="utf-8").read()
        h1 = next((l[2:].strip() for l in txt.splitlines() if l.startswith("# ")), chap)
        dec_rows = _parse_md_table(_extract_section(txt, 1))
        num_rows = _parse_md_table(_extract_section(txt, 3))
        inc_rows = _parse_md_table(_extract_section(txt, 5))

        out.append(f"## Card {chap} — {h1.split('—', 1)[-1].strip()}\n")
        if dec_rows:
            out.append("**Quyết định cốt lõi:** " + " · ".join(r[1] if len(r) > 1 else r[0] for r in dec_rows[:4]))
        if num_rows:
            nums = [f"{r[0]}: `{r[1]}`" for r in num_rows[:4] if len(r) >= 2]
            if nums:
                out.append("**Con số neo:** " + " · ".join(nums))
        if inc_rows:
            incs = [f"{r[0]} → `{r[2] if len(r) > 2 else r[-1]}`" for r in inc_rows[:3] if len(r) >= 2]
            if incs:
                out.append("**Bệnh & chẩn đầu tiên:** " + " ; ".join(incs))
        out.append("")
        count += 1

    out_path = os.path.join(paths.CONTENT_GENERATED, "cards-145.md")
    open(out_path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    return count, out_path


def _extract_tu_cham_cards():
    cards = []
    # Extract selected solutions from P15-02-Q* and remaining solutions from P15-04-S*
    p15_sol_files = sorted(
        f for f in paths.edu_files()
        if os.path.basename(f).startswith(("P15-02-Q", "P15-04-S"))
        and not os.path.basename(f).startswith("P15-02-QA")
    )
    for fpath in p15_sol_files:
        deck = os.path.basename(fpath).replace(".md", "")
        txt = open(fpath, encoding="utf-8").read()
        blocks = re.split(r"(?=^###\s+)", txt, flags=re.M)
        for blk in blocks:
            if not blk.startswith("### "):
                continue
            lines = blk.splitlines()
            header = lines[0][4:].strip()
            body = "\n".join(lines[1:]).strip()
            if "**Tự chấm:**" not in body:
                continue
            m_ch = re.match(r"(\d+\.\d+(?:\.\d+)?)", header)
            chap = m_ch.group(1).lstrip("0") if m_ch else ""
            if chap.startswith("."):
                chap = "0" + chap
            sol_part, crit_part = body.split("**Tự chấm:**", 1)
            sol_clean = re.sub(r"^\*\*Lời giải:\*\*\s*", "", sol_part.strip())
            cards.append({
                "id": f"EX-{len(cards) + 1:03d}",
                "kind": "self-check",
                "deck": deck,
                "chapter": chap,
                "front": header,
                "back": sol_clean.strip(),
                "criteria": crit_part.strip(),
            })
    return cards


def _extract_qa_cards():
    cards = []
    qa_path = os.path.join(paths.CONTENT_BOOK, "P15-02-QA-nang-cao.md")
    if not os.path.exists(qa_path):
        return cards
    txt = open(qa_path, encoding="utf-8").read()
    q_sec, a_sec = txt.split("## Đáp án & giải thích", 1)
    ans_map = {}
    for line in a_sec.splitlines():
        m = re.match(r"^\|\s*(A\d+\.\d+)\s*\|\s*([A-D])\s*\|\s*(.+?)\s*\|$", line.strip())
        if m:
            ans_map[m.group(1)] = (m.group(2), m.group(3))

    for m in re.finditer(r"^(A\d+\.\d+)\.\s+(.+?)(?=\nA\d+\.\d+\.|\n### |\Z)", q_sec, re.S | re.M):
        qid = m.group(1)
        qtxt = m.group(2).strip()
        ans_letter, why = ans_map.get(qid, ("", ""))
        m_ch = re.search(r"\((\d+\.\d+(?:\.\d+)?)", why)
        cards.append({
            "id": qid,
            "kind": "decision-qa",
            "deck": "P15-02-QA",
            "chapter": m_ch.group(1) if m_ch else "",
            "front": f"{qid}. {qtxt}",
            "back": f"Đáp án {ans_letter}: {why}",
            "criteria": "Giải thích được ràng buộc bị phương án nhiễu bỏ qua",
        })
    return cards


def build_flashcards_json():
    """Export all 433 Tự chấm + 60 QA cards to content/generated/flashcards.json."""
    os.makedirs(paths.CONTENT_GENERATED, exist_ok=True)
    self_checks = _extract_tu_cham_cards()
    qas = _extract_qa_cards()
    all_cards = self_checks + qas
    payload = {
        "edition": "SA-2028.1",
        "self_check_count": len(self_checks),
        "qa_count": len(qas),
        "total": len(all_cards),
        "cards": all_cards,
    }
    out_path = os.path.join(paths.CONTENT_GENERATED, "flashcards.json")
    open(out_path, "w", encoding="utf-8", newline="\n").write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return len(self_checks), len(qas), out_path


def _extract_kit_course_map():
    course_of = {}
    specs = [
        ("SYS101", os.path.join(paths.KIT, "01-MON-1-NEN-TANG.md")),
        ("SYS102", os.path.join(paths.KIT, "02-MON-2-HE-THONG-THUC.md")),
        ("SYS103", os.path.join(paths.KIT, "02b-MON-3-QUY-MO-BIEN-GIOI.md")),
    ]
    for cname, spath in specs:
        if not os.path.exists(spath):
            continue
        txt = open(spath, encoding="utf-8").read()
        m = re.search(r"## 2\. Lịch 15 tuần.*?(?=^\*\*|## 3\.)", txt, re.S | re.M)
        if not m:
            continue
        for row in m.group().splitlines():
            if not row.startswith("|") or row.startswith(("| Tuần", "|---")):
                continue
            cells = [c.strip() for c in row.strip("|").split("|")]
            if len(cells) < 2:
                continue
            col = cells[1]
            for rng in re.finditer(r"(\d+\.\d+\.)(\d+)[–-]\1(\d+)", col):
                for k in range(int(rng.group(2)), int(rng.group(3)) + 1):
                    course_of[f"{rng.group(1)}{k}"] = cname
                col = col.replace(rng.group(0), " ")
            for rng in re.finditer(r"\b(\d+)\.(\d+)[–-]\1\.(\d+)\b", col):
                for k in range(int(rng.group(2)), int(rng.group(3)) + 1):
                    course_of[f"{rng.group(1)}.{k}"] = cname
                col = col.replace(rng.group(0), " ")
            for tok in re.findall(r"\b\d+\.\d+(?:\.\d+)?\b", col):
                course_of[tok] = cname
    return course_of


def build_three_indexes():
    """Generate INDEX-DECISIONS.md, INDEX-INCIDENTS.md, and INDEX-CS2023.md."""
    os.makedirs(paths.CONTENT_GENERATED, exist_ok=True)
    decs = paths.read_csv_dicts(os.path.join(paths.FACTS, "coverage-decisions.csv"))
    incs = paths.read_csv_dicts(os.path.join(paths.FACTS, "coverage-incidents.csv"))

    # 1. Decisions Index
    d_lines = [
        f"# INDEX-DECISIONS — Danh mục {len(decs)} Quyết định Kiến trúc\n",
        "| ID | Quyết định | Câu hỏi tự vấn | Chương |",
        "|---|---|---|---:|",
    ]
    for r in decs:
        d_lines.append(f"| `{r['id']}` | {r['decision']} | {r['question']} | `{r['chapter']}` |")
    d_path = os.path.join(paths.CONTENT_GENERATED, "INDEX-DECISIONS.md")
    open(d_path, "w", encoding="utf-8", newline="\n").write("\n".join(d_lines) + "\n")

    # 2. Incidents Index
    i_lines = [
        f"# INDEX-INCIDENTS — Danh mục {len(incs)} Sự cố & Lệnh chẩn\n",
        "| ID | Triệu chứng | Nguyên nhân hàng đầu | Kiểm tra đầu tiên | Chương |",
        "|---|---|---|---|---:|",
    ]
    for r in incs:
        i_lines.append(
            f"| `{r['id']}` | {r['symptom']} | {r['likely_causes']} | `{r['first_check']}` | `{r['chapter']}` |"
        )
    i_path = os.path.join(paths.CONTENT_GENERATED, "INDEX-INCIDENTS.md")
    open(i_path, "w", encoding="utf-8", newline="\n").write("\n".join(i_lines) + "\n")

    # 3. CS2023 & Curriculum Mapping Index
    courses = _extract_kit_course_map()
    c_lines = [
        "# INDEX-CS2023 — Ánh xạ 145 Chương theo ACM/IEEE/AAAI CS2023 & 3 Môn Kit\n",
        "| Chương | Tiêu đề | Cụm | Môn Kit | Knowledge Area (CS2023) |",
        "|---|---|---|---|---|",
    ]
    for fpath in paths.chapter_files():
        chap = paths.fname_to_chap(fpath)
        txt = open(fpath, encoding="utf-8").read()
        h1 = next((l[2:].strip() for l in txt.splitlines() if l.startswith("# ")), chap)
        cl = int(chap.split(".")[0])
        ka, _desc = CLUSTER_CS2023.get(cl, ("SF", ""))
        course = courses.get(chap, "Phụ lục (Đọc khi cần)")
        c_lines.append(f"| `{chap}` | {h1} | `P{cl}` | `{course}` | `{ka}` |")
    c_path = os.path.join(paths.CONTENT_GENERATED, "INDEX-CS2023.md")
    open(c_path, "w", encoding="utf-8", newline="\n").write("\n".join(c_lines) + "\n")

    return len(decs), len(incs)


def build_all():
    n_ref, _ = build_reference_cards()
    n_sc, n_qa, _ = build_flashcards_json()
    n_dec, n_inc = build_three_indexes()
    return dict(ref_cards=n_ref, self_checks=n_sc, qa=n_qa, decisions=n_dec, incidents=n_inc)


if __name__ == "__main__":
    res = build_all()
    print(
        f"CARDS & INDEXES: {res['ref_cards']} ref cards · "
        f"{res['self_checks']}+{res['qa']} flashcards · "
        f"{res['decisions']} decisions · {res['incidents']} incidents"
    )
