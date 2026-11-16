# P15-02-QA — Quiz Nâng cao: 60 câu, 15 cụm


> **Tầng:** Học · **Làm khi:** sau khi đã làm quiz cụm (≥6/8) và lab của cụm · **Thời lượng:** 15–20 phút/cụm ·
> **Bản:** SA-2028.1 · **Tổng bài tập:** 8 câu/cụm (quiz cụm) + 4 câu/cụm (bộ này) = 12 × 15 = 180 câu *(cộng 25 câu trong Q00–Q14 gốc)*

---
Quy tắc: làm không nhìn sách, không tra; ≥3/4 mới coi là "đã qua cụm". Câu nào sai ⇒ đọc lại đúng § được ghi ở đáp án, không đọc cả chương.
Bộ này khác quiz cụm ở chỗ: quiz cụm hỏi "có biết không", bộ này hỏi "có quyết định đúng không". Mọi câu đều có một phương án nghe rất hợp lý nhưng sai vì bỏ qua một ràng buộc — tìm ra ràng buộc đó là mục đích của câu hỏi.

### Cụm P0 — Bản đồ, Tiên đề & Nhận thức luận

A0.1. Hai kỹ sư cãi nhau 2 giờ về "nên dùng message queue hay gọi trực tiếp". Cách xử lý đúng nhất theo 0.1?

- A. Chọn người có nhiều kinh nghiệm hơn trong hai người
- B. Vẽ 7 trục, ghim vị trí từng ý — nếu hai bên khác trục, tách quyết định làm hai
- C. Làm benchmark cả hai rồi so số
- D. Đưa ra họp kiến trúc để bỏ phiếu

A0.2. Một đồng nghiệp nói "hệ này chắc chắn không mất dữ liệu vì đã bật replication 3 bản". Câu trả lời đúng theo 0.2 (tiên đề) là:

- A. Đúng, 3 bản là đủ
- B. Hỏi: tiên đề nào bị bỏ qua — A3 (mất gói/partition) hay A4 (hỏng âm thầm)? Và ai kiểm chứng điều đó, lần cuối là khi nào?
- C. Đề nghị tăng lên 5 bản cho chắc
- D. Yêu cầu viết ADR

A0.3. Ma trận lens × động từ của một dịch vụ có hàng "Chẩn" trống hoàn toàn. Rủi ro cụ thể nhất là:

- A. Không ai viết tài liệu
- B. Khi sự cố, không ai biết bắt đầu từ đâu — nhưng on-call vẫn phải gánh, tức là rủi ro đã tồn tại mà không được phân bổ
- C. Thiếu ngân sách
- D. Không ảnh hưởng, vì đã có monitoring

A0.4. Tài liệu nội bộ ghi "Kafka 3.6 là bản mới nhất". Bạn kiểm tra thấy 4.4.0 đã ra. Hành động đúng nhất theo 0.4:

- A. Sửa con số và thôi
- B. Sửa con số và thêm dòng ERRATA ghi cũ→mới + ngày + nguồn, rồi đặt lịch soát định kỳ
- C. Viết lại cả tài liệu
- D. Báo cho quản lý

### Cụm P1 — Nền vật lý & Phần cứng

A1.1. Ứng dụng tăng 300% chậm sau khi thêm 2× số lõi nhưng không đổi code. Nguyên nhân ít khả năng nhất:

- A. False sharing tăng theo số lõi
- B. Tranh chấp khoá toàn cục
- C. Băng thông bộ nhớ / NUMA trở thành trần
- D. Ổ đĩa bị phân mảnh

A1.2. Cụm 10 đĩa 16 TB RAID5, URE 10¹⁴. Câu nào đúng?

- A. Rebuild an toàn vì chỉ đọc 1 đĩa
- B. Xác suất gặp lỗi đọc trong rebuild rất cao (~1 − e^(−11,5) ≈ gần 100%), nên RAID5 cỡ này là bẫy
- C. URE chỉ ảnh hưởng đĩa mới
- D. RAID5 luôn tốt hơn RAID10 về độ bền

A1.3. Service p99 tăng 40% sau khi chuyển sang máy 2 socket. Kiểm tra đầu tiên:

- A. Nâng cấp CPU
- B. Bố cục NUMA: tiến trình/thread và bộ nhớ có nằm cùng node với NIC/đĩa không
- C. Đổi ngôn ngữ lập trình
- D. Tăng timeout

A1.4. Đo `cs/s` (context switch) tăng nhanh hơn throughput khi tăng tải từ 1× lên 4×. Kết luận đúng:

- A. Cần thêm thread
- B. Đã tới trần concurrency: thêm thread sẽ làm tệ hơn; phải giảm chi phí mỗi việc hoặc tăng tỉ lệ việc/lần chặn
- C. Cần thêm RAM
- D. Lỗi kernel

### Cụm P2 — Hệ điều hành, Kernel & Cô lập

A2.1. Pod bị `OOMKilled` dù `memory.max` đặt 2 GB và heap app ~1,2 GB. Nguyên nhân khả dĩ nhất:

- A. Kernel tính sai
- B. RSS > limit vì ngoài heap còn: stack thread, page cache của chính container, arena của allocator, mmap — phải đo RSS thật chứ không nhìn heap
- C. Cần tắt swap
- D. Do CPU throttling

A2.2. Bạn cần ghi file cấu hình "không bao giờ mất" khi mất điện. Bốn bước tối thiểu là:

- A. `write` rồi `close`
- B. `write` + `fsync(file)` → `rename` → `fsync(dir)`
- C. `write` + `fsync(file)` → `rename`
- D. `write` + `fdatasync` → `copy`

A2.3. Có 5.000 kết nối TCP nhưng mỗi kết nối gần như im lặng (chat, ~1 msg/giây). Chọn mô hình:

- A. Thread-per-connection
- B. Event loop / epoll (hoặc async runtime): chi phí theo kết nối phải là vài KB, không phải 8 MB stack
- C. Process-per-connection
- D. Không quan trọng, 5.000 là ít

A2.4. Code chạy plugin của người dùng trong container cùng kernel với service chính, nhiều tenant. Đánh giá đúng:

- A. Container là ranh giới an ninh đủ mạnh
- B. Container chia sẻ kernel ⇒ một lỗ hổng kernel là thoát; với multi-tenant + code ngoài nên dùng microVM/Wasm
- C. Chỉ cần seccomp là đủ
- D. Chỉ cần chạy non-root

### Cụm P3 — Runtime ngôn ngữ & Tầng phục vụ

A3.1. Benchmark: T(1)=100 ms, T(8)=20 ms ⇒ Amdahl cho phần tuần tự s ≈ 8,6%. Ý nghĩa thực dụng:

- A. Tối ưu song song thêm sẽ vô ích; phải tấn công phần tuần tự hoặc chấp nhận trần ~11,6×
- B. Cần mua CPU nhanh hơn
- C. Đổi ngôn ngữ
- D. Số đo sai

A3.2. Số liệu thật: `json.dumps` 33,5 ms, `orjson` 2,2 ms (15,2×). Serialize chiếm 10% p99 hiện tại. Tiết kiệm p99 thực tế:

- A. 15,2×
- B. ~9% (10% × (1 − 1/15,2)) — con số này mới được hứa với sếp
- C. 0%
- D. 50%

A3.3. GOMEMLIMIT = 85% limit: GC chạy nhiều hơn, GC CPU tăng 3%, OOMKilled = 0 trong 2 tuần. Kết luận:

- A. Bỏ GOMEMLIMIT vì tốn CPU
- B. Giữ: đánh đổi 3% CPU lấy 0 OOM là đánh đổi đúng cho service có SLA; và GC CPU là chi phí thấy được, OOM là sự cố không thấy trước
- C. Đặt 100%
- D. Tắt GC

A3.4. Với 500 rps, mỗi request giữ DB connection 8 ms, retry 1,2, an toàn 1,5 ⇒ pool ≈ 7,2. Cấu hình đang là 50. Hệ quả:

- A. Không ảnh hưởng
- B. 50 kết nối chỉ tạo hàng đợi + RAM + context switch ở DB; tăng p99 chứ không tăng throughput
- C. 50 tốt hơn vì dư
- D. Cần tăng lên 100

### Cụm P4 — Giao thức, API & Hợp đồng

A4.1. Bạn bật 0-RTT cho mọi endpoint để giảm 1 RTT trên 4G. Rủi ro:

- A. Không có
- B. Replay: 0-RTT cho phép phát lại request ⇒ chỉ dùng cho GET/HEAD, hoặc POST phải có Idempotency-Key bắt buộc
- C. Chỉ chậm hơn
- D. Chỉ ảnh hưởng HTTP/2

A4.2. Client 502 chập chờn ở lưu lượng thấp. Nghi phạm số một:

- A. DNS
- B. Keep-alive: client giữ kết nối lâu hơn server (idle client ≥ idle server) ⇒ client tái dùng kết nối vừa bị đóng
- C. TLS version
- D. Thiếu CPU

A4.3. API có `additionalProperties: true` và không `required`. Fuzz 200 ca: nhiều ca gây 500. Cách chữa đúng thứ tự:

- A. Bọc try/catch trả 500 đẹp hơn
- B. Siết schema (`required`, `additionalProperties: false`) để input sai thành 400 trước khi vào logic; rồi mới xử lý các ca còn lại
- C. Chặn IP lạ
- D. Giảm tải

A4.4. 200 request/5 s từ một token, không có 429. Kết luận:

- A. Hệ khoẻ
- B. Rate limit không tồn tại hoặc đặt ở tầng không chạy; đặt bucket ở gateway theo danh tính, có burst + giới hạn ngày
- C. Cần thêm WAF
- D. 200 request là ít

### Cụm P5 — Lưu trữ, CSDL & Dữ liệu

A5.1. Bảng 100 GB, 8 index, 3 index có `idx_scan = 0` suốt 30 ngày. Hệ quả cụ thể:

- A. Không ảnh hưởng gì
- B. Mỗi INSERT/UPDATE phải ghi cả 3 index ⇒ tốn WAL + I/O; bỏ đi thường giảm 20–35% độ trễ ghi và ~25% dung lượng
- C. Chỉ tốn dung lượng
- D. Index luôn có lợi

A5.2. Cassandra: `DELETE ... WHERE pk=? AND ck < ?` xoá 10⁶ dòng. Rủi ro:

- A. Không có
- B. 10⁶ tombstone sống `gc_grace` (10 ngày) ⇒ mọi đọc trên partition đó quét qua chúng, latency bomb + timeout
- C. Chỉ tốn dung lượng
- D. Chỉ chậm một lần

A5.3. ClickHouse: INSERT trung bình 500 dòng/lần. Nguy cơ:

- A. Không có
- B. "too many parts": merge không theo kịp ⇒ insert bị từ chối; phải gom lô ≥10k hoặc `async_insert`
- C. Chỉ chậm đọc
- D. Phải tăng RAM

A5.4. RAG: gửi query với `tenant_id` của tenant khác và nhận được kết quả. Vấn đề gốc:

- A. Model yếu
- B. ACL nằm ở prompt/tầng app, không ở retrieval ⇒ filter tenant phải cưỡng bức ở tầng store, không sửa được từ client
- C. Thiếu embedding tốt hơn
- D. Chỉ là bug nhỏ

### Cụm P6 — Client, Thiết bị & Biên

A6.1. Airplane mode 60 s: 6/10 màn hình trắng hoặc loading vô hạn. Việc rẻ nhất cải thiện nhiều nhất:

- A. Xây CRDT
- B. Cache read-through + trạng thái "offline" rõ ràng ở màn hình đầu tiên (không spinner vô hạn)
- C. Thêm retry
- D. Nâng cấp backend

A6.2. 8% người dùng ở bản app > 6 tháng tuổi. Quyết định API:

- A. Bỏ hỗ trợ bản cũ ngay
- B. Ghi ngưỡng version tối thiểu vào hợp đồng API; API phải suy giảm được (không phá client cũ); chặn mềm bằng thông báo
- C. Không cần quan tâm
- D. Bắt buộc cập nhật, chặn cứng

A6.3. Sync lag p95 = 45 s khi app đang mở. Hệ quả người dùng:

- A. Chỉ chậm
- B. Người dùng "nhìn thấy quá khứ": sửa ở máy này, mở máy kia thấy dữ liệu cũ và sửa lại ⇒ mất dữ liệu âm thầm
- C. Không ảnh hưởng
- D. Tăng pin

A6.4. Đổi giá sản phẩm: DB đã mới, CDN còn 5 phút, app cache 10 phút. Cách đúng:

- A. Giảm mọi TTL xuống 1 phút
- B. Purge theo tag/surrogate key khi có sự kiện + TTL ngắn chỉ cho dữ liệu nhạy cảm về giá; kèm con số origin QPS tăng
- C. Chờ TTL hết
- D. Tắt CDN

### Cụm P7 — Web, Hiệu năng & An toàn Frontend

A7.1. TTFB 180 ms trong nước, 900 ms từ EU, render server 60 ms. Kết luận:

- A. Server chậm
- B. Phần lớn là RTT/round-trip: chữa rẻ trước (HTTP/3, session resumption, cache HTML tại CDN/edge) chứ chưa cần edge render
- C. Cần thêm CPU
- D. Do CDN

A7.2. Tắt JS: trang chủ đọc được, trang danh mục trắng. Đánh giá:

- A. Bình thường
- B. Trang danh mục là "SSR trên giấy" (SEO/chia sẻ/bền vững kém); cần SSR/streaming cho trang có nhu cầu SEO, không cần cho app sau đăng nhập
- C. Nên bỏ SSR hết
- D. Do trình duyệt

A7.3. Hệ 4 runtime production, 5 service dùng runtime nhỏ nhất. Câu hỏi đúng:

- A. Bắt buộc gộp về 2
- B. Runtime đó có "đáng một chỗ" không (thư viện độc quyền, độ trễ, talent) — nếu không viết ra được lý do thì đó là tai nạn lịch sử
- C. Không quan tâm
- D. Đổi hết sang Go

A7.4. Grep repo: 24 sink `dangerouslySetInnerHTML`/`innerHTML`, 0 justification. Hành động:

- A. Bỏ qua vì đã chạy lâu
- B. Phân loại: sink không cần (code chết, nội dung nội bộ) xoá; sink cần thì sanitize + comment nguồn tin; theo dõi số sink theo quý như metric
- C. Thêm CSP là đủ
- D. Đổi framework

### Cụm P8 — Hệ phân tán

A8.1. Dịch vụ cần "exactly-once" giữa DB và Kafka. Kết luận đúng:

- A. Bật `enable.idempotence` là đủ
- B. Không có exactly-once xuyên hai hệ: dùng outbox + consumer idempotent (khoá nghiệp vụ) — biến "exactly-once" thành "ít nhất một lần + khử trùng"
- C. Dùng 2PC
- D. Dùng retry vô hạn

A8.2. Leader bị treo 30 s (không chết). Với Raft, hệ quả:

- A. Không sao, có timeout
- B. Cluster không bầu được leader mới cho tới khi lease/timeout hết hạn; nếu hệ khác lại dựa vào lease của leader cũ ⇒ hai "chủ" cùng ghi (cần fencing token)
- C. Tự bầu ngay
- D. Mất dữ liệu

A8.3. Hai DC, cần chịu được mất 1 DC mà vẫn ghi được. Chọn:

- A. Strong consistency đồng bộ 2 DC
- B. Ghi cục bộ + đồng bộ bất đồng bộ, chấp nhận RPO > 0 và có cơ chế xung đột viết ra; hoặc quorum 2 DC nếu cần RPO=0 (đắt hơn)
- C. Chỉ cần backup
- D. Dùng một DC

A8.4. Timeout tầng ngoài 30 s, tầng trong 30 s, retry 3 lần mỗi tầng. Khi downstream chậm 30 s:

- A. Hệ tự phục hồi
- B. Bão retry nhân theo tầng (3×3 = 9 request cho 1) + tất cả chờ cùng lúc ⇒ khuếch đại sự cố; cần timeout giảm dần + ngân sách retry + circuit breaker
- C. Không ảnh hưởng
- D. Chỉ cần thêm thread

### Cụm P9 — Cloud & Nền tảng

A9.1. HPA scale theo CPU % nhưng app nghẽn ở DB. Kết quả:

- A. Scale đúng
- B. Scale pod mà không scale DB ⇒ thêm kết nối, DB càng nghẽn; phải scale theo tín hiệu gần nút cổ chai (độ trễ, hàng đợi) hoặc đặt trần + backpressure
- C. Không ảnh hưởng
- D. Cần Karpenter

A9.2. Node chứa 40 pod bị mất. Điều đáng kiểm tra trước khi coi là thảm hoạ:

- A. Số pod
- B. PodDisruptionBudget + topology spread + dung lượng dư của cụm: nếu 40 pod dồn về 30% cụm và DB không có headroom thì sự cố mới thực sự bắt đầu
- C. Log của node
- D. Version Kubernetes

A9.3. Cụm dùng NAT gateway cho toàn bộ traffic ra ngoài, hoá đơn NAT rất cao. Nguyên nhân thường gặp:

- A. Giá NAT tăng
- B. Traffic đi qua NAT (kể cả tới S3/DynamoDB trong region) do thiếu VPC endpoint/PrivateLink ⇒ dùng endpoint rẻ hơn nhiều
- C. Do DNS
- D. Do TCP

A9.4. Progressive delivery: bạn có thể bật 1% → 100% trong 10 phút, nhưng rollback cần build lại 40 phút. Vấn đề:

- A. Không có
- B. Rollback = trạng thái bạn phải đo được; nếu > MTTR mục tiêu thì thực chất không có rollback, chỉ có "phát hành lại và hy vọng"
- C. Cần thêm test
- D. Cần canary lâu hơn

### Cụm P10 — An ninh

A10.1. Hệ dùng Zero Trust "vì đã có mTLS giữa mọi service". Thiếu gì?

- A. Không thiếu
- B. Authorization theo danh tính workload (SPIFFE/policy) + kiểm soát egress: mTLS chứng minh "ai", không nói "được làm gì"
- C. Cần VPN
- D. Cần WAF

A10.2. Ứng dụng lưu secret trong biến môi trường của pod, secret xoay mỗi 90 ngày bằng tay. Rủi ro chính:

- A. Env var không an toàn tuyệt đối nhưng vấn đề lớn hơn là xoay tay: 90 ngày × N service = có lần trễ ⇒ hoặc secret chết, hoặc không xoay
- B. Không có rủi ro
- C. Chỉ cần mã hoá etcd
- D. Chỉ cần RBAC

A10.3. OWASP Top 10:2025 đặt Supply Chain ở A03. Việc tương ứng bắt buộc:

- A. Chỉ quét lỗ hổng dependency
- B. SBOM + ký artifact + verify lúc deploy (SLSA) + chặn dependency không pin; quét CVE chỉ là một phần
- C. Chỉ cần Dependabot
- D. Chỉ cần review code

A10.4. CRA (EU) — nghĩa vụ báo cáo lỗ hổng đang bị khai thác có hiệu lực từ 11/09/2026. Việc cần làm ngay:

- A. Không liên quan nếu không bán ở EU
- B. Xác định sản phẩm thuộc phạm vi, dựng quy trình báo cáo 24 h/72 h + đầu mối liên hệ + kênh nhận báo cáo từ bên ngoài
- C. Chờ tới 2027
- D. Chỉ cần cập nhật chính sách

### Cụm P11 — Vận hành, SRE, Kinh tế

A11.1. SLO 99,9%/30 ngày = 43,2 phút. Một deploy hỏng mất 45 phút. Kết luận:

- A. Chuyện nhỏ
- B. Đã tiêu 104% ngân sách ⇒ đúng một sự cố như vậy là hết tháng; do đó canary + rollback nhanh không phải nghi thức mà là điều kiện của SLO
- C. Tăng SLO lên 99,95%
- D. Bỏ SLO

A11.2. p99 = 497 ms sau khi bơm sự cố 350 ms/request. Điều đáng nhớ:

- A. p99 là số chính xác
- B. `histogram_quantile` nội suy trong bucket ⇒ p99 phụ thuộc biên bucket, không phải giá trị đo; và alert có `for: 15s` trễ thêm
- C. Nên dùng trung bình
- D. p99 luôn sai

A11.3. FinOps: 40% hoá đơn là data transfer giữa AZ. Hành động đúng:

- A. Mua thêm băng thông
- B. Giảm traffic xuyên AZ: đặt consumer cạnh dữ liệu, cache cục bộ, gộp request — hoặc chấp nhận và ghi vào ADR
- C. Chuyển sang multi-cloud
- D. Không làm gì

A11.4. Postmortem ghi "nguyên nhân: kỹ sư chạy sai lệnh". Thiếu gì?

- A. Không thiếu
- B. Nguyên nhân hệ thống: vì sao một lệnh sai lại có thể chạy trên production (thiếu guardrail, thiếu dry-run, thiếu quyền tối thiểu) — người là triệu chứng, hệ thống là nguyên nhân
- C. Cần kỷ luật
- D. Cần thêm tài liệu

### Cụm P12 — AI & Mô hình

A12.1. int4 làm decode nhanh gấp đôi trên GPU nhưng SLA là "một người dùng thấy phản hồi nhanh". Kết luận:

- A. int4 luôn tốt hơn
- B. Ở batch = 1, decode nghẽn băng thông bộ nhớ ⇒ int4 giúp thật; nhưng khi tăng batch, nghẽn dời sang compute và KV cache (128 KiB/token) ⇒ phải đo lại, không suy từ bảng
- C. int4 luôn tệ hơn
- D. Không liên quan

A12.2. RAG trả lời sai nhưng context chứa đúng thông tin. Nghi phạm đầu tiên:

- A. Model yếu
- B. Thứ tự/khối lượng context: thông tin đúng nằm giữa "lost in the middle", hoặc bị cắt do vượt ngân sách token — sửa context engineering trước khi đổi model
- C. Cần fine-tune
- D. Cần agent

A12.3. Agent dùng MCP, công cụ trả về 2 MB text. Rủi ro:

- A. Không có
- B. Ngân sách context bị chiếm + chi phí token tăng vọt + model suy giảm chất lượng; phải cắt/khoanh vùng kết quả ở tầng công cụ
- C. Chỉ chậm
- D. Cần GPU lớn hơn

A12.4. Bạn định đổi model để "tốt hơn". Điều kiện tiên quyết:

- A. Benchmark công khai
- B. Eval set nội bộ + baseline + tiêu chí (độ chính xác, chi phí, độ trễ) — không có ba thứ đó thì "tốt hơn" là ý kiến
- C. Chạy thử vài prompt
- D. Hỏi cộng đồng

### Cụm P13 — Playbook theo miền

A13.1. Sổ cái thanh toán: chọn DB theo "cần strong consistency". Cách đúng hơn:

- A. Chọn DB nổi tiếng nhất
- B. Xác định bất biến nghiệp vụ (không âm quỹ, không ghi kép), rồi chọn cơ chế: giao dịch + khoá hoặc event-sourcing có idempotency; DB chỉ là phương tiện
- C. Dùng NoSQL cho nhanh
- D. Dùng cache

A13.2. Lớp tải realtime: 100k kết nối, cần gửi sự kiện có thứ tự trong 1 phòng. Chọn:

- A. WS broadcast không trạng thái
- B. Có "phòng" giữ thứ tự (một actor/partition/phòng), resume token để không mất sự kiện khi reconnect
- C. Polling 1 s
- D. SSE cho mọi thứ

A13.3. Multi-tenant SaaS: tenant lớn nhất chiếm 40% tải, đang dùng chung pool. Rủi ro:

- A. Không có
- B. "Hàng xóm ồn": tenant lớn làm sập trải nghiệm tenant khác và mất khả năng cô lập/định giá; cần escape hatch (silo) đã diễn tập
- C. Chỉ cần autoscale
- D. Tăng quota

A13.4. Analytics: cần query ad-hoc trên 300 GB parquet nội bộ, 5 analyst. Kiến trúc tối thiểu đủ dùng:

- A. Cluster Spark 20 node
- B. DuckDB/Trino một node trên object storage — đo trước, chỉ lên cluster khi vượt ngưỡng
- C. Data warehouse đắt nhất
- D. Excel

### Cụm P14 — Biên giới

A14.1. Vòng điều khiển 100 Hz: `sleep(10ms)` trong vòng lặp vs lịch tuyệt đối. Khác biệt đo được:

- A. Không khác
- B. `sleep` cộng dồn sai số (~180 ms sau 3.000 nhịp), lịch tuyệt đối giữ trễ p99 ~0,2 ms; và dưới tải, p50 tốt lên nhưng max xấu đi 13× ⇒ phải nhìn max/WCET
- C. sleep chính xác hơn
- D. Chỉ khác khi bật RTOS

A14.2. Hai lần build cùng source, cách nhau 2 giây, khác hash. Nguyên nhân phổ biến nhất và cách chặn:

- A. Trình biên dịch lỗi
- B. `__DATE__`/`__TIME__` (và đường dẫn tuyệt đối) nhúng vào binary ⇒ `SOURCE_DATE_EPOCH` + đường dẫn ảo cố định (`-ffile-prefix-map`)
- C. Do ổ đĩa
- D. Do phiên bản gcc

A14.3. WASI 0.3 đưa async vào canonical ABI. Hệ quả kiến trúc cho plugin:

- A. Không có
- B. Host sở hữu event loop; interface nên thô (batch, vùng nhớ chia sẻ) vì chi phí nằm ở biên giới, không ở CPU
- C. Plugin phải viết lại bằng Rust
- D. Bỏ WASM

A14.4. OWASP/chuẩn mới liên tục đổi. Cách duy nhất giữ tài liệu không phân rã:

- A. Viết lại mỗi năm
- B. Cơ chế: ledger có nguồn + ngày kiểm + cổng tự động (freshness) + ERRATA công khai — "đúng" là một quá trình, không phải một lần viết
- C. Thuê chuyên gia đọc lại
- D. Không cần, chuẩn ít đổi

## Đáp án & giải thích


| Câu | Đáp án | Vì sao (2 dòng) |
|---|---|---|
| A0.1 | B | Hai bên thường khác trục, không khác sự thật; 7 trục biến cãi thành đo (0.1) |
| A0.2 | B | Replication trả lời "mấy bản", không trả lời "mất gói/partition" (A3) hay "hỏng âm thầm" (A4) |
| A0.3 | B | Ô "Chẩn" trống = việc vẫn phải làm nhưng không ai sở hữu; rủi ro đã tồn tại, chỉ chưa được gán (0.3) |
| A0.4 | B | ERRATA + lịch soát là cơ chế; sửa số đơn lẻ để lại đúng lỗi đó ở 40 chỗ khác (0.4) |
| A1.1 | D | Phân mảnh đĩa gần như không đổi theo số lõi; A/B/C đều là hiệu ứng scale-out (1.2, 1.3) |
| A1.2 | B | Rebuild RAID5 đọc toàn bộ đĩa còn lại: λ ≈ 11,5 ⇒ xác suất sạch ≈ e^−11,5 ≈ 10⁻⁵ (1.4) |
| A1.3 | B | 2 socket ⇒ bộ nhớ có thể nằm node xa NIC/đĩa; pin/membind là bước kiểm rẻ nhất (1.3) |
| A1.4 | B | `cs` tăng nhanh hơn throughput = thời gian đang đi vào chuyển ngữ cảnh, không vào việc (2.3) |
| A2.1 | B | Limit áp lên RSS, không lên heap; stack thread + arena + mmap + page cache đều tính (2.1) |
| A2.2 | B | Thiếu `fsync(thư mục)` thì tên file mới có thể chưa tồn tại sau mất điện (2.4) |
| A2.3 | B | 5.000 kết nối im lặng: chi phí/kết nối phải là KB, không phải stack MB (2.5) |
| A2.4 | B | Container chung kernel; multi-tenant + code ngoài ⇒ cần ranh giới kernel (microVM/Wasm) (2.7) |
| A3.1 | A | s ≈ 8,6% đặt trần ~11,6×; tối ưu song song thêm không vượt được (3.1) |
| A3.2 | B | Δp99 ≈ 10% × (1 − 1/15,2) ≈ 9%; hứa 15× là hứa sai đơn vị (3.11) |
| A3.3 | B | GC CPU là chi phí thấy trước; OOM là sự cố không thấy trước (3.4) |
| A3.4 | B | Pool lớn hơn Little chỉ tạo hàng đợi tại DB + RAM + context switch (3.10) |
| A4.1 | B | 0-RTT cho phép replay; chỉ GET/HEAD, hoặc POST kèm Idempotency-Key bắt buộc (4.1) |
| A4.2 | B | Idle client ≥ idle server ⇒ tái dùng kết nối server vừa đóng ⇒ 502 chập chờn (4.2) |
| A4.3 | B | Siết schema biến input sai thành 400 trước logic; try/catch chỉ che triệu chứng (4.3) |
| A4.4 | B | Không 429 ⇒ không có rate limit thật; đặt theo danh tính ở gateway (4.8) |
| A5.1 | B | Mỗi index là một lần ghi; index không dùng chỉ là thuế (5.1) |
| A5.2 | B | Tombstone sống `gc_grace` ⇒ mọi đọc partition quét qua chúng (5.5) |
| A5.3 | B | Block nhỏ ⇒ quá nhiều part ⇒ insert bị từ chối khi merge không kịp (5.8) |
| A5.4 | B | ACL ở prompt là ACL có thể bị bỏ qua; phải cưỡng bức ở retrieval (5.10) |
| A6.1 | B | Cache + trạng thái offline rõ ràng sửa phần lớn cảm nhận, không cần CRDT (6.1) |
| A6.2 | B | Cửa sổ compatibility là số đo, và API phải suy giảm được cho client cũ (6.1) |
| A6.3 | B | Lag 45 s ⇒ người dùng sửa lại trên dữ liệu cũ ⇒ mất dữ liệu âm thầm (6.3) |
| A6.4 | B | Purge theo tag + TTL ngắn cục bộ, kèm số QPS origin — TTL toàn hệ là khuếch đại tải (6.5) |
| A7.1 | B | 900 − 60 ms chủ yếu là round-trip; chữa RTT trước, edge render sau (7.1) |
| A7.2 | B | "SSR trên giấy" = server chỉ trả khung; cần SSR cho trang có nhu cầu SEO (7.1) |
| A7.3 | B | Runtime nhỏ phải biện hộ được bằng một đoạn văn, không bằng quán tính (3.9) |
| A7.4 | B | Phân loại sink + sanitize + metric theo quý; CSP là lớp thứ hai, không phải cách sửa (7.7) |
| A8.1 | B | Outbox + consumer idempotent: biến exactly-once thành at-least-once + dedupe (8.3) |
| A8.2 | B | Leader treo ≠ leader chết; lease cũ + hai chủ ⇒ cần fencing token (8.2) |
| A8.3 | B | Chọn theo RPO/RTO, không theo khẩu hiệu "strong consistency" (8.7) |
| A8.4 | B | Timeout bằng nhau + retry mỗi tầng = khuếch đại 9× khi downstream chậm (8.5) |
| A9.1 | B | Scale theo tín hiệu gần nút cổ chai; scale pod khi DB nghẽn làm mọi thứ tệ hơn (9.2) |
| A9.2 | B | Câu hỏi là cụm còn headroom và PDB/topology spread có đúng không (9.2, 9.4) |
| A9.3 | B | Thiếu VPC endpoint ⇒ traffic nội region đi qua NAT (9.3) |
| A9.4 | B | Rollback là trạng thái phải đo; nếu chậm hơn MTTR mục tiêu thì không tồn tại (9.7) |
| A10.1 | B | mTLS trả lời "ai", không trả lời "được làm gì"; thiếu authz + egress (10.1) |
| A10.2 | A | Vấn đề hệ thống là xoay tay: quy mô × 90 ngày ⇒ sẽ có lần trễ (10.6) |
| A10.3 | B | Supply chain = SBOM + ký + verify + pin, không phải chỉ quét CVE (10.5) |
| A10.4 | B | Nghĩa vụ báo cáo 24 h/72 h đã có hiệu lực 11/09/2026 với sản phẩm trong phạm vi (10.8) |
| A11.1 | B | 45 phút = 104% ngân sách tháng ⇒ canary/rollback là điều kiện của SLO (11.1) |
| A11.2 | B | `histogram_quantile` nội suy trong bucket; `for: 15s` thêm trễ cảnh báo (11.2) |
| A11.3 | B | Data transfer xuyên AZ là quyết định vị trí, không phải băng thông (11.5) |
| A11.4 | B | Người là triệu chứng; thiếu guardrail là nguyên nhân (11.4) |
| A12.1 | B | Batch=1 nghẽn băng thông (int4 giúp); batch lớn nghẽn compute + KV cache (12.2) |
| A12.2 | B | Context đúng nhưng bị chôn/cắt ⇒ sửa context engineering trước khi đổi model (12.3) |
| A12.3 | B | Kết quả công cụ phải được cắt ở tầng công cụ, không đẩy vào context (12.4) |
| A12.4 | B | Không có eval + baseline thì "tốt hơn" là ý kiến (12.5) |
| A13.1 | B | Bất biến nghiệp vụ trước, cơ chế sau, DB sau cùng (13.1) |
| A13.2 | B | Thứ tự trong phòng cần một "chủ" (actor/partition) + resume token (13.2) |
| A13.3 | B | Hàng xóm ồn là rủi ro kiến trúc, không phải rủi ro vận hành (13.7) |
| A13.4 | B | 300 GB / 5 analyst: đo bằng một node trước khi dựng cluster (13.4) |
| A14.1 | B | `sleep` cộng dồn sai số; dưới tải p50 tốt lên nhưng max xấu 13× (14.7.2) |
| A14.2 | B | `__DATE__`/`__TIME__` + đường dẫn tuyệt đối là hai nguồn lệch phổ biến nhất (14.8.1) |
| A14.3 | B | Chi phí nằm ở biên giới ⇒ interface thô, batch, vùng nhớ chia sẻ (14.2) |
| A14.4 | B | "Đúng" là quá trình: ledger + ngày kiểm + cổng + ERRATA (0.4, 14.8.1) |
Cách tự chấm: đếm số đúng theo cụm. 4/4 ⇒ cụm đã qua. 3/4 ⇒ đọc lại § ghi ở câu sai rồi làm lại câu đó sau 48 giờ. ≤2/4 ⇒ quay lại lab của cụm: kiến thức này chưa thành kỹ năng.
