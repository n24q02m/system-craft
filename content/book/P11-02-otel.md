# 11.2 — OpenTelemetry & 4 Tín hiệu

> **Tầng:** Vận hành · **Quyển II** · **Trục đọc:** độ tin cậy · **Động từ liên quan:** Đo · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 11.1 (SLO cần số đo) · 5.11 (cardinality — đã gặp).

**Sợi chỉ đỏ:** *Đo được thì phải thấy — bốn tín hiệu telemetry ghép nhau thế nào?* — trả lời: thấy bằng bốn tín hiệu — trace (đi qua đâu), metric (bao nhiêu), log (chuyện gì xảy ra), profile (tốn ở đâu) — ghép nhau qua trace ID chung; OpenTelemetry là ngôn ngữ chung mọi runtime; sampling head/tail quyết định hóa đơn và độ trung thực; cardinality là quả bom chậm của metric. Câu hỏi để lại cho chương sau: *Biết sức chứa đâu mà cân tải — đo đạc, capacity planning và chaos dạy gì?*

**Thuật ngữ sẽ gặp:** *trace* — một request để lại vết qua chín trạm (nối 3.10): span nối span; *span* — một đơn vị việc trong trace: tên, thời gian, attribute; *head vs tail sampling* — quyết định lấy mẫu ở đầu (rẻ nhưng mù) hay cuối (giữ được đúng request lỗi): bẫy 100% là hóa đơn; *cardinality* — số tổ hợp label riêng biệt: phình lên là tiền và truy vấn chậm (nối 5.11); *correlate* — metric, log, trace cùng trace ID: ba câu hỏi trả lời trong một cú nhấp; *collector* — tầng gom và lọc trung gian: app đừng đẩy thẳng tới backend.

**Ví dụ mở đầu:** p99 của DM xấu đi: metric nói "có chuyện" nhưng không nói ở đâu; log đầy stack nhưng rời rạc; trace gắn trace ID xuyên suốt chín trạm cho thấy ngay 700 ms nằm ở hop thứ năm, đang chờ pool. Bốn tín hiệu là bốn câu hỏi khác nhau — chương này ghép chúng bằng OpenTelemetry thay vì bốn bộ tool bốn định dạng.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Bốn tín hiệu (trace/metric/log/profile) — cái nào trước, cái nào trả tiền | Tôi mù về gì nhất — luồng (trace), sức khoẻ (metric), chứng cứ (log), hay tài nguyên (profile)? |
| 2 | Sampling trace: head vs tail, tỉ lệ | Tôi có cần 100% trace không — hay 100% trace **của lỗi**? |
| 3 | Cardinality: cái gì được làm label | Metric của tôi nổ kho vì label gì (user_id? request_id?) |
| 4 | Vận hành: tự chạy collector/backend hay managed | Ai trực hệ này lúc 2h sáng — và nó tự chết thì sao? |

---

## 2. Cơ chế

### 2.1 Bốn tín hiệu — bốn câu hỏi khác nhau

| Tín hiệu | Trả lời | Chi phí | Chương đã gặp |
|---|---|---|---|
| **Trace** | request của tôi đi qua đâu, kẹt ở đâu? | cao (mọi hop) | 1.6, 8.6 |
| **Metric** | hệ khoẻ không — theo thời gian? | thấp (aggregate) | mọi chương §3 |
| **Log** | chính xác cái gì đã xảy ra? | trung bình–cao | 10.7 |
| **Profile** | CPU/heap của đoạn đó làm gì? | khi cần (continuous) | 2.x, 3.x |

Điều thú vị 2026: bốn tín hiệu **gắn với nhau qua trace-id/span-id** (exemplars — metric điểm về trace; log gắn span; profile gắn span) — chẩn đoán đi vòng tròn: metric đỏ → trace chậm → log tại span đó → profile của đoạn code — không rời ghế.

### 2.2 OpenTelemetry — ngôn ngữ chung

OTel là **chuẩn + SDK + collector** (CNCF): instrument một lần, gửi bất kỳ backend nào (vendor-neutral — không khóa). Ba khối cần biết: **SDK trong app** (auto-instrumentation phổ biến — HTTP/DB/gRPC tự bắt), **Collector** (agent đứng giữa: batch, lọc, sensitive-data scrub, route — nền tảng của mọi chiến lược sampling/giảm chi phí), **semantic conventions** (tên thuộc tính chuẩn — `http.route`, `db.system` — nên theo, query chéo hệ nhờ nó). Trạng thái 2026: trace/metric/log stable; **profiling signal** đang chuẩn hoá (đã có trong một số distribution) — hướng đi rõ.

### 2.3 Sampling trace — head vs tail (và cái bẫy 100%)

- **Head sampling** (quyết định khi bắt đầu): rẻ (không thu thập phần bỏ), nhưng **không biết đâu để giữ** — giữ ngẫu nhiên 1% thì đúng lúc cần trace lỗi lại không có;
- **Tail sampling** (quyết định khi kết thúc, tại collector): giữ **100% lỗi + 100% chậm (p99) + 1% bình thường** — vàng cho chẩn đoán; tốn bộ nhớ đệm request đang chạy;
- Chuẩn thực chiến: tail sampling tại collector trung tâm, tỉ lệ theo service (đường nóng 5–10%, batch 1%), **luôn giữ trace lỗi**. Chi phí telemetry là chi phí thật (storage + thu thập ~ vài % CPU) — sampling là kỹ thuật **kiểm soát hóa đơn mà giữ khả năng chẩn đoán**.

### 2.4 Cardinality — bom chậm của metric

Mỗi tổ hợp label là **một chuỗi thời gian** riêng: `http_requests_total{user_id=…}` × 1 triệu user = 1 triệu chuỗi — Prometheus-style backend chết (OOM/ chậm query — D-120). Quy tắc: **label chỉ nhận tập giá trị hữu hạn nhỏ** (route, status class, region, version); **không bao giờ** user_id/request_id/trace_id làm label (chúng thuộc về trace/log — exemplar nối); cardinality budget per metric (audit `label_values()` định kỳ). Đã gặp nhiều lần: "metrics giết monitoring" là dạng sự cố khó hiểu nhất vì dấu hiệu là **chính hệ giám sát chết**.

### 2.5 Log — cấu trúc, mức, và hygiene

- **Structured JSON** (field, không câu prose) — query/parse được; correlation-id tự động chèn từ trace context;
- **Mức có nghĩa thật:** DEBUG (dev), INFO (sự kiện nghiệp vụ), WARN (tự chữa được), ERROR (cần người) — "ERROR làm nền" làm on-call mù;
- **Hygiene:** không ghi secret (I-063 — →10.6 redact), không ghi PII thừa (→10.8), có **request_id/user_id** (điều tra cần), retention theo lớp (vận hành 30 ngày, an ninh 1 năm — →10.7);
- Không dùng log làm metric (đếm log line cho SLO — chậm và đắt; metric tồn tại để làm điều đó) và không dùng metric làm log (không có "cái gì đã xảy ra").

### 2.6 Vận hành đám mây telemetry

Collector là hạ tầng phải HA (batch + retry + load-balance giữa nhiều instance); mất telemetry lúc sự cố = mù đúng lúc cần mắt nhất (đó là thất bại kép kinh điển). Ba tầng tiêu thụ: **realtime** (alert — →11.1 burn rate; 11–15 phút window), **gần-realtime** (dashboard 30–60 phút), **lưu trữ dài** (điều tra/trend — object storage rẻ). Mỗi tầng backend khác nhau (alerting TSDB vs cheap storage) — đừng ép một hệ làm cả ba (đắt hoặc yếu).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| OTel trace/metric/log | stable; profiling đang chuẩn hoá | V | CNCF |
| Tail sampling chuẩn | 100% lỗi + 100% p99-chậm + 1–10% thường | P | |
| Cardinality an toàn | < ~vài chục chuỗi/metric thường | P | theo backend |
| Overhead telemetry | vài % CPU (SDK+collector) | I | |
| Retention log | 30 ngày ops / 1 năm an ninh | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Observability là **khả năng trả lời câu hỏi mới không cần deploy code mới** — trace/metric/log/profile là bốn loại bằng chứng; thiếu một loại là có câu hỏi không trả lời nổi (và sẽ bị hỏi đúng loại đó);
- **S2:** Tham số trụ: tỉ lệ trace lỗi có context (gần 100%), cardinality tổng (trend), chi phí telemetry/GB/tuần, thời gian từ "câu hỏi" → "đồ thị" (< 5 phút là khỏe).
- **S3:** Sampling đổi chi phí lấy độ phủ chọn lọc; cardinality discipline đổi tính query lấy sự sống của backend — hai quyết định này định hình hóa đơn telemetry nhiều hơn mọi tối ưu khác.
- **S4:** OTel là **hợp đồng dữ liệu của vận hành** — như OpenAPI cho API (→4.3): theo chuẩn thì đổi backend/thêm consumer không đụng app; tự chế format là tự nhốt mình.
- **S5:** AI dùng telemetry hai cách: (a) phân tích — LLM đọc log/trace tóm tắt "chuyện gì xảy ra" (đang hoạt động thật trong incident tooling — →11.4); (b) **sinh tải mới** — agent sinh request phải mang trace context như người dùng (không thì mù một lớp);
- **S6:** Khi "không tái lập được": kiểm tra tín hiệu nào vắng (thường là trace xuyên — chỉ có log rời), rồi fix theo §2.2/§2.3 — đừng cố tái lập bằng tay cái mà hệ có thể ghi lại tự động.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Trace đứt giữa các service | Context không truyền (queue/HTTP) | propagate header chuẩn | §2.2 |
| Lỗi xảy ra mà không có trace | Head sampling bỏ đúng cái lỗi | tail sampling giữ lỗi | §2.3 |
| Prometheus OOM | Cardinality nổ (user_id label) | audit label + budget | §2.4 |
| Log không tìm ra gì khi sự cố | Prose + thiếu correlation-id | structured + trace-id | §2.5 |
| "ERROR làm nền" | Lạm dụng mức ERROR | policy mức + review | §2.5 |
| Mất telemetry đúng lúc sự cố | Collector không HA / chết theo app | collector riêng + batch | §2.6 |

---

## 6. Cách đo

```bash
# Kiểm tra context truyền đúng (từ ngoài vào):
curl -sH 'traceparent: 00-<32hex>-<16hex>-01' https://app/api/health
#   → log/backend phải hiện trace-id đó xuyên suốt các service
#   đứt ở service nào = propagate thiếu ở đó

# Cardinality audit (Prometheus):
count({__name__=~"http_.*"}) by (__name__)   — top theo chuỗi
topk(10, count by (job, route) (http_requests_total))  — thủ phạm thường ở đây
```

Nguyên tắc: **telemetry tự nó là một hệ thống có SLO** (đủ dữ liệu khi cần — uptime collector, độ trễ ingest) — nó chết mà không ai biết là lỗi thiết kế của chương này.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay OTel tự vận hành:** vendor managed (Datadog-style — đủ nhanh, khóa + đắt theo GB); **thay tail sampling phức tạp:** head 10% + luôn ghi ERROR log có stack (kém chuẩn đoán hơn, đơn giản hơn — hợp lúc nhỏ); **thay collector HA:** gửi thẳng vendor từ app (mất tầng scrub/batch — chấp nhận được lúc nhỏ).

Năm thấu kính:
- **Kinh tế:** Telemetry là **hệ duy nhất sinh ROI khi sự cố** (rút ngắn MTTD/MTTR — mỗi phút downtime có giá); nhưng cũng là hệ dễ đốt tiền vô hình nhất (sampling + retention là hai vòi chính — kiểm soát chủ ý);
- **Vận hành:** Dashboard "meta" — sức khoẻ của chính telemetry (ingest rate, drop, cardinality) — phải tồn tại; hệ giám sát giám sát chính nó không phải nghịch lý, là điều kiện;
- **An ninh:** Telemetry là **kho dữ liệu nhạy thứ hai** của tổ chức (log chứa token? user_id? nội dung?) — redact + retention + quyền truy cập (→10.6/10.8) áp cho nó như DB;
- **Lịch sử:** Syslog (1980s) → APM vendor từng đóng (2010s, instrument riêng mỗi hãng) → Prometheus (2012, metric mở) → OpenTracing+OpenCensus hợp nhất thành **OpenTracing → OpenTelemetry** (2019+) → 4 tín hiệu một chuẩn (2020s): ngành học lại bài **mở chuẩn thắng đóng cụm** — như HTTP/API đã học (4.x);
- **Người dùng:** Người dùng không cần biết system có trace — nhưng khi họ tweet "app lỗi từ 14h", tổ chức có trace **trả lời được trong 5 phút** chính xác thứ gì ảnh hưởng họ; đó khác biệt giữa xin lỗi chung chung và "chúng tôi biết chính xác cái gì đã xảy ra với bạn".

---

## 8. Đọc tiếp & bài tập

- SLO dùng tín hiệu: **11.1** · Chaos/đo.capacity: **11.3** · Incident: **11.4** · Log an ninh: **10.7** · Profiling ngôn ngữ: **3.x** · Frontend RUM: **7.6**
- **Bài tập 1:** Chạy curl traceparent (§6) xuyên 3 service chính. Trace-id sống qua hết không? Đứt ở đâu — sửa truyền header ở đó (thường là qua queue: cần propagate qua message attribute).
- **Bài tập 2:** Audit cardinality (§6): top 10 metric theo số chuỗi. Mỗi cái > 1.000 chuỗi: tìm label vô hạn và bỏ ra trace/log. Bài 30 phút cứu một trận OOM tương lai.
- **Bài tập 3:** Đặt tail sampling theo chuẩn §2.3 (100% lỗi + chậm, 5% thường) và đo: chi phí GB/tuần trước–sau + số lần bạn cần trace lỗi và **có nó**. Hai con số đó là bài thuyết trình cho lãnh đạo về telemetry.
