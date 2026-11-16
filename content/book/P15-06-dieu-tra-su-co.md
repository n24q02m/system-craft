# P15-06 — Sổ tay Điều tra Sự cố Thực chiến (5 Ca Điển hình)

> **Tầng học mở rộng** · Áp dụng khung [11.4 (Chỉ huy Sự cố & Postmortem)](./P11-04-incident.md), [INDEX-INCIDENTS](./P15-00-tang-hoc-cach-dung.md) và chuỗi lab `P15-03-L02`, `L05`, `L09`, `L12`.
> **Trạng thái:** VIẾT XONG · Học đọc chứng cứ theo thứ tự: Triệu chứng → Giả thuyết cạnh tranh → Lệnh đo 15 giây → Gốc & Vá.

---

## 1. Khung OODA 15 Giây trước khi Khởi động lại Pod

Khi sự cố nổ lúc 02:00 sáng, phản xạ `kubectl rollout restart` chỉ xoá mất dấu vết RAM/thread dump và có thể kích hoạt thundering herd (`I-052`). Trước khi restart, luôn đi qua 4 bước:

1. **Khoanh vùng tầng lỗi (30s):** Lỗi nằm ở Client/Edge (`6.x`, `4.2`), App Runtime (`3.x`), Hàng đợi/DB (`5.x`), Hạ tầng/Kernel (`2.x`, `9.x`) hay AI Serving (`12.2`)?
2. **Đặt đúng 3 giả thuyết loại trừ nhau:** Không ôm 1 giả thuyết rồi chỉ đi tìm bằng chứng ủng hộ nó.
3. **Chạy đúng 1 lệnh kiểm chứng rẽ nhánh:** Ưu tiên chứng cứ trực tiếp từ kernel (`cgroup`, `ss`, `PSI`), profiler runtime (`pprof`, `py-spy`, `JFR`), hoặc explain/metrics tầng dữ liệu thay vì nhìn chart CPU trung bình 5 phút.
4. **Hành động hai pha:** **Giảm thiệt hại ngay** (cắt tải/rollback/nới giới hạn an toàn) → **Sửa gốc rễ sau** kèm regression check vào CI.

---

## Triage 1 — p99 API tăng gấp 3 dù CPU node báo chỉ 55%

* **Dấu vết danh mục:** `I-002` (CFS throttling), `I-018` (Event loop block), `I-020` (GC pause) · **Chương gốc:** `2.3`, `3.3`, `3.6`, `3.10` · **Lab liên kết:** [`P15-03-L02`](./P15-03-L02-p2.md).
* **Triệu chứng ban đầu:** Đường `p50` vẫn đẹp (`28 ms`), nhưng `p99` nhảy từ `110 ms` lên `480 ms` mỗi khi tải tăng nhẹ; Grafana hiển thị `host CPU ~ 55%` nên nhiều kỹ sư kết luận "không phải nghẽn CPU".
* **Ba giả thuyết cần loại trừ trong 60 giây:**
  1. **G1 — Kernel CPU throttling (`cgroup v2`):** Container bị `limits.cpu` quá thấp dù host rảnh, cứ tiêu hết quota trong cửa sổ `100 ms` là bị đình chỉ phần còn lại của chu kỳ (`2.3`).
  2. **G2 — Runtime STW / Event-loop block (`3.x`):** JVM G1/ZGC stop-the-world, hoặc Node.js `JSON.parse`/sync crypto chặn single thread (`I-018`).
  3. **G3 — Downstream tail (`3.10`):** Một hop DB hoặc external API đẩy tail qua retry.
* **Lệnh kiểm chứng nhanh:**

```bash
cat /sys/fs/cgroup/cpu.stat        # xem nr_throttled và throttled_usec
cat /proc/pressure/cpu             # xem some avg10 / full avg10 (PSI)
# nếu throttled_usec == 0 -> kiểm tra runtime lag / GC log:
# Go: curl -s localhost:6060/debug/pprof/trace?seconds=5 > trace.out
# Node: theo dõi event_loop_utilization / --prof; JVM: jstat -gcutil <pid> 1000 5
```

* **Bắt bệnh thật:** `throttled_usec` tăng đều hàng trăm miligiây mỗi giây trong khi `requests.cpu = 500m, limits.cpu = 1000m`: một burst 4 thread chạy `25 ms` ăn hết quota `100 ms` rồi cả pod bị đóng băng `75 ms`! Hoặc ở Node/Python: `nr_throttled == 0` nhưng `event loop lag` nhảy vọt mỗi khi nhận payload > `2 MB`.
* **Xử lý ngay:** Gỡ hoặc nới `limits.cpu` với dịch vụ latency-sensitive theo khuyến nghị cụm Kubernetes (`9.1`, giữ `requests.cpu` chuẩn để scheduler đặt pod đúng chỗ); nếu lỗi do blocking runtime → tách pool / worker / stream parser.
* **Phòng ngừa dài hạn:** Gắn alert tỷ lệ `rate(container_cpu_cfs_throttled_periods_total) / rate(container_cpu_cfs_periods_total) > 0.05` thay vì chỉ alert `% CPU`.

---

## Triage 2 — Checkout DB quá tải đúng 00:01 giờ Flash Sale

* **Dấu vết danh mục:** `I-033` (Cache stampede), `I-049` (Double charge), `I-050` (Retry storm), `I-052` (Thundering herd) · **Chương gốc:** `4.8`, `5.2`, `5.4`, `8.5`, `13.1` · **Lab liên kết:** [`P15-03-L05`](./P15-03-L05-p5.md).
* **Triệu chứng ban đầu:** Lưu lượng người dùng thực tăng `3×`, nhưng lượng query vào PostgreSQL Primary tăng **`25×`**, kết nối chạm `max_connections` (`I-039`), một số khách báo bị trừ tiền hai lần (`I-049`).
* **Ba giả thuyết cần loại trừ:**
  1. **G1 — Stampede + Retry Storm:** Key cache sản phẩm hot hết TTL đồng thời khiến hàng nghìn worker chọc DB; khi DB chậm quá timeout client `2s`, client/proxy retry `3×` tạo hiệu ứng nhân tầng (`I-050`).
  2. **G2 — Missing index / Lock contention:** Query kiểm kho chạy `Seq Scan` (`5.2`) hoặc giao dịch giữ lock dài (`I-041`).
  3. **G3 — Thiếu `Idempotency-Key` ở cổng thanh toán (`4.8`, `13.1`).**
* **Lệnh kiểm chứng nhanh:**

```sql
-- 1) Kiểm tra hàng đợi lock & query đang treo trên PostgreSQL
SELECT pid, state, wait_event_type, wait_event, now() - query_start AS dur, left(query, 80)
FROM pg_stat_activity
WHERE state <> 'idle' ORDER BY dur DESC LIMIT 15;
```

```bash
# 2) So tỷ lệ request gốc từ edge với request nội bộ (phát hiện retry factor)
# Kiểm tra cache hit-rate & số key expired đột biến tại T+00:00
redis-cli info stats | grep -E 'keyspace_(hits|misses)|expired_keys'
```

* **Bắt bệnh thật:** Cả ba tầng cộng hưởng: TTL đồng loạt gây Miss đồng loạt (`I-033`), query chậm kích hoạt retry không jitter/không token-bucket (`8.5`), và endpoint `/checkout` không khoá `Idempotency-Key` trong cùng transaction với trạng thái đơn hàng (`8.3`, `13.1`).
* **Xử lý ngay:** Bật load shedding / rate limit có `Retry-After` ở edge (`4.8`), ngắt retry tự động trên non-idempotent POST, tăng pool qua `PgBouncer` và trả stale-while-revalidate cho key sản phẩm.
* **Phòng ngừa dài hạn:** Dùng `singleflight` + TTL có jitter (`±15%`), bắt buộc `Idempotency-Key` cho mọi mutation tài chính (`13.1`), gắn retry budget ≤ `10%` lưu lượng (`8.5`).

---

## Triage 3 — Rollout Kubernetes kẹt Pending/Terminating & 502 rải rác

* **Dấu vết danh mục:** `I-001` (OOM cgroup/glibc arena), `I-026` (502 keep-alive mismatch), `I-058` (PDB kẹt drain), `I-061` (DNS `ndots:5`) · **Chương gốc:** `2.1`, `4.2`, `9.1`, `9.3` · **Lab liên kết:** [`P15-03-L09`](./P15-03-L09-p9.md).
* **Triệu chứng ban đầu:** Sau khi nâng phiên bản node pool, rollout dừng nửa chừng; đồng thời ALB/Nginx thỉnh thoảng trả `502 Bad Gateway` trong 10 giây khi pod cũ tắt và latency RPC nội bộ tăng `~20 ms` do DNS.
* **Ba giả thuyết cần loại trừ:**
  1. **G1 — `PodDisruptionBudget` xung đột (`I-058`):** `minAvailable: 100%` hoặc số replica = `minAvailable`, khiến kubelet/drain không được phép trục xuất pod cuối.
  2. **G2 — Race condition keep-alive & preStop (`I-026`, `4.2`, `9.1`):** ALB/Nginx giữ `keepalive_timeout = 65s`, còn app server đóng sau `60s` (hoặc app tắt tức thì trước khi kube-proxy/EndpointSlice rút IP).
  3. **G3 — Cạn Arena/Page Cache OOM (`I-001`) hoặc `ndots:5` DNS nhân truy vấn (`I-061`).**
* **Lệnh kiểm chứng nhanh:**

```bash
kubectl get pdb -A
kubectl describe deployment <app> | tail -n 25
# Kiểm tra timeout keep-alive hai đầu (app vs ingress/LB) và /etc/resolv.conf trong pod:
kubectl exec <pod> -- cat /etc/resolv.conf
```

* **Bắt bệnh thật:** `PDB` khoá drain; app `idle_timeout` nhỏ hơn LB `keepalive_timeout` (`I-026`); và `options ndots:5` khiến mọi tên miền ngoài (`api.partner.com`) phải thử 4 search domain nội bộ thành 5–10 query UDP DNS (`I-061`).
* **Xử lý ngay:** Chỉnh `PDB` hợp lý (`maxUnavailable: 1` hoặc `minAvailable <= replicas - 1`), đặt app `keepalive_timeout` **lớn hơn** LB (vd App `75s` > LB `60s`), thêm `preStop: sleep 5` trước SIGTERM grace period, bật NodeLocal DNSCache hoặc đặt `ndots:2` / dấu chấm cuối FQDN.
* **Phòng ngừa dài hạn:** Đưa bài kiểm tra drain/graceful-shutdown (0% 5xx khi rollout dưới tải) vào pipeline staging (`9.7`).

---

## Triage 4 — Kafka Consumer Lag dựng đứng & Rebalance liên tục

* **Dấu vết danh mục:** `I-034` (Hot partition), `I-042` (Poison message), `I-043` (Rebalance storm), `I-044` (Lag tăng đều) · **Chương gốc:** `5.7`, `5.15`, `8.3` · **Lab liên kết:** `5.7` (Tầng Dữ liệu & Outbox).
* **Triệu chứng ban đầu:** Consumer lag nhảy từ `0` lên `450k` message trong 15 phút; pod không crash (Exit 0) nhưng log ngập tràn `Revoking previously assigned partitions` / `Rebalance in progress`.
* **Ba giả thuyết cần loại trừ:**
  1. **G1 — Rebalance storm (`I-043`):** Một batch `500` record xử lý mất `6 phút` > `max.poll.interval.ms` (`5 phút`), broker tưởng consumer chết và đá khỏi group → batch bị gửi lại cho node khác lặp vô tận!
  2. **G2 — Poison message (`I-042`):** Một record schema lỗi làm consumer ném exception không commit offset rồi restart loop đúng partition đó.
  3. **G3 — Hot partition key (`I-034`):** 90% sự kiện dùng cùng 1 `merchant_id = null` rơi hết vào 1 partition duy nhất, 11 consumer khác ngồi chơi.
* **Lệnh kiểm chứng nhanh:**

```bash
kafka-consumer-groups.sh --bootstrap-server <broker> --describe --group <cg>
# Nhìn kỹ sự phân bố LAG theo từng PARTITION (lệch về 1 partition hay đều?)
# và cột CURRENT-OFFSET có đứng im hay nhảy lùi liên tục không.
```

* **Bắt bệnh thật:** Nếu đúng 1 partition lag cao còn lại = 0 và log lỗi parse JSON tại offset cố định → `G2` Poison message (`I-042`) hoặc `G3` Hot key (`I-034`). Nếu nhiều partition đổi `CONSUMER-ID` mỗi vài phút → `G1` Processing time > `max.poll.interval.ms` (`I-043`).
* **Xử lý ngay:** Chuyển poison message sau N lần retry sang **Dead Letter Queue (DLQ)** (`5.7`); giảm `max.poll.records` (vd từ `500` xuống `50`) hoặc nâng `max.poll.interval.ms`, dùng CooperativeStickyAssignor để giảm stop-the-world khi rebalance.
* **Phòng ngừa dài hạn:** Thực thi `AsyncAPI / Schema Registry` chặn producer gửi record lỗi từ cửa vào (`4.7`), xử lý batch idempotent dựa trên Outbox/dedup key (`8.3`).

---

## Triage 5 — LLM RAG Endpoint TTFT vọt 8s & Agent rò Dữ liệu chéo Phòng

* **Dấu vết danh mục:** `I-066` (TTFT cao dù GPU chưa bão hoà compute), `I-067` (Token bill tăng `10×`), `I-068` (ACL không lọc ở retrieval) · **Chương gốc:** `12.2`, `12.3`, `12.5`, `12.6`, `10.3` · **Lab liên kết:** [`P15-03-L12`](./P15-03-L12-p12.md).
* **Triệu chứng ban đầu:** Hai sự cố liên tiếp cùng sprint AI: (a) người dùng kêu "chờ 8 giây mới hiện chữ đầu tiên" dù tổng request/s thấp; (b) nhân viên phòng Sales hỏi chatbot RAG lại nhận được đoạn trích từ tài liệu lương phòng HR.
* **Ba giả thuyết cần loại trừ (Hiệu năng + An ninh):**
  1. **G1 — Prefill/KV-Cache contention (`I-066`, `12.2`):** System prompt + lịch sử RAG `24k token` không bật Prefix Caching, cộng chung hàng đợi với request sinh text dài làm prefill nghẽn đầu.
  2. **G2 — Reasoning / Agent loop bloat (`I-067`, `12.4`, `12.6`):** Model bật reasoning budget mặc định hoặc agent gọi tool lặp 6 vòng đẩy số token lên `10×`.
  3. **G3 — Prompt-level ACL thay vì Retrieval-level ACL (`I-068`, `12.3`, `12.5`):** Chunk nhạy cảm được retriever kéo thẳng vào context rồi hy vọng system prompt "cấm nhắc tới dữ liệu phòng khác" sẽ giữ bí mật.
* **Lệnh kiểm chứng nhanh:**

```bash
# 1) Đọc metric hàng đợi prefill/KV cache từ vLLM/SGLang:
curl -s http://localhost:8000/metrics | grep -E 'num_requests_waiting|gpu_cache_usage_perc|time_to_first_token'
# 2) Kiểm tra trace GenAI + ACL filter trước retrieval:
# xác minh mọi vector/keyword query đều nhận tenant_id / acl_groups làm pre-filter bắt buộc
```

* **Bắt bệnh thật:** `num_requests_waiting > 0` và `gpu_cache_usage_perc ~ 0.96` (hết chỗ KV cache cho sequence dài -> preemption!) đẩy TTFT lên `8s`; đồng thời vector index lọc ACL theo dạng post-filter hoặc không có metadata ACL khi chunking/ingest (`12.3`).
* **Xử lý ngay (An ninh trước):** Tắt ngay truy vấn chung nếu chưa có **pre-filter ACL cứng tại vector/search engine** gắn thẳng với token danh tính người dùng (`10.3`, `12.5`); đồng thời bật Prefix Caching (`12.2`), giới hạn `max_tokens` + capping agent turns (`12.4`), tách pool prefill dài khỏi chat ngắn.
* **Phòng ngừa dài hạn:** Mọi PR đụng RAG/Agent phải chạy bộ red-team `I-068` (user phòng A thử truy vấn câu đặc trưng của phòng B → phải trả về `0` chunk rò rỉ) và theo dõi OTel `gen_ai.usage.*` + `TTFT p95` trên CI eval (`12.5`).
