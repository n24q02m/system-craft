# 3.2 — Python Runtime (3.11 → 3.15)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** lang-2.md

---

## 0. Nhập môn

**Đọc trước:** 3.1.

**Sợi chỉ đỏ:** *Python ra sản phẩm nhanh — nhưng chậm ở đâu, và khi nào lỗi của bạn không phải tại ngôn ngữ?* — trả lời: Python là runtime ra sản phẩm nhanh nhất trong 6+1 lựa chọn; cái giá là GIL giữ việc tính nhiều thread — nhưng chương này dạy phân loại thời gian trước, vì chỗ chậm thật thường không nằm ở ngôn ngữ. Câu hỏi để lại cho chương sau: *Đẩy trạng thái đơn realtime cho hàng vạn client — event loop của Node dạy gì?*

**Thuật ngữ sẽ gặp:** *GIL* — khoá toàn cục: một thread chạy bytecode Python tại một thời điểm; *refcount + cycle GC* — đếm tham chiếu dọn rác tức thời, kèm bộ dọn vòng tròn; *py-spy* — soi profile process đang chạy, không cần restart; *asyncio* — event loop cho I/O song song (không phải tính song song); *C extension* — đoạn native có thể nhả GIL khi tính nặng; *vòng đời request* — từ accept tới trả response, chỗ mọi miligiây được chi.

**Ví dụ mở đầu:** Team DM đổ "Python chậm" cho API gợi ý. py-spy chạy 60 giây: 55% thời gian là "chờ" — chờ DB, chờ HTTP. Đổi sang Rust cũng vẫn chờ y hệt. Chương này dạy chia thời gian ra trước khi đổ lỗi cho ngôn ngữ — còn chỗ Python thật chậm (serialization) thì đổi thư viện là đủ.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Song song hoá bằng gì: multiprocess / free-threaded 3.13t+ / C-ext / sang Go | GIL của tôi là cổ chai đã đo chưa? |
| 2 | Phiên bản Python cho service mới | 3.12 (security-only) hay 3.14/3.15 — trade-off gì với team? |
| 3 | ASGI server + framework + JSON path | Uvicorn/hypercorn; orjson thay json chuẩn chưa? |
| 4 | On-demand import & khởi động lạnh (FaaS) | Khối lượng import có làm cold start 100ms→1s không? |

---

## 2. Cơ chế

### 2.1 Trạng thái phiên bản (verify 2026-10-30)

| Phiên bản | Trạng thái | Ghi chú |
|---|---|---|
| 3.15 | mới nhất (3.15.2, 10/2026) | PEP 790 hướng tự do tối ưu hoá; free-threaded + JIT tiến bộ |
| 3.14 | hỗ trợ đầy đủ (3.14.10) | free-threaded bản chính thức hỗ trợ; subinterpreters |
| 3.13 | hỗ trợ (3.13.18) | bản free-threaded **thực nghiệm** đầu (PEP 703) |
| 3.12/3.11 | security-only | EOL 2028/2027 |
| 3.10 | **EOL 2026-10-01** | đã chết — upgrade bắt buộc |

Chu kỳ release: 10 tháng/lần, EOL 5 năm — việc nâng cấp nên là việc định kỳ, không phải "dự án".

### 2.2 GIL: nó thực sự khóa cái gì

Global Interpreter Lock đảm bảo **một** thread chạy bytecode Python tại một thời điểm (per-interpreter). Thread vẫn hợp lệ cho **I/O** (nhả GIL khi chờ) — bẫy chỉ nổ với **CPU-bound thuần Python** (thread không ăn thêm lõi). Ba lối thoát truyền thống: multiprocess (copy interpreter — IPC qua pickle), C-extension (nhả GIL trong tính toán — NumPy/numpy/pandas sống nhờ thế), và… viết phần nóng bằng ngôn ngữ khác.

**Free-threaded (PEP 703, "3.13t → 3.14+"):** GIL bỏ hẳn,giá = ~5–10% single-thread chậm hơn + một số C-ext cần port (tình trạng 2026 đã phủ phần lớn phổ biến: NumPy, etc., nhưng **kiểm tra** dependency của bạn trước khi hứa). Dùng khi: thật sự CPU-bound, đã đo, và quy mô tiến trình đơn quan trọng. Dùng sai khi: workload I/O (async đã đủ) hoặc nhỏ (multiprocess rẻ hơn).

### 2.3 Vòng đời request Python web hiện đại

```
Client → ASGI server (Uvicorn: event loop asyncio + threadpool cho sync)
       → framework (FastAPI/Starlette/Django-async)
       → orjson/msgspec (serialization — thay json C-stock)
       → driver bất đồng bộ (asyncpg/redis-py async) — KHÔNG chặn loop
       → blocking lúc nào? → chạy threadpool (run_in_executor)
```

Ba quyết định ăn tiền: (1) orjson ~5–10× json stdlib (I); (2) asyncpg ~2–5× psycopg2 trong path async (I); (3) `PYTHONOPTIMIZE` + pre-compile (`__pycache__` đóng băng vào image — giảm cold start).

### 2.4 Mô hình bộ nhớ Python: refcount + cycle GC

Mọi object có refcount; GC chỉ dọn **chu kỳ** (thế hệ 0/1/2). Hệ quả thực dụng:
- Đóng tài nguyên bằng `with`/context manager (refcount giải phóng ngay) — không trông chờ GC;
- Object lơ lửng (global list, closure — →3.9) là leak thật, không tự hết;
- **`gc.freeze()`** cho FaaS/process-fork: đóng băng heap cha, con fork không phải dọn lại — giảm copy (nối 2.1 COW).

### 2.5 Vận hành: đo gì, vá gì

- **py-spy** — flame graph không cần sửa code (gold standard chẩn Python chậm: thấy ngay đang ở Python-code, C-ext, hay đang chờ);
- **PYTHONASYNCIODEBUG=1** — bắt việc chặn event loop;
- Startup: `-X importtime` — danh sách module chậm (thường pandas ~0,5–1 s — cân nhắc lazy import);
- Dependencies: `uv` (2024+) đã thành mặc định quản lý env/lock (nhanh hơn pip ~10–100× (I)) — lock file vào repo như mọi runtime khác.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị | Nhãn | Ghi chú |
|---|---|---|---|
| 3.10 EOL | 2026-10-01 | V | versions.csv |
| Free-threaded | 3.13 experimental → 3.14+ official track | V | PEP 703 |
| orjson vs json | ~5–10× | I | đo trên payload của bạn |
| pandas import | ~0,5–1 s | I | lazy import nếu FaaS |
| Refcount giải phóng | ngay khi về 0 | V | GC chỉ dọn chu kỳ |

---

## 4. Suy luận kiến trúc

- **S1:** Python đổi câu hỏi "nhanh không" thành "đường nóng ở đâu" — chuẩn thư viện + data path C (NumPy/Arrow) + glue Python là pattern thắng 20 năm.
- **S2:** Tham số trụ: CPU% phân biệt (Python vs native qua py-spy), event loop delay, RSS per-worker, import time.
- **S3:** Free-threaded đổi ~5–10% single-thread lấy scale lõi thật; multiprocess đổi bộ nhớ + IPC lấy đơn giản; C-ext đổi gánh build/port lấy tốc độ đoạn nóng.
- **S4:** Node 22+ bỏ cần Python để build (native binding ít hơn) + `uv` tốc độ package — "ma sát vận hành Python" giảm nhanh, kéo Python sâu hơn vào ops/scripting nơi Bash/Node từng giữ.
- **S5:** AI/ML kéo Python về vị trí "ngôn ngữ của data" (PyTorch, vLLM đều Python-first) — kỹ năng tối ưu serving Python (→12.2) là kỹ năng hạ tầng AI, không phải kỹ năng "web".
- **S6:** Khi Python chậm: py-spy trước, tối ưu sau. 80% trường hợp là I/O/serialization/đợi — không phải interpreter.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Multi-thread không ăn CPU | GIL (CPU-bound thuần) | py-spy (thấy 1 thread chạy) | §2.2 |
| Latency vọt khi parse JSON lớn | json stdlib chậm | orjson; msgspec | §2.3 |
| Event loop lag cao | sync I/O trong async path | PYTHONASYNCIODEBUG | §2.3 |
| FaaS cold start > 1 s | Import nặng | -X importtime; lazy | §2.5 |
| RSS mỗi worker phình theo thời gian | Object lơ lửng (closure/global) | tracemalloc snapshot diff | §2.4 |
| Free-threaded chậm hơn 3.13 thường | overhead single-thread | đo lại; có thật cần scale-lõi? | §2.2 |

---

## 6. Cách đo

```bash
# Flame toàn tiến trình, không cần code
py-spy record -o profile.svg --pid <pid> --duration 30
py-spy top --pid <pid>              # "top" của Python-code

# Blocking trong async
PYTHONASYNCIODEBUG=1 python app.py  # log cảnh báo coroutine chặn

# Khởi động — danh sách tội đồ import
python -X importtime -c "import app" 2> import.log; sort -t'|' -k2 -n import.log | tail

# Bộ nhớ theo chỗ
python -m tracemalloc 20 app.py      # top allocation
```

Nguyên tắc: **py-spy là đèn pin mặc định** — 30 giây cho biết vấn đề nằm ở tầng nào trước khi mở code.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay "đổi ngôn ngữ vì chậm":** phần nóng đã là C (NumPy) thì Python chỉ là glue — đổi sang Go chỉ đổi glue; đường thật thường là serialization + query (→5.2/5.4). **Thay multiprocess:** free-threaded khi CPU-bound đo được; hoặc dời tính sang DB (SQL đủ mạnh cho đa số aggregation — →5.8).

Năm thấu kính:
- **Kinh tế:** Python rẻ để viết, đắt để scale CPU — hợp đúng khi logic thay đổi nhanh (prototyped thật) và phần nóng nằm ở thư viện native.
- **Vận hành:** Pin version trong image + lock (uv) + định kỳ upgrade theo EOL (3.10 vừa chết 10/2026 — còn service nào 3.10 trong cụm của bạn?).
- **An ninh:** pip supply-chain từng có sự cố lớn (2024–2025); dùng lock + hash + private index (→10.4) — Python là hệ sinh thái hấp dẫn cho tấn công phụ thuộc.
- **Lịch sử:** GIL bị "khai tử" 20 năm (2026 mới thật sự bắt đầu có free-threaded production-track); bài học: tin vào lộ trình có PEP, không tin vào lời đồn.
- **Người dùng:** Với người dùng, Python vô hình; họ thấy "API AI trả chậm" — mà thường đó là đúng chương này (tokenize/parse/GIL) chứ không phải "GPU yếu".

---

## 8. Đọc tiếp & bài tập

- So sánh 6+1 runtime: **3.9** · Serving tier: **3.10, 12.2** · JSON/serialization chi phí: **3.11** · Bẫy xuyên ngôn ngữ: **3.9**
- **Bài tập 1:** py-spy top một service đang tải thật 60 giây. Phân loại thời gian: Python / native / chờ. Nếu "chờ" > 50% — vấn đề của bạn không phải ngôn ngữ.
- **Bài tập 2:** Thay json → orjson ở một endpoint serializ nặng; đo p50/p99. Ghi lại — đây thường là 10 dòng đổi lấy 30%.
- **Bài tập 3:** Chuyển một service 3.10 (đã EOL!) lên 3.12+; chạy test + py-spy so sánh. Lập ticket cho những service còn lại ngay hôm nay.
