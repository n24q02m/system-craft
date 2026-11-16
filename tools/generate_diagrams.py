#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate 30 XML-valid schematic SVG diagrams for the 30★ backbone chapters and write facts/diagrams.csv."""
import csv
import html
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import paths  # noqa: E402


def _e(text):
    return html.escape(str(text), quote=True)


def _mid(chap):
    return "arr-" + chap.replace(".", "-")


def svg_wrap(chap, width, height, aria, inner):
    m = _mid(chap)
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{_e(aria)}" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        f'  <defs><marker id="{m}" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">\n'
        f'    <path d="M0,0.5 L6.5,3.5 L0,6.5 z" fill="currentColor"/></marker></defs>\n'
        f'{inner}\n'
        f'</svg>\n'
    )


def box(x, y, w, h, title, sub="", cls="box", sub2="", title_size=11.5):
    out = [f'  <rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}"/>']
    ty = y + 18 if sub else y + h / 2 + 4
    out.append(f'  <text x="{x + 10}" y="{ty}" font-size="{title_size}" font-weight="600">{_e(title)}</text>')
    if sub:
        out.append(f'  <text x="{x + 10}" y="{y + 33}" font-size="9.5" class="dim">{_e(sub)}</text>')
    if sub2:
        out.append(f'  <text x="{x + 10}" y="{y + 46}" font-size="9.5" class="dim">{_e(sub2)}</text>')
    return "\n".join(out)


def box_c(x, y, w, h, title, sub="", cls="box"):
    cx = x + w / 2
    ty = y + (18 if sub else h / 2 + 4)
    out = [
        f'  <rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}"/>',
        f'  <text x="{cx}" y="{ty}" text-anchor="middle" font-size="11" font-weight="600">{_e(title)}</text>',
    ]
    if sub:
        out.append(f'  <text x="{cx}" y="{y + 33}" text-anchor="middle" font-size="9.5" class="dim">{_e(sub)}</text>')
    return "\n".join(out)


def arrow(chap, d, cls="flow"):
    return f'  <path class="{cls}" d="{d}" marker-end="url(#{_mid(chap)})"/>'


def lbl(x, y, txt, anchor="start"):
    return f'  <text class="lbl dim" x="{x}" y="{y}" text-anchor="{anchor}" font-size="9.5">{_e(txt)}</text>'


def txt(x, y, s, size=10.5, cls="", anchor="start", weight="normal"):
    c = f' class="{cls}"' if cls else ""
    w = f' font-weight="{weight}"' if weight != "normal" else ""
    return f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}"{c}{w}>{_e(s)}</text>'


# ---------------------------------------------------------------------------
# 30 bespoke chapter diagram specs:
# (chapter, anchor_section, caption_vi, caption_en, builder_fn)
# ---------------------------------------------------------------------------

def d_0_2():
    parts = [
        lbl(10, 16, "MƯỜI TIÊN ĐỀ NỀN (A1–A10) & ĐIỀU KIỆN ĐỔI THIẾT KẾ"),
        box(10, 28, 198, 52, "Vật lý & Phần cứng", "A1 Nhị phân · A4 Hỏng âm thầm", "box", "A6 CMOS · A7 Điện & tản nhiệt"),
        box(220, 28, 198, 52, "Mạng & Thời gian", "A2 Đồng hồ lệch (ms–s)", "box", "A3 Gói mất · trùng · đảo thứ tự"),
        box(430, 28, 200, 52, "Mật mã, Mã & Pháp lý", "A5 PQC · A8 Tất định (AI)", "box-warn", "A9 Conway · A10 GDPR/CRA/PDPD"),
        arrow("0.2", "M109 80 V106"),
        arrow("0.2", "M319 80 V106"),
        arrow("0.2", "M530 80 V106"),
        box(10, 110, 198, 48, "Bắt mạch: 1.4 · 1.10 · 14.1", "ECC không bắt 100%; hết điện trước rack", "box-soft"),
        box(220, 110, 198, 48, "Bắt mạch: 4.1 · 8.1 · 8.5", "Logical clock · Lease · Fencing token", "box-soft"),
        box(430, 110, 200, 48, "Bắt mạch: 12.5 · 14.10.2", "Eval harness · Hybrid X25519+ML-KEM", "box-accent"),
        txt(320, 180, "Chu kỳ rà soát: mỗi ấn bản kiểm 10 điều kiện gãy trước khi tin số benchmark", 10, "dim", "middle"),
    ]
    return svg_wrap("0.2", 640, 194, "Mười tiên đề A1 đến A10 và các điểm rà soát khi điều kiện biên đổi", "\n".join(parts))


def d_1_1():
    bars = [
        ("L1 Cache", 18, "~1 ns (1×)", "bar-accent"),
        ("L2 Cache", 36, "~4 ns", "bar-accent"),
        ("DRAM (RAM)", 92, "~100 ns (100×)", "bar-accent"),
        ("SSD NVMe", 185, "~100 µs (10⁵×)", "bar"),
        ("Cùng AZ / Region", 248, "~0.5 ms", "bar"),
        ("HDD Seek", 315, "~10 ms (10⁷×)", "bar"),
        ("Liên lục địa", 390, "~100 ms (10⁸×)", "bar"),
    ]
    parts = [lbl(10, 16, "BẬC THANG ĐỘ TRỄ (THANG LOGARIT: MỖI NẤC ≈ 10×–1000×)")]
    y = 30
    for name, w, val, bcls in bars:
        parts.append(txt(10, y + 14, name, 10.5))
        parts.append(f'  <rect class="box-soft" x="128" y="{y + 2}" width="400" height="16"/>')
        parts.append(f'  <rect class="{bcls}" x="128" y="{y + 2}" width="{w}" height="16"/>')
        parts.append(txt(536, y + 14, val, 9.8, "num"))
        y += 26
    parts.append(txt(128, y + 14, "Bẫy N+1: 100 vòng query mạng thay vì 1 batch = cộng ~50 ms thành nghẽn chính", 9.8, "dim"))
    return svg_wrap("1.1", 640, y + 26, "Bậc thang độ trễ từ L1 cache đến liên lục địa theo thang logarit", "\n".join(parts))


def d_1_2():
    parts = [
        lbl(10, 16, "BỐ CỤC DỮ LIỆU TRONG DÒNG CACHE 64 BYTE: AoS VS SoA"),
        txt(10, 42, "AoS (Array of Structs) — đọc x[i] kéo cả y,z,vy,vz vô ích:", 10.5, weight="600"),
    ]
    # Draw 64B AoS vs SoA blocks
    x = 10
    for i, field, cls in [
        ("x₀", "box-warn", "box-warn"), ("y₀", "box-soft", "box-soft"), ("z₀", "box-soft", "box-soft"),
        ("vy₀", "box-soft", "box-soft"), ("x₁", "box-warn", "box-warn"), ("y₁", "box-soft", "box-soft"),
        ("z₁", "box-soft", "box-soft"), ("vy₁", "box-soft", "box-soft"),
    ]:
        parts.append(box_c(x, 52, 76, 30, x if False else i, "", cls))
        x += 78
    parts.append(txt(10, 102, "SoA (Structure of Arrays) — 1 dòng cache 64B nuôi đủ 8–16 phần tử SIMD:", 10.5, weight="600"))
    x = 10
    for i in range(8):
        parts.append(box_c(x, 112, 76, 30, f"x[{i}]", "", "box-accent"))
        x += 78
    parts.append('  <line class="axis dashed" x1="10" y1="154" x2="634" y2="154"/>')
    parts.append(txt(320, 172, "L1 (~4 chu kỳ) → L3 (~45 chu kỳ) → DRAM (~250 chu kỳ): tuần tự hoá để compiler vector hoá", 10, "dim", "middle"))
    return svg_wrap("1.2", 640, 188, "So sánh bố cục bộ nhớ AoS lãng phí dòng cache 64B với SoA thân thiện SIMD", "\n".join(parts))


def d_1_4():
    parts = [
        lbl(10, 16, "NAND FLASH WRITE CLIFF & XÁC SUẤT URE KHI REBUILD RAID"),
        box(10, 30, 296, 130, "SSD nội tại: Write Amplification (WAF)", "Ghi 4–16 KB theo trang; Xoá theo khối (MB)", "box"),
        box_c(24, 78, 120, 36, "Ghi tuần tự", "WAF ~1.0–1.5", "box-ok"),
        box_c(164, 78, 128, 36, "Ghi ngẫu nhiên ≥80%", "GC chạy → Write Cliff", "box-warn"),
        txt(24, 144, "PLP tụ điện giữ lời hứa fsync (~10 µs)", 9.5, "dim"),
        box(326, 30, 304, 130, "RAID5 đĩa lớn vs URE (~10⁻¹⁴–10⁻¹⁵ bit)", "12 × 12 TB rebuild ≈ 132 TB đọc toàn phần", "box"),
        box_c(340, 78, 132, 36, "RAID 5 (parity đơn)", "Xác suất URE nổ cao", "box-warn"),
        box_c(484, 78, 132, 36, "RAID 10 / 3× Rep / EC", "An toàn rebuild / đọc", "box-accent"),
        txt(340, 144, "Benchmark ngắn 60s che cliff; cần fio ≥30 phút", 9.5, "dim"),
    ]
    return svg_wrap("1.4", 640, 178, "Cơ chế Write Amplification của NAND SSD và rủi ro URE khi rebuild RAID5 dung lượng TB", "\n".join(parts))


def d_1_7():
    parts = [
        lbl(10, 16, "ĐƯỜNG ỐNG BDP = BANDWIDTH × RTT (TRẦN CHO 1 KẾT NỐI)"),
        box(10, 32, 136, 48, "Bên gửi", "Window mặc định: 4 MB", "box-warn"),
        box(200, 32, 240, 48, "Sợi quang (~5 µs/km · 40 ms RTT)", "10 Gbps × 40 ms ⇒ BDP = 50 MB bay", "box-accent"),
        box(494, 32, 136, 48, "Bên nhận", "Cần RCVBUF ≥ BDP", "box"),
        arrow("1.7", "M146 56 H196"),
        arrow("1.7", "M440 56 H490"),
        box(10, 104, 300, 56, "Nếu Window < BDP (4 MB < 50 MB)", "Thông lượng tối đa = Window/RTT ≈ 100 MB/s (8% tải)", "box-warn"),
        box(330, 104, 300, 56, "Giải pháp theo thứ tự", "1) Tăng tcp_rmem/wmem  2) N streams  3) QUIC / Batch", "box-ok"),
    ]
    return svg_wrap("1.7", 640, 176, "Băng thông tích độ trễ BDP làm nghẽn kết nối khi cửa sổ TCP nhỏ hơn dung lượng đường ống", "\n".join(parts))


def d_2_1():
    parts = [
        lbl(10, 16, "KHÔNG GIAN ĐỊA CHỈ ẢO · VSZ / RSS / PSS & BẪY COPY-ON-WRITE"),
        box(10, 30, 190, 92, "VSZ (ảo hoàn toàn)", "Mọi mmap + thư viện chưa chạm", "box-soft", "Không đo lượng RAM thật"),
        box(216, 30, 196, 92, "RSS (đếm kép shared)", "Cộng đủ lib .so cho từng pod", "box-warn", "10 pod dùng chung lib → phồng ảo"),
        box(428, 30, 202, 92, "PSS (thước đúng để sizing)", "Shared RAM ÷ số process giữ", "box-accent", "Tổng PSS = RAM vật lý thật"),
        arrow("2.1", "M200 76 H212"),
        arrow("2.1", "M412 76 H424"),
        box(10, 140, 620, 48, "Cảnh báo fork() + Copy-on-Write (vd Redis BGSAVE)", "Cha ghi vào heap lúc con đang chạy → nhân đôi trang vật lý → chạm cgroup limit → OOM Killer", "box-warn"),
    ]
    return svg_wrap("2.1", 640, 200, "Phân biệt VSZ RSS PSS trong bộ nhớ ảo và bẫy Copy-on-Write khi fork tiến trình lớn", "\n".join(parts))


def d_2_3():
    parts = [
        lbl(10, 16, "CGROUP v2 CPU QUOTA 500m (50 ms MỖI CHU KỲ 100 ms) GÂY VỌT p99"),
        '  <line class="axis" x1="30" y1="128" x2="610" y2="128"/>',
        '  <line class="axis" x1="30" y1="36" x2="30" y2="128"/>',
        '  <rect class="area-ok" x="30" y="54" width="140" height="74"/>',
        '  <rect class="area-warn" x="170" y="54" width="140" height="74"/>',
        '  <rect class="area-ok" x="310" y="54" width="140" height="74"/>',
        '  <rect class="area-warn" x="450" y="54" width="140" height="74"/>',
        txt(100, 92, "0–50 ms: Chạy", 10.5, anchor="middle", weight="600"),
        txt(240, 86, "50–100 ms:", 10.5, anchor="middle", weight="600"),
        txt(240, 102, "BỊ THROTTLE", 10, "dim", "middle"),
        txt(380, 92, "100–150 ms: Chạy", 10.5, anchor="middle", weight="600"),
        txt(520, 86, "150–200 ms:", 10.5, anchor="middle", weight="600"),
        txt(520, 102, "BỊ THROTTLE", 10, "dim", "middle"),
        '  <line class="dashed axis" x1="310" y1="36" x2="310" y2="138"/>',
        txt(170, 148, "1 chu kỳ CFS = 100 ms · Request tới lúc ms 51 chờ đứng ~49 ms dù CPU trung bình thấp", 9.8, "dim", "middle"),
        txt(490, 44, "PSI / nr_throttled báo nghẽn", 9.5, "dim", "middle"),
    ]
    return svg_wrap("2.3", 640, 168, "Cơ chế cgroup CPU quota 500m gây throttle 50ms mỗi chu kỳ 100ms làm p99 nhảy bậc", "\n".join(parts))


def d_2_4():
    parts = [
        lbl(10, 16, "CHECKLIST 4 BƯỚC GHI BỀN CHỐNG MẤT KHI CÚP ĐIỆN (PAGE CACHE VS FSYNC)"),
        box_c(10, 32, 134, 48, "1. Ghi tệp tạm", "write(file.tmp)", "box"),
        box_c(168, 32, 136, 48, "2. Ép dữ liệu", "fsync(tmp) → đĩa", "box-accent"),
        box_c(328, 32, 138, 48, "3. Đổi tên nguyên tử", "rename(tmp → chính)", "box"),
        box_c(490, 32, 140, 48, "4. Ép thư mục (dễ quên)", "fsync(dir) metadata", "box-warn"),
        arrow("2.4", "M144 56 H164"),
        arrow("2.4", "M304 56 H324"),
        arrow("2.4", "M466 56 H486"),
        box(10, 104, 300, 46, "Buffered I/O (mặc định app)", "Qua Page Cache RAM · Writeback theo vm.dirty_*", "box-soft"),
        box(330, 104, 300, 46, "O_DIRECT (Database tự quản buffer)", "Bỏ double-cache · Bắt buộc alignment 512B/4KB", "box-soft"),
    ]
    return svg_wrap("2.4", 640, 166, "Quy trình 4 bước ghi tệp an toàn qua cúp điện và so sánh Buffered I/O với O_DIRECT", "\n".join(parts))


def d_3_1():
    parts = [
        lbl(10, 16, "ĐƯỜNG CONG HÀNG ĐỢI M/M/1: ĐỘ TRỄ TĂNG PHI TUYẾN KHI TẢI > 80%"),
        '  <line class="axis" x1="48" y1="146" x2="368" y2="146"/>',
        '  <line class="axis" x1="48" y1="30" x2="48" y2="146"/>',
        '  <line class="dashed axis" x1="280" y1="30" x2="280" y2="146"/>',
        '  <path class="area-warn" d="M280,146 L280,104 Q324,84 352,32 L368,32 L368,146 Z"/>',
        '  <path class="curve-accent" d="M52,140 C150,137 230,130 280,104 C318,84 338,54 354,32"/>',
        txt(42, 144, "W", 10, "num", "end"),
        txt(280, 162, "ρ = 80% (biên)", 9.5, "num", "middle"),
        txt(354, 162, "95%", 9.5, "num", "middle"),
        box(390, 30, 240, 38, "Little's Law: L = λ × W", "Cần biết 2 để sizing đúng 1", "box-accent"),
        box(390, 76, 240, 38, "Amdahl: 1 / (s + (1−s)/n)", "Phần tuần tự s ghim trần lõi", "box"),
        box(390, 122, 240, 38, "Backpressure từ chối sớm", "Tránh hàng đợi vô hạn nổ RAM", "box-warn"),
    ]
    return svg_wrap("3.1", 640, 174, "Đường congUtilization-Latency với ngưỡng gối 80 phần trăm cùng định luật Little và Amdahl", "\n".join(parts))


def d_3_10():
    parts = [
        lbl(10, 16, "CHÍN TRẠM TRÊN MỘT REQUEST & CHIA NGÂN SÁCH TIMEOUT (CON < CHA)"),
        box_c(10, 32, 114, 42, "1. DNS / LB", "budget: 20 ms", "box"),
        box_c(136, 32, 114, 42, "2. Ingress TLS", "budget: 40 ms", "box"),
        box_c(262, 32, 114, 42, "3. App Pool", "L = λ × W", "box-accent"),
        box_c(388, 32, 114, 42, "4. Codec/Parse", "orjson vs std", "box"),
        box_c(514, 32, 116, 42, "5. Client Pool", "downstream", "box"),
        arrow("3.10", "M124 53 H132"),
        arrow("3.10", "M250 53 H258"),
        arrow("3.10", "M376 53 H384"),
        arrow("3.10", "M502 53 H510"),
        arrow("3.10", "M572 74 V92 H572"),
        box_c(514, 96, 116, 42, "6. DB Pool", "cạn trước DB", "box-warn"),
        box_c(350, 96, 140, 42, "7. DB / Cache Engine", "deadline còn 120 ms", "box-accent"),
        box_c(184, 96, 144, 42, "8. Response Path", "stream / gzip", "box"),
        box_c(10, 96, 152, 42, "9. Telemetry Async", "không chặn đường nóng", "box-soft"),
        arrow("3.10", "M514 117 H494"),
        arrow("3.10", "M350 117 H332"),
        arrow("3.10", "M184 117 H166"),
        txt(320, 160, "Chữa nhanh trạm 3 mà bỏ quên trạm 6 = dời điểm nghẽn thẳng xuống pool DB", 9.8, "dim", "middle"),
    ]
    return svg_wrap("3.10", 640, 174, "Chín trạm từ DNS/LB tới DB và Async Log với phân bổ timeout budget và kích thước pool", "\n".join(parts))


def d_4_1():
    parts = [
        lbl(10, 16, "SO SÁNH BẮT TAY & ĐỨT GÃY: TCP+TLS1.2 · TLS1.3 · QUIC/HTTP3"),
        box(10, 30, 196, 118, "TCP + TLS 1.2", "2–3 RTT trước byte dữ liệu", "box"),
        txt(20, 82, "• Đổi WiFi → 4G = đứt hẳn", 9.8),
        txt(20, 98, "• Mất 1 gói = treo mọi stream", 9.8),
        txt(20, 114, "• Tốt nội cụm dùng H2 + offload", 9.8, "dim"),
        box(222, 30, 196, 118, "TLS 1.3 (RFC 8446)", "1-RTT (0-RTT chỉ idempotent)", "box-soft"),
        txt(232, 82, "• Bỏ cipher yếu, 0-RTT replay", 9.8),
        txt(232, 98, "• Chỉ GET / query dùng 0-RTT", 9.8),
        txt(232, 114, "• Không bao giờ cho POST tiền", 9.8, "dim"),
        box(434, 30, 196, 118, "QUIC / HTTP3 (UDP)", "Handshake + crypto gộp 1 RTT", "box-accent"),
        txt(444, 82, "• Stream độc lập (hết HoL)", 9.8),
        txt(444, 98, "• Connection ID sống qua IP", 9.8),
        txt(444, 114, "• Đặt edge cho mobile user", 9.8, "dim"),
    ]
    return svg_wrap("4.1", 640, 164, "So sánh TCP+TLS1.2 với TLS1.3 và QUIC HTTP/3 về số RTT và giữ kết nối khi đổi mạng", "\n".join(parts))


def d_5_2():
    parts = [
        lbl(10, 16, "RDBMS POOL EXHAUSTION & ĐÁNH ĐỔI ISOLATION LEVEL (POSTGRES / MYSQL)"),
        box_c(10, 32, 128, 46, "App Instances", "hàng trăm goroutine", "box"),
        box_c(168, 32, 152, 46, "PgBouncer / Pool", "transaction-mode", "box-accent"),
        box_c(350, 32, 134, 46, "DB Backend Worker", "số ≈ lõi CPU × 2", "box-ok"),
        box_c(510, 32, 120, 46, "WAL + fsync", "NVMe PLP", "box"),
        arrow("5.2", "M138 55 H164"),
        arrow("5.2", "M320 55 H346"),
        arrow("5.2", "M484 55 H506"),
        box(10, 98, 200, 56, "READ COMMITTED", "Đọc bản commit mới nhất · Nền web", "box-soft"),
        box(220, 98, 200, 56, "REPEATABLE READ", "Snapshot · PG skip, MySQL gap lock", "box-soft"),
        box(430, 98, 200, 56, "SERIALIZABLE (SSI)", "Tiền/kho · App bắt lỗi 40001 retry", "box-warn"),
    ]
    return svg_wrap("5.2", 640, 168, "Kiến trúc connection pool trước RDBMS và ba mức isolation từ Read Committed tới Serializable", "\n".join(parts))


def d_5_7():
    parts = [
        lbl(10, 16, "QUEUE (XÓA SAU ACK) VS APPEND-ONLY LOG (REPLAY THEO PARTITION)"),
        box(10, 30, 298, 124, "Queue Truyền thống (vd RabbitMQ)", "Đẩy tới worker → xong là XOÁ", "box"),
        box_c(24, 78, 122, 34, "Routing phức tạp", "priority / topic", "box-soft"),
        box_c(164, 78, 130, 34, "Poison Message", "→ DLQ + đếm retry", "box-warn"),
        txt(24, 138, "Không giữ lịch sử để nhiều service tự đọc lại", 9.5, "dim"),
        box(324, 30, 306, 124, "Distributed Log (Kafka / KRaft)", "Ghi nối đuôi · Giữ retention theo ngày/S3", "box-accent"),
        box_c(338, 78, 134, 34, "hash(key) % N", "Thứ tự trong Partition", "box-ok"),
        box_c(484, 78, 132, 34, "Nhóm A & Nhóm B", "Đọc cùng log, riêng offset", "box-soft"),
        txt(338, 138, "Dùng salt/tách topic khi gặp hot partition", 9.5, "dim"),
    ]
    return svg_wrap("5.7", 640, 168, "So sánh Queue xóa sau xử lý và Distributed Log giữ offset replay nhiều consumer group", "\n".join(parts))


def d_5_12():
    parts = [
        lbl(10, 16, "EVENT TIME VS PROCESSING TIME · WATERMARK & TRẠNG THÁI FLINK"),
        '  <line class="axis" x1="48" y1="146" x2="352" y2="146"/>',
        '  <line class="axis" x1="48" y1="30" x2="48" y2="146"/>',
        '  <line class="dashed axis" x1="48" y1="146" x2="340" y2="42"/>',
        '  <line class="curve-accent" x1="48" y1="132" x2="340" y2="62"/>',
        '  <circle class="node" cx="140" cy="108" r="3.5"/>',
        '  <circle class="node-accent" cx="230" cy="96" r="3.5"/>',
        '  <circle class="node-open" cx="282" cy="112" r="4"/>',
        txt(292, 116, "Đến muộn → Side output", 9.5),
        txt(200, 162, "Event Time (trên thiết bị)", 9.8, "dim", "middle"),
        txt(18, 90, "Proc", 9.5, "dim"),
        box(374, 32, 256, 38, "Watermark: đã đủ dữ liệu ≤ t", "Đóng cửa sổ trước khi chốt kết quả", "box-accent"),
        box(374, 80, 256, 38, "RocksDB State + Checkpoint", "Crash → hồi state + offset nguồn", "box-ok"),
        box(374, 128, 256, 32, "Batch khi cần chờ ≥ phút (rẻ 10×)", "", "box-soft"),
    ]
    return svg_wrap("5.12", 640, 174, "Biểu đồ Event Time và Processing Time với đường Watermark xử lý sự kiện đến trễ", "\n".join(parts))


def d_5_14():
    parts = [
        lbl(10, 16, "BA MÔ HÌNH ĐA THUÊ BAO (MULTI-TENANCY): POOL · BRIDGE · SILO"),
        box(10, 30, 198, 92, "1. Pool (Shared + RLS)", "1 Schema · cột tenant_id", "box-accent", "80% tenant nhỏ · rẻ nhất"),
        box(220, 30, 198, 92, "2. Bridge (Schema/Tenant)", "1 Cụm · tối đa vài nghìn schema", "box", "Cô lập tầm trung"),
        box(430, 30, 200, 92, "3. Silo (DB riêng/Tenant)", "Hạ tầng tách hẳn · compliance", "box-ok", "Enterprise, không ồn chéo"),
        arrow("5.14", "M208 76 H216"),
        arrow("5.14", "M418 76 H426"),
        box(10, 138, 620, 44, "Bất biến sống còn: Index đặt (tenant_id, ...) đầu tiên & RLS policy ở DB (không dùng superuser)", "Tránh tenant A quét dữ liệu tenant B và ngăn lỗi WHERE bị quên ở code ứng dụng", "box-warn"),
    ]
    return svg_wrap("5.14", 640, 194, "Lộ trình từ Pool Shared RLS lên Bridge và Silo cùng ràng buộc composite index tenant_id", "\n".join(parts))


def d_6_5():
    parts = [
        lbl(10, 16, "BỐN TẦNG LƯU WEB & HỢP ĐỒNG CACHE-CONTROL"),
        box_c(10, 32, 124, 46, "Browser Cache", "private · max-age", "box"),
        box_c(162, 32, 136, 46, "CDN Edge PoP", "public · s-maxage", "box-accent"),
        box_c(326, 32, 144, 46, "Origin Shield", "gom cache miss (SW)", "box-ok"),
        box_c(498, 32, 132, 46, "Origin App/DB", "nguồn chân lý", "box"),
        arrow("6.5", "M134 55 H158"),
        arrow("6.5", "M298 55 H322"),
        arrow("6.5", "M470 55 H494"),
        box(10, 98, 302, 54, "stale-while-revalidate=60", "Trả ngay bản cũ cho khách; CDN cập nhật nền", "box-soft"),
        box(328, 98, 302, 54, "Bẫy Vary & Stampede", "Thiếu Vary = lộ nhầm · Vary Cookie = 0% hit", "box-warn"),
    ]
    return svg_wrap("6.5", 640, 168, "Luồng 4 tầng cache từ Browser tới Origin qua CDN PoP và Origin Shield", "\n".join(parts))


def d_8_2():
    parts = [
        lbl(10, 16, "RAFT TERM · LEASE HẾT HẠN & FENCING TOKEN CHỐNG ZOMBIE LEADER"),
        box_c(10, 30, 180, 40, "Node A (Leader cũ, GC pause)", "giữ Fencing Token = 33", "box-warn"),
        box_c(230, 30, 180, 40, "Node B (Leader mới, Term N+1)", "cấp Token = 34 (Quorum)", "box-accent"),
        box_c(450, 30, 180, 40, "Storage / Resource", "chỉ nhận token ≥ max_seen", "box-ok"),
        arrow("8.2", "M320 70 V102 H446"),
        txt(385, 96, "Ghi token=34 (OK)", 9.5, anchor="middle"),
        arrow("8.2", "M100 70 V126 H446"),
        txt(275, 120, "Tỉnh dậy gửi ghi muộn token=33 → BỊ TỪ CHỐI!", 9.5, "dim", "middle"),
        txt(320, 154, "Consensus = đa số N/2+1 (mất ≥(N+1)/2 là dừng ghi hoàn toàn) · Election timeout ≥ ~10× RTT", 9.8, "dim", "middle"),
    ]
    return svg_wrap("8.2", 640, 168, "Fencing token tăng đơn điệu chặn leader cũ tỉnh lại sau GC pause ghi đè dữ liệu", "\n".join(parts))


def d_8_3():
    parts = [
        lbl(10, 16, "TRANSACTIONAL OUTBOX + SAGA COMPENSATION (THAY THẾ 2PC)"),
        box(10, 32, 188, 52, "1. Giao dịch DB cục bộ", "INSERT order + outbox", "box-accent", "1 transaction → không đứt đôi"),
        box(226, 32, 188, 52, "2. Relay / Debezium CDC", "Đọc outbox → gửi Kafka", "box", "At-least-once an toàn"),
        box(442, 32, 188, 52, "3. Idempotent Consumer", "Khử trùng theo event_id", "box-ok", "= Hiệu ứng Exactly-Once"),
        arrow("8.3", "M198 58 H222"),
        arrow("8.3", "M414 58 H438"),
        box_c(10, 108, 138, 42, "Bước S1: Đặt chỗ", "OK", "box-soft"),
        box_c(174, 108, 138, 42, "Bước S2: Trừ kho", "OK", "box-soft"),
        box_c(338, 108, 138, 42, "Bước S3: Thu tiền", "FAIL → kích hoàn", "box-warn"),
        box_c(502, 108, 128, 42, "Phản đề S2⁻¹·S1⁻¹", "Cộng trả kho · Huỷ", "box-ok"),
        arrow("8.3", "M148 129 H170"),
        arrow("8.3", "M312 129 H334"),
        arrow("8.3", "M476 129 H498"),
    ]
    return svg_wrap("8.3", 640, 166, "Mẫu Transactional Outbox và chuỗi Saga kèm phản đề compensation khi một bước thất bại", "\n".join(parts))


def d_8_4():
    parts = [
        lbl(10, 16, "CONSISTENT HASHING RING & QUORUM ĐỌC-GHI (W + R > N)"),
        '  <circle class="axis" cx="110" cy="98" r="56"/>',
        '  <circle class="node-accent" cx="110" cy="42" r="5"/>',
        '  <circle class="node" cx="164" cy="112" r="5"/>',
        '  <circle class="node" cx="56" cy="112" r="5"/>',
        txt(110, 32, "vnode A", 9.2, "dim", "middle"),
        txt(182, 116, "B", 9.2, "dim"),
        txt(40, 116, "C", 9.2, "dim", "end"),
        txt(110, 102, "Di dời ~1/N", 9.5, anchor="middle"),
        box(226, 32, 190, 52, "Chọn Shard Key theo truy vấn", "Đi thẳng 1 shard = nhanh", "box-accent", "Tránh scatter-gather cả cụm"),
        box(430, 32, 200, 52, "Quorum: W + R > N", "Vd N=3, W=2, R=2 → giao nhau ≥1", "box-ok", "Đọc thấy bản ghi mới nhất"),
        box(226, 98, 404, 52, "Replica Lag & Resharding", "Async replication → RPO > 0 · Reshard nóng bằng dual-write + backfill hoặc CDC", "box-soft"),
    ]
    return svg_wrap("8.4", 640, 168, "Vòng consistent hashing và công thức quorum W + R > N chống đọc dữ liệu cũ", "\n".join(parts))


def d_8_5():
    parts = [
        lbl(10, 16, "BỐN TẦNG CHỊU LỖI CẦN ĐỦ (THIẾU MỘT LÀ SẬP LAN TRUYỀN)"),
        box_c(10, 34, 138, 52, "1. Load Shedding", "Trả 503 sớm giữ lõi", "box-warn"),
        box_c(170, 34, 138, 52, "2. Bulkhead", "Pool riêng từng nhóm", "box-accent"),
        box_c(330, 34, 138, 52, "3. Circuit Breaker", "CLOSED ↔ OPEN ↔ HALF", "box"),
        box_c(490, 34, 140, 52, "4. Retry + Full Jitter", "Budget ≤ 10% traffic", "box-ok"),
        arrow("8.5", "M148 60 H166"),
        arrow("8.5", "M308 60 H326"),
        arrow("8.5", "M468 60 H486"),
        box(10, 108, 620, 44, "Nguyên lý chống bão: Retry không jitter = nhân tải lên đúng lúc dependency hấp hối", "Luôn cấp fallback thật khi Circuit Breaker chuyển OPEN và đặt timeout con < cha", "box-soft"),
    ]
    return svg_wrap("8.5", 640, 166, "Chuỗi phòng thủ 4 lớp: Load Shedding, Bulkhead, Circuit Breaker và Retry kèm Jitter", "\n".join(parts))


def d_8_7():
    parts = [
        lbl(10, 16, "BẬC THANG ĐA VÙNG (RTO · RPO) & CÔ LẬP CELL-BASED"),
        box(10, 32, 144, 56, "1. Một vùng", "RTO: dựng lại từ đầu", "box-soft"),
        box(168, 32, 144, 56, "2. Backup chéo vùng", "RTO giờ · RPO chu kỳ", "box"),
        box(326, 32, 144, 56, "3. Active-Passive", "Standby · RPO giây/phút", "box-accent"),
        box(484, 32, 146, 56, "4. Active-Active", "RTO ≈ 0 · Phải giải xung đột", "box-warn"),
        arrow("8.7", "M154 60 H164"),
        arrow("8.7", "M312 60 H322"),
        arrow("8.7", "M470 60 H480"),
        box(10, 108, 298, 48, "Cell-Based Isolation", "C khách vào C cell → 1 lỗi khoanh tối đa 1/C user", "box-ok"),
        box(326, 108, 304, 48, "Hợp đồng DR không có drill = giả định", "DNS TTL · RHO % công suất standby sau failover", "box-soft"),
    ]
    return svg_wrap("8.7", 640, 170, "Bốn cấp độ sẵn sàng đa vùng cùng kiến trúc Cell cô lập blast radius", "\n".join(parts))


def d_9_1():
    parts = [
        lbl(10, 16, "KUBERNETES RECONCILE LOOP · VÒNG ĐỜI PROBE & DRAIN CÓ PDB"),
        box(10, 30, 176, 54, "kube-apiserver", "Cổng đọc/ghi + watch duy nhất", "box-accent"),
        box(214, 30, 196, 54, "etcd (Raft Quorum)", "Lưu trạng thái khai báo thật", "box"),
        box(438, 30, 192, 54, "Scheduler + Controllers", "So Spec vs Thực → Reconcile", "box"),
        arrow("9.1", "M186 57 H210"),
        arrow("9.1", "M410 57 H434"),
        box_c(10, 104, 140, 44, "startupProbe", "Chờ app khởi động", "box-soft"),
        box_c(170, 104, 142, 44, "readinessProbe", "Mới vào Endpoints LB", "box-accent"),
        box_c(332, 104, 140, 44, "livenessProbe", "Kẹt thì restart container", "box-warn"),
        box_c(492, 104, 138, 44, "preStop + PDB", "Drain graceful không rớt", "box-ok"),
        arrow("9.1", "M150 126 H166"),
        arrow("9.1", "M312 126 H328"),
        arrow("9.1", "M472 126 H488"),
    ]
    return svg_wrap("9.1", 640, 164, "Control plane Kubernetes theo vòng reconcile cùng chuỗi Startup, Readiness, Liveness và PDB", "\n".join(parts))


def d_9_7():
    parts = [
        lbl(10, 16, "ARTIFACT BẤT BIẾN THEO DIGEST & PROGRESSIVE CANARY CÓ PHANH"),
        box_c(10, 34, 136, 48, "1. Hermetic Build", "Artifact @sha256:...", "box-accent"),
        box_c(166, 34, 126, 48, "2. Canary 1% → 5%", "Đo SLO tự động", "box"),
        box_c(312, 34, 146, 48, "3. Canary 25% → 100%", "Giữ xanh các DORA KPI", "box-ok"),
        box_c(478, 34, 152, 48, "Auto-Rollback", "Lỗi vượt ngưỡng → lùi tức thì", "box-warn"),
        arrow("9.7", "M146 58 H162"),
        arrow("9.7", "M292 58 H308"),
        arrow("9.7", "M458 58 H474"),
        box(10, 106, 620, 44, "Trunk-based + Feature Flag ngắn hạn + SBOM", "Cấm build lại per-environment: bản lên prod chính là bản vừa vượt qua kiểm định", "box-soft"),
    ]
    return svg_wrap("9.7", 640, 164, "Chuỗi phát hành an toàn bằng artifact SHA-256 duy nhất đi qua các bậc canary có auto-rollback", "\n".join(parts))


def d_10_3():
    parts = [
        lbl(10, 16, "OAUTH 2.1 + PASSKEY & QUYẾT ĐỊNH THU HỒI SESSION VS JWT NGẮN HẠN"),
        box(10, 30, 198, 56, "AuthN: OAuth 2.1 + PKCE", "Passkey/WebAuthn chống phishing", "box-accent"),
        box(224, 30, 200, 56, "Access Token (JWT ~5 phút)", "Stateless xác thực nhanh", "box"),
        box(440, 30, 190, 56, "Refresh Store (Thu hồi tức thì)", "Xoá store/SCIM = đá ngay (I-064)", "box-warn"),
        arrow("10.3", "M208 58 H220"),
        arrow("10.3", "M424 58 H436"),
        box(10, 106, 198, 46, "RBAC (theo vai)", "Đơn giản, hợp tổ chức gọn", "box-soft"),
        box(224, 106, 200, 46, "ABAC (theo thuộc tính)", "Ngữ cảnh phòng ban, IP, thời gian", "box-soft"),
        box(440, 106, 190, 46, "ReBAC (đồ thị quan hệ)", "Ai là chủ/thành viên tài nguyên nào", "box-ok"),
    ]
    return svg_wrap("10.3", 640, 166, "Chuỗi AuthN OAuth 2.1 và token thu hồi được kết hợp ba mô hình AuthZ RBAC ABAC ReBAC", "\n".join(parts))


def d_11_1():
    parts = [
        lbl(10, 16, "CHUỖI SLI → SLO → SLA & ERROR BUDGET MULTI-WINDOW BURN ALERT"),
        box_c(10, 32, 138, 48, "SLI (Trải nghiệm)", "% req < 300ms (ko CPU)", "box"),
        box_c(168, 32, 144, 48, "SLO (Mục tiêu nội)", "Vd 99.9% ⇒ 43.8′/tháng", "box-accent"),
        box_c(332, 32, 142, 48, "SLA (Hợp đồng ngoài)", "99.5% (luôn lỏng hơn SLO)", "box-soft"),
        box_c(494, 32, 136, 48, "Error Budget", "Hết → đóng băng release", "box-warn"),
        arrow("11.1", "M148 56 H164"),
        arrow("11.1", "M312 56 H328"),
        arrow("11.1", "M474 56 H490"),
        box(10, 102, 302, 48, "Fast Burn Alert (1h = 14.4× · 5′ kiểm)", "Page on-call ngay khi đốt 2% budget/giờ", "box-warn"),
        box(328, 102, 302, 48, "Slow Burn (6h = 6×) · Ticket/giờ làm việc", "Loại nhiễu ban đêm của ngưỡng tĩnh cũ", "box-ok"),
    ]
    return svg_wrap("11.1", 640, 164, "Chuỗi SLI SLO SLA cùng hợp đồng Error Budget và cảnh báo burn-rate đa cửa sổ", "\n".join(parts))


def d_11_5():
    parts = [
        lbl(10, 16, "VÒNG QUẢN TRỊ FINOPS & CHI PHÍ ẨN KIẾN TRÚC"),
        box_c(10, 32, 142, 48, "1. Tag & Unit Cost", "$ / 1k req hay $/đơn", "box-accent"),
        box_c(172, 32, 142, 48, "2. Bắt khoản ẩn", "Egress · NAT · Cross-AZ", "box-warn"),
        box_c(334, 32, 142, 48, "3. Mua đúng loại", "RI/SP nền + Spot batch", "box-ok"),
        box_c(496, 32, 134, 48, "4. Showback Team", "Tiền = phản hồi kỹ thuật", "box"),
        arrow("11.5", "M152 56 H168"),
        arrow("11.5", "M314 56 H330"),
        arrow("11.5", "M476 56 H492"),
        box(10, 102, 620, 44, "Không tag = không đo được · Tiết kiệm nhất là tắt idle và đặt dữ liệu gần compute (bỏ NAT/Egress)", "", "box-soft"),
    ]
    return svg_wrap("11.5", 640, 160, "Vòng phản hồi FinOps gắn unit economics và các khoản ẩn egress NAT cross-region", "\n".join(parts))


def d_12_2():
    parts = [
        lbl(10, 16, "HAI PHA ĐỐI NGHỊCH CỦA LLM INFERENCE SERVING & PAGED KV-CACHE"),
        box(10, 32, 200, 74, "Pha PREFILL (đọc prompt)", "Compute-bound (FLOPs)", "box-accent", "Quyết định TTFT (chữ đầu tiên)"),
        box(224, 32, 206, 74, "Pha DECODE (sinh từng token)", "HBM Bandwidth-bound", "box-warn", "Quyết định ITL / TPOT (tốc độ tuôn)"),
        box(444, 32, 186, 74, "PagedAttention + Prefix", "Chia trang KV-cache (ko phân mảnh)", "box-ok", "System prompt đặt ĐẦU"),
        box(10, 124, 302, 48, "Continuous Batching vs Disaggregation", "Gom liên tục tăng throughput; cụm lớn tách P/D riêng GPU", "box-soft"),
        box(328, 124, 302, 48, "Quantization: BF16 → FP8 → INT4", "Cắt đôi bytes đọc mỗi bước decode · Luôn đo eval riêng", "box-soft"),
    ]
    return svg_wrap("12.2", 640, 186, "Hai pha Prefill compute-bound và Decode memory-bound cùng PagedAttention trong LLM serving", "\n".join(parts))


def d_12_5():
    parts = [
        lbl(10, 16, "CỔNG EVAL CI/CD (D-130) & BA LỚP GUARDRAILS QUANH LLM"),
        box_c(10, 32, 134, 48, "1. Input Wall", "PII redact · Injection", "box-warn"),
        box_c(168, 32, 140, 48, "2. Process Wall", "Tool schema · Allowlist", "box-accent"),
        box_c(332, 32, 136, 48, "3. Output Wall", "Schema · Grounding check", "box-ok"),
        box_c(492, 32, 138, 48, "4. gen_ai Telemetry", "Trace + token + eval/PR", "box"),
        arrow("12.5", "M144 56 H164"),
        arrow("12.5", "M308 56 H328"),
        arrow("12.5", "M468 56 H488"),
        box(10, 102, 620, 46, "Golden Set (50–500 ca mỗi PR) + LLM-Judge chấm mù hai chiều đã đối chuẩn với nhãn người", "Chữa bias thiên vị câu dài/giọng quen trước khi chặn merge tự động", "box-soft"),
    ]
    return svg_wrap("12.5", 640, 162, "Kiến trúc Guardrails 3 lớp bảo vệ Input Process Output kèm cổng Eval golden set trên từng PR", "\n".join(parts))


def d_13_1():
    parts = [
        lbl(10, 16, "PLAYBOOK OLTP SỔ CÁI KÉP (DOUBLE-ENTRY) & IDEMPOTENCY TOÀN TRÌNH (D-134)"),
        box_c(10, 32, 140, 48, "Client + Gateway", "Idempotency-Key header", "box"),
        box_c(172, 32, 138, 48, "Order Saga", "Gắn order_id xuyên suốt", "box-accent"),
        box_c(332, 32, 146, 48, "Ledger ACID (PG)", "Nợ + Có = 0 (append-only)", "box-ok"),
        box_c(500, 32, 130, 48, "Payment Adapter", "Webhook + Retry an toàn", "box"),
        arrow("13.1", "M150 56 H168"),
        arrow("13.1", "M310 56 H328"),
        arrow("13.1", "M478 56 H496"),
        box(10, 102, 620, 44, "Đối soát (Reconciliation) 3 chiều hằng đêm: Sổ nội bộ ⇄ Provider ⇄ Sao kê Ngân hàng", "Truy vấn SQL SUM(amount) = 0 phát hiện mọi lệch kế toán ngay cuối ngày", "box-soft"),
    ]
    return svg_wrap("13.1", 640, 160, "Kiến trúc OLTP thanh toán với Idempotency toàn trình sổ cái kép SUM bằng 0 và đối soát ba nguồn", "\n".join(parts))


def d_14_10_2():
    parts = [
        lbl(10, 16, "CHUYỂN DỊCH HẬU LƯỢNG TỬ (PQC FIPS 203/204/205) & BẪY HARVEST-NOW"),
        box(10, 32, 298, 60, "Harvest Now, Decrypt Later (HNDL)", "Thời hạn bí mật (10–20y) + Thời gian di dời", "box-warn", "Nếu > Q-day ⇒ phải bắt đầu chuyển NGAY hôm nay"),
        box(326, 32, 304, 60, "Hybrid Bước Chuyển An Toàn", "Trao khoá: X25519 + ML-KEM (FIPS 203)", "box-accent", "Chữ ký: ML-DSA (204) / SLH-DSA (205) · AES-256 giữ"),
        box(10, 110, 298, 52, "Chi phí kích thước chữ ký (KB vs 64B)", "Ảnh hưởng packet TLS handshake, cert chain & IoT", "box-soft"),
        box(326, 110, 304, 52, "Constant-Time + Crypto-Agility", "Không nhánh/index/log theo secret; đổi chuẩn qua cấu hình", "box-ok"),
    ]
    return svg_wrap("14.10.2", 640, 176, "Lộ trình di chuyển PQC hybrid FIPS 203/204/205 đối phó Harvest-Now-Decrypt-Later và yêu cầu constant-time", "\n".join(parts))


SPECS = [
    ("0.2", "2", "Mười tiên đề A1–A10, điểm rà soát theo mảng kỹ thuật và điều kiện đổi thiết kế.", "The 10 foundational axioms (A1–A10), verification domains, and assumption-break triggers.", d_0_2),
    ("1.1", "2", "Bậc thang độ trễ từ thanh ghi/L1 (~1 ns) tới liên lục địa (~100 ms) trên thang logarit.", "Latency hierarchy from L1 cache (~1 ns) to cross-continent (~100 ms) on a log scale.", d_1_1),
    ("1.2", "2", "Bố cục AoS kéo byte vô ích trên dòng cache 64B so với SoA nén phẳng cho SIMD.", "AoS striding unused fields per 64B cache line versus SoA contiguous packing for SIMD.", d_1_2),
    ("1.4", "2", "NAND Write Cliff trên SSD đầy 80% và xác suất lỗi URE khi rebuild RAID5 dung lượng TB.", "SSD NAND GC write cliff above 80% fill and TB-scale RAID5 URE rebuild failure risk.", d_1_4),
    ("1.7", "2", "Công thức BDP = Bandwidth × RTT và ngưỡng cửa sổ TCP tránh tự nghẽn đường ống trống.", "Bandwidth-Delay Product pipe capacity versus undersized TCP receive windows.", d_1_7),
    ("2.1", "2", "Phân biệt VSZ, RSS, PSS và hiện tượng nhân đôi RAM do Copy-on-Write sau fork().", "Distinguishing VSZ, RSS, PSS memory accounting and fork() Copy-on-Write spikes.", d_2_1),
    ("2.3", "2", "Cơ chế cgroup v2 CPU quota 500m (50 ms chạy / 50 ms chờ mỗi 100 ms) làm vọt đuôi p99.", "cgroup v2 500m quota halting execution for 50 ms inside each 100 ms CFS period.", d_2_3),
    ("2.4", "2", "Checklist 4 bước ghi tệp an toàn qua mất điện và đánh đổi giữa Page Cache với O_DIRECT.", "4-step crash-safe atomic write sequence and Buffered I/O versus O_DIRECT tradeoffs.", d_2_4),
    ("3.1", "2", "Đường cong Utilization–Latency M/M/1 gãy dốc từ 80% kèm định luật Little và Amdahl.", "M/M/1 queueing knee past 80% utilization alongside Little's and Amdahl's laws.", d_3_1),
    ("3.10", "2", "9 trạm xử lý request, tính kích thước pool theo Little và chia timeout budget con < cha.", "Nine request stations bounded by Little's Law pool sizing and nested timeout budgets.", d_3_10),
    ("4.1", "2", "So sánh RTT bắt tay và giữ kết nối khi đổi mạng giữa TCP+TLS1.2, TLS1.3 và QUIC.", "Handshake RTTs and WiFi-to-LTE migration across TCP+TLS1.2, TLS1.3, and QUIC/HTTP3.", d_4_1),
    ("5.2", "2", "Transaction pooling trước worker RDBMS và bảng đánh đổi 3 mức isolation level.", "Connection pooling ahead of fixed RDBMS workers and isolation anomaly tradeoffs.", d_5_2),
    ("5.7", "2", "Phân biệt Queue truyền thống xóa sau ack với Distributed Log hỗ trợ replay theo partition.", "Ephemeral consumer queues compared with offset-replayable partitioned event logs.", d_5_7),
    ("5.12", "2", "Độ lệch Event Time / Processing Time, mốc Watermark và state checkpoint trong Flink.", "Event-time vs processing-time skew, watermarks, side outputs, and RocksDB checkpoints.", d_5_12),
    ("5.14", "2", "Lộ trình đa thuê bao Pool (RLS) → Bridge → Silo và bất biến composite index tenant_id.", "Multi-tenancy progression from RLS shared tables to silos with tenant-first indexing.", d_5_14),
    ("6.5", "2", "Chuỗi 4 tầng lưu web cùng cơ chế stale-while-revalidate và bẫy tiêu chuẩn Vary.", "Four-tier caching chain with stale-while-revalidate and Vary header pitfalls.", d_6_5),
    ("8.2", "2", "Fencing token tăng đơn điệu chặn leader cũ mất sync ghi đè lên lớp lưu trữ.", "Monotonic fencing tokens blocking stale paused leaders from corrupting shared storage.", d_8_2),
    ("8.3", "2", "Transactional Outbox gom ghi DB + phát event và chuỗi Saga có bước hoàn tác ngược.", "Atomic local Outbox relay plus forward Saga steps with compensating rollbacks.", d_8_3),
    ("8.4", "2", "Consistent Hashing vnode giảm di dời dữ liệu và công thức Quorum đọc-ghi W + R > N.", "Consistent hashing vnode placement paired with strict W + R > N quorum intersection.", d_8_4),
    ("8.5", "2", "4 tầng phòng thủ chịu lỗi chống bão retry: Load Shedding → Bulkhead → Breaker → Jitter.", "Four-layer cascade shield ordering Load Shedding, Bulkheads, Breakers, and Jittered Retry.", d_8_5),
    ("8.7", "2", "Bậc thang RPO/RTO từ 1 vùng tới Active-Active và mô hình cô lập vùng lỗi theo Cell.", "Multi-region DR ladder (RTO/RPO tiers) combined with bounded cell blast radius.", d_8_7),
    ("9.1", "2", "Control plane vòng reconcile của Kubernetes, 4 lớp probe và PDB khi drain node.", "Kubernetes declarative reconcile loop alongside ordered pod probes and PDB eviction guards.", d_9_1),
    ("9.7", "2", "Một artifact bất biến SHA-256 chạy qua canary tăng dần với phanh auto-rollback theo SLO.", "Immutable build digest advancing through SLO-gated canary percentages with auto-rollback.", d_9_7),
    ("10.3", "2", "OAuth 2.1 + PKCE, tách Access token ngắn hạn khỏi Refresh thu hồi tức thì và AuthZ.", "OAuth 2.1 + PKCE with short-lived access tokens, revocable refresh store, and RBAC/ABAC/ReBAC.", d_10_3),
    ("11.1", "2", "Chuỗi SLI → SLO → SLA, ngân sách lỗi 99.9% và cảnh báo burn-rate đa cửa sổ.", "SLI-SLO-SLA hierarchy, error budgets, and multi-window burn-rate alerting.", d_11_1),
    ("11.5", "2", "Vòng khép kín FinOps đo unit economics ($/đơn) và chặn các khoản ẩn egress/NAT.", "FinOps governance cycle tying unit economics to hidden egress/NAT/idle architectural leaks.", d_11_5),
    ("12.2", "2", "Hai pha Prefill (compute) và Decode (HBM bandwidth) kèm PagedAttention trong LLM serving.", "LLM serving Prefill/Decode resource split paired with PagedAttention and prefix caching.", d_12_2),
    ("12.5", "2", "Cổng Eval PR trên golden set kết hợp Guardrails 3 lớp bảo vệ Đầu vào · Xử lý · Đầu ra.", "Golden-set PR evaluation gates alongside 3-wall Input, Process, and Output guardrails.", d_12_5),
    ("13.1", "2", "Sổ cái kép (SUM = 0), Idempotency-Key toàn trình và đối soát 3 chiều hằng đêm.", "Double-entry accounting invariant, end-to-end idempotency keys, and 3-way reconciliation.", d_13_1),
    ("14.10.2", "2", "Rủi ro Harvest-Now-Decrypt-Later và lộ trình chuyển dịch hybrid PQC FIPS 203/204/205.", "Harvest-Now-Decrypt-Later timeline and hybrid X25519+ML-KEM / ML-DSA migration controls.", d_14_10_2),
]


def generate_all(write_csv=True):
    os.makedirs(paths.CONTENT_DIAGRAMS, exist_ok=True)
    rows = []
    for idx, (chap, sec, cap_vi, cap_en, fn) in enumerate(SPECS, 1):
        svg_txt = fn()
        # Strict XML validation before writing
        ET.fromstring(svg_txt)
        fname = f"ch-{chap}.svg"
        fpath = os.path.join(paths.CONTENT_DIAGRAMS, fname)
        open(fpath, "w", encoding="utf-8", newline="\n").write(svg_txt)
        rows.append({
            "diagram_id": f"D-{idx:02d}",
            "chapter": chap,
            "svg_file": fname,
            "anchor_section": sec,
            "caption_vi": cap_vi,
            "caption_en": cap_en,
        })

    if write_csv:
        csv_path = os.path.join(paths.FACTS, "diagrams.csv")
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            f.write("# DIAGRAMS — 30 so do SVG cho 30 chuong xuong song (SA-2028.1)\n")
            w = csv.DictWriter(f, fieldnames=["diagram_id", "chapter", "svg_file", "anchor_section", "caption_vi", "caption_en"])
            w.writeheader()
            for r in rows:
                w.writerow(r)
    return len(rows)


if __name__ == "__main__":
    n = generate_all(write_csv=True)
    print(f"DIAGRAMS: generated {n} validated SVGs -> content/diagrams/ + facts/diagrams.csv")
