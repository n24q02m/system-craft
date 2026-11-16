#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract bilingual engineering glossary from book chapters into facts/glossary.csv."""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import paths  # noqa: E402

OUT_CSV = os.path.join(paths.FACTS, "glossary.csv")

# Curated bilingual English equivalents for Vietnamese-first §0 glossary entries
VI_TO_EN_HINTS = {
    "độ trễ": "Latency — end-to-end duration of a single operation.",
    "bậc thang": "Latency hierarchy — discrete orders of magnitude separating hardware/network tiers.",
    "luật little": "Little's Law — L = lambda * W: average items in system equals arrival rate times residence time.",
    "hệ quy chiếu": "Reference frame — shared coordinate axes and vocabulary to evaluate architectural tradeoffs.",
    "trục": "Design axis — independent evaluation dimension on the systems map.",
    "tiên đề": "Axiom — foundational assumption bounded by stated operating conditions.",
    "điều kiện biên": "Boundary condition — parameter regime where a design assumption stops holding.",
    "lăng kính": "Review lens — structured analytical perspective with concrete audit questions.",
    "động từ": "Engineering verb — recurring mode of work across design, diagnosis, and operations.",
    "nhãn nguồn": "Provenance label — P (primary), I (independent measurement), V (vendor), E (estimate).",
    "mạng": "Network — shared packet transport introducing serialization, propagation, and queueing delay.",
    "chịu lỗi": "Fault tolerance — continued bounded operation despite component crash or partition.",
    "đồng thuận": "Consensus — agreement among a quorum of replicas on a shared state or log order.",
    "khóa phân tán": "Distributed lock — lease-backed exclusivity guard needing fencing tokens for safety.",
    "nhất quán cuối": "Eventual consistency — replicas converge after quiescence without synchronous coordination.",
    "bộ nhớ ảo": "Virtual memory — OS-managed address translation backed by page tables, TLB, and swap/reclaim.",
    "hàng đợi": "Queue — explicit buffer absorbing burst mismatched producer/consumer rates.",
    "nút cổ chai": "Bottleneck — resource saturating first and bounding system throughput or tail latency.",
    "tràn bộ nhớ": "Out-of-Memory (OOM) — memory exhaustion triggering kernel OOM killer or process abort.",
    "chuyển ngữ cảnh": "Context switch — saving/restoring thread/process CPU state across scheduler preemption.",
    "giám sát": "Observability — metrics, logs, and traces exposing internal runtime state externally.",
    "dự phòng": "Redundancy — N+1/active-active headroom surviving single-component failure.",
    "phân mảnh": "Sharding / fragmentation — partitioning state by key range or hash across nodes/pages.",
}

ENTRY_RE = re.compile(
    r"\*([^*]{1,90})\*\s*[—–:\-]+\s*(.+?)(?=;\s*\*[^*]{1,90}\*\s*[—–:\-]+|$)"
)
PAREN_EN_RE = re.compile(r"^(.*?)\s*\(([A-Za-z0-9][A-Za-z0-9 /\-\.+]{1,40})\)\s*$")
ASCII_TERM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 /\-\.+_']*$" )


# Curated cross-cutting CS/ML/Systems terms connecting book chapters and case studies
CORE_BILINGUAL_TERMS = [
    ("latency", "độ trễ hoàn thành một tác vụ đầu-cuối (đo theo p50/p95/p99, không chỉ trung bình)", "Latency — end-to-end duration of a single request or operation, measured in quantiles.", "1.1"),
    ("throughput", "số đơn vị công việc hoàn thành mỗi giây (req/s, tok/s, MB/s)", "Throughput — completed units of work per second under steady load.", "1.1;3.1"),
    ("quantization", "giảm độ chính xác trọng số/activation (BF16 → FP8/INT8/INT4) để giảm VRAM và tăng tốc decode", "Quantization — reducing numeric precision of weights/activations to shrink memory footprint and latency.", "12.2;14.4.3"),
    ("perplexity", "độ đo mức bối rối của mô hình ngôn ngữ khi dự đoán token tiếp theo (chỉ so được trên cùng bộ tách từ)", "Perplexity — exp(cross-entropy loss) over next-token prediction; only comparable across identical tokenizers.", "12.1;12.5"),
    ("tokenizer", "bộ tách văn bản thành chuỗi mã số nguyên (BPE, Unigram, WordPiece) quyết định độ dài ngữ cảnh và chi phí", "Tokenizer — deterministic segmentation mapping raw text into discrete vocabulary IDs before the model.", "12.1;12.6"),
    ("embedding", "vector số thực chiều cố định biểu diễn ngữ nghĩa của văn bản, âm thanh hoặc ảnh", "Embedding — dense continuous vector encoding semantic similarity in metric space.", "5.10;12.3"),
    ("attention", "cơ chế tự chú ý (Q·K^T) cho phép mô hình gán trọng số ngữ cảnh giữa mọi cặp token; tốn O(N²) compute & KV cache", "Self-attention — pairwise contextual weighting across sequence tokens scaling quadratically in context length.", "12.2;14.4.1"),
    ("KV cache", "bộ nhớ đệm lưu các tensor Key/Value của những token đã tính để không tính lại khi sinh token tiếp", "KV cache — persisted key/value attention tensors reusing past prefix computation during autoregressive decoding.", "12.2"),
    ("LoRA", "Low-Rank Adaptation — tinh chỉnh trọng số bằng hai ma trận hạng thấp thay vì cập nhật toàn bộ mô hình", "LoRA — low-rank matrix adapters fine-tuning large frozen base weights cheaply.", "12.7"),
    ("Transformer", "kiến trúc mạng nơ-ron dựa trên self-attention chạy song song lúc huấn luyện và đọc băng thông HBM lúc suy luận", "Transformer — attention-based architecture parallelizable in training/prefill and memory-bandwidth bound during decode.", "12.1;14.4.1"),
    ("data leakage", "rò rỉ dữ liệu kiểm định vào tập huấn luyện hoặc bước tiền xử lý (normalization, split sai chiều thời gian)", "Data leakage — evaluation information inadvertently influencing training or preprocessing statistics.", "0.4;12.5"),
    ("overfitting", "mô hình học thuộc nhiễu của tập train, giảm độ chính xác khi chuyển sang dữ liệu mới", "Overfitting — excess model capacity fitting training idiosyncrasies at the expense of out-of-distribution generalization.", "12.5;14.4.1"),
    ("RAM", "bộ nhớ chính DRAM (~100 ns/truy cập ngẫu nhiên), nhanh hơn SSD ~1000× nhưng mất khi cúp điện", "RAM (DRAM) — volatile main memory (~100 ns access) bridging fast CPU caches and persistent storage.", "1.1;1.3"),
    ("GPU", "bộ xử lý song song mật độ cao ưu tiên thông lượng FLOPs và băng thông HBM hơn độ trễ đơn luồng", "GPU — wide-SIMD parallel accelerator trading single-thread latency for massive compute and HBM bandwidth.", "1.5;12.2"),
    ("vector", "mảng số biểu diễn đặc trưng đa chiều phục vụ tìm kiếm lân cận gần đúng (ANN/HNSW)", "Vector — multi-dimensional numeric feature point indexed by approximate nearest-neighbor structures.", "5.10;12.3"),
    ("HNSW", "Hierarchical Navigable Small World — đồ thị nhiều tầng tìm lân cận gần đúng nhanh trong RAM", "HNSW — multi-layer proximity graph offering sublinear approximate nearest-neighbor recall at high RAM cost.", "5.10"),
    ("BM25", "hàm xếp hạng từ khoá kinh điển (TF-IDF chuẩn hoá độ dài tài liệu) luôn cần làm nhánh đối chiếu với tìm kiếm ngữ nghĩa", "BM25 — lexical relevance scoring family complementing dense semantic retrieval in hybrid search.", "5.6;12.3"),
    ("ARIMA", "mô hình thống kê chuỗi thời gian tuyến tính (AutoRegressive Integrated Moving Average) chuẩn để làm baseline", "ARIMA — classical autoregressive statistical baseline for stationary and seasonal time series.", "5.11"),
    ("baseline", "mô hình hoặc hệ đo đơn giản nhất chạy được đầu cuối để làm mốc so sánh mọi cải tiến phức tạp", "Baseline — simplest end-to-end reference system required before adding modeling or architectural complexity.", "0.4;12.5"),
    ("token", "đơn vị văn bản (subword BPE) đầu vào/ra của LLM, hoặc biến thiết kế / vé xác thực tuỳ ngữ cảnh", "Token — subword unit processed by language models (12.6), bearer auth credential (10.3), or design variable (7.4).", "7.4;10.3;12.6"),
    ("distillation", "chưng cất tri thức — dạy mô hình nhỏ (student) bắt chước phân phối đầu ra của mô hình lớn (teacher)", "Knowledge distillation — training a compact student model against a larger teacher model's soft predictions.", "12.2;12.7"),
]


def _extract_en_gloss(raw_term, clean_term, vi_gloss):
    m = PAREN_EN_RE.match(raw_term)
    if m:
        alias = m.group(2).strip()
        if ASCII_TERM_RE.match(alias):
            return f"{alias} — {vi_gloss}"
    low = clean_term.lower()
    for k, hint in VI_TO_EN_HINTS.items():
        if k in low:
            return hint
    if ASCII_TERM_RE.match(clean_term):
        return f"{clean_term} — {vi_gloss}"
    return vi_gloss


def build_glossary(out_csv=OUT_CSV):
    """Extract and deduplicate §0 glossary terms across all 145 book chapters."""
    entries = {}  # lower_term -> dict

    for fpath in paths.chapter_files():
        chap = paths.fname_to_chap(fpath)
        txt = open(fpath, encoding="utf-8").read()
        for line in txt.splitlines():
            if not line.startswith("**Thuật ngữ sẽ gặp:**"):
                continue
            body = line.split("**Thuật ngữ sẽ gặp:**", 1)[1].strip()
            for m in ENTRY_RE.finditer(body):
                raw_term = m.group(1).strip()
                vi_gloss = m.group(2).strip().rstrip(".").strip()
                if not raw_term or not vi_gloss:
                    continue
                pm = PAREN_EN_RE.match(raw_term)
                clean_term = pm.group(1).strip() if pm else raw_term
                alias_en = pm.group(2).strip() if pm else ""

                key = clean_term.lower()
                if key not in entries:
                    en_gloss = _extract_en_gloss(raw_term, clean_term, vi_gloss)
                    entries[key] = {
                        "term": clean_term,
                        "vi_gloss": vi_gloss,
                        "en_gloss": en_gloss,
                        "chapters": [chap],
                        "source": "book-s0",
                    }
                else:
                    if chap not in entries[key]["chapters"]:
                        entries[key]["chapters"].append(chap)

                # Also expose English alias as direct searchable entry if parenthetical
                if alias_en and ASCII_TERM_RE.match(alias_en) and len(alias_en) >= 2:
                    ekey = alias_en.lower()
                    if ekey not in entries:
                        entries[ekey] = {
                            "term": alias_en,
                            "vi_gloss": f"{clean_term}: {vi_gloss}",
                            "en_gloss": f"{alias_en} ({clean_term}) — {vi_gloss}",
                            "chapters": [chap],
                            "source": "book-s0-alias",
                        }
                    elif chap not in entries[ekey]["chapters"]:
                        entries[ekey]["chapters"].append(chap)

    for term, vi_g, en_g, chs in CORE_BILINGUAL_TERMS:
        k = term.lower()
        if k not in entries:
            entries[k] = {
                "term": term,
                "vi_gloss": vi_g,
                "en_gloss": en_g,
                "chapters": chs.split(";"),
                "source": "curated-bilingual",
            }
        else:
            if not entries[k]["en_gloss"] or entries[k]["en_gloss"] == entries[k]["vi_gloss"]:
                entries[k]["en_gloss"] = en_g
            for ch in chs.split(";"):
                if ch not in entries[k]["chapters"]:
                    entries[k]["chapters"].append(ch)

    rows = sorted(entries.values(), key=lambda r: r["term"].lower())
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        f.write("# GLOSSARY — thuat ngu song ngu System Craft (sinh tu 145 chuong)\n")
        writer = csv.DictWriter(f, fieldnames=["term", "vi_gloss", "en_gloss", "chapters", "source"])
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "term": r["term"],
                "vi_gloss": r["vi_gloss"],
                "en_gloss": r["en_gloss"],
                "chapters": ";".join(r["chapters"]),
                "source": r["source"],
            })
    return len(rows)


if __name__ == "__main__":
    n = build_glossary()
    print(f"GLOSSARY: wrote {n} terms -> {os.path.relpath(OUT_CSV, paths.ROOT)}")
