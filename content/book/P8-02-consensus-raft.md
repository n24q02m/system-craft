# 8.2 — Đồng thuận (Raft/Paxos), Leases & Fencing Tokens

> **Tầng:** Lõi phân tán · **Quyển II** · **Trục đọc:** lý thuyết vận hành hoá · **Động từ liên quan:** Chọn · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 8.1 (FLP, CAP — nền) · 5.7 (đã gặp KRaft).

**Sợi chỉ đỏ:** *Muốn một sự thật chung — đồng thuận kiểu Raft đánh đổi gì để có nó?* — trả lời: muốn một sự thật chung trong cụm máy chết được — Raft bầu leader theo term, ghi log nhân bản tới quorum; cái giá là một vòng quorum mỗi lần ghi và kỷ luật member; kèm lease, fencing token — và hẳn mục "khi nào KHÔNG cần" vì đồng thuận đắt. Câu hỏi để lại cho chương sau: *Một giao dịch chạm nhiều service — saga và outbox thay 2PC thế nào?*

**Thuật ngữ sẽ gặp:** *quorum* — đa số N/2+1: chấp nhận thiểu số máy chết mà vẫn quyết định được; *term* — "nhiệm kỳ" bầu cử của Raft: term cao luôn thắng term thấp; *lease* — thuê quyền leader trong thời hạn định trước: hết hạn là bầu lại, đừng tin mãi mãi; *fencing token* — số tăng đơn điệu gắn mỗi quyền: node chậm tới mà vẫn tưởng mình là leader sẽ bị token thấp vô hiệu; *ba sản phẩm chạy sẵn* — etcd, Consul, ZooKeeper: đừng tự viết Raft cho sản phẩm; *KRaft* — Kafka tự gộp Raft vào: đã lướt qua ở 5.7.

**Ví dụ mở đầu:** Việc "ai gán shipper cho đơn" của DM cần đúng một quyết định tại một thời điểm. Tự chế bằng khoá trong DB: mạng chia đôi, hai bên cùng nghĩ mình giữ khoá — split-brain. Raft trả câu hỏi bằng bầu cử theo term; fencing token dẹp nốt thằng lagging vẫn tự xưng leader. Chương này đọc Raft như một đoạn code 100 dòng.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Có thật sự cần đồng thuận không | Tôi cần một giá trị **toàn hệ thống** thống nhất — hay chỉ cần lock để đỡ tranh nhau? |
| 2 | Nếu cần: dùng hệ đồng thuận chạy sẵn (etcd/ZooKeeper/Consul) hay tự nhúng (Raft library) | Ai trực nhật hệ này 3 năm tới? |
| 3 | Lock phân tán dùng cho **hiệu năng** hay cho **tính đúng đắn** | Sai một lần lock — mất dữ liệu hay chỉ làm lại công việc? |
| 4 | Fencing token có hay không (và ai kiểm tra nó) | Node "ngủ quên" (GC pause) quay lại — ai chặn nó đè dữ liệu mới? |

---

## 2. Cơ chế

### 2.1 Đồng thuận giải bài gì

N máy, một số chết/mạng chia, vẫn phải **thống nhất một giá trị/thứ tự** (leader, config, lock ownership). Raft/Paxos trả lời: một giá trị được chấp nhận khi **đa số** node ghi nhận (N=3 chịu 1 lỗi; N=5 chịu 2). Hai hệ quả phải thuộc:
- Quorum = **đa số** → hai nhóm thiểu số không thể cùng "thắng" (không split-brain về giá trị);
- Cluster chỉ tiến khi **đa số sống + liên lạc được** — mất 2/5 node là cluster dừng ghi (không phải "chậm lại" mà là **dừng**).

### 2.2 Raft trong 100 dòng khái niệm

Leader bầu theo **term** (đại số tăng dần); mọi ghi qua leader, leader sao chép log sang follower, **commit khi đa số ghi** rồi báo cho mọi node. An toàn từ bất biến: term + log index. Vận hành: **election timeout phải ≥ vài lần RTT chéo node** (khuyến nghị ~10×, I) — vi phạm là leader flap (I-054). Paxos cùng kết luận bằng con đường khác (đúng hơn, khó cài hơn — Multi-Paxos ≈ Raft về hiệu năng khi tối ưu; thực tế mới chọn Raft vì dễ hiểu/dễ cài).

### 2.3 Ba sản phẩm chạy sẵn

| | **etcd** | **ZooKeeper** | **Consul** |
|---|---|---|---|
| Gốc | CoreOS/CNCF | Apache (Hadoop hệ sinh thái) | HashiCorp |
| Thuật toán | Raft | ZAB (họ Paxos) | Raft |
| Mô hình dữ liệu | KV phẳng + watch (prefix) | znode cây + watch | KV + catalog + service discovery DNS |
| Ngôn ngữ/DB | Go | Java | Go |
| Thường thấy | Kubernetes control plane | Kafka (đang thay bằng KRaft) | Service mesh/multi-DC |

Cả ba đều: session + TTL (máy chết → node biến mất sau TTL), watch (biến đổi đẩy tới), và **đều không tự cho bạn tính đúng đắn** — chỉ cho bạn nguyên liệu (lock + token) — việc dùng đúng là của bạn (§2.5).

### 2.4 Lease — "thuê thời gian"

Leader/lock có **hạn**: node A giữ lease 15 s, gia hạn liên tục; hết hạn mà không gia hạn → quyền rơi, node khác nhận. Lease biến "node chết" thành bài toán **thời gian** (không cần phát hiện chết tức thời). Nhưng lease dựa trên **đồng hồ** (→8.1): nếu node giữ lease bị **stop-the-world GC 30 s** trong khi lease 15 s: nó tỉnh dậy **vẫn tưởng mình giữ quyền** — hai "người thắng" cùng tồn tại (I-055). Đây là lý do tồn tại fencing.

### 2.5 Fencing token — số đơn điệu

Lock service cấp kèm **token tăng dần** (2, 3, 4...); storage/đối tượng bị bảo vệ **kiểm tra token**: yêu cầu mang token nhỏ hơn token đã thấy = từ chối. Node cũ (GC tỉnh dậy, mạng chậm) cầm token 3 không đè được node mới cầm token 4. Ba điều kiện sống còn: (1) token **đơn điệu toàn cục** cho khoá đó; (2) **phía lưu trữ phải kiểm** (thiếu chỗ này = token trang trí — lỗi số một của tự làm); (3) kho lưu trữ tự ghi nhớ token mới nhất từng thấy (ít nhất cho khoá đang bảo vệ). Kafka dùng epoch cho txn producer — cùng tư tưởng.

### 2.6 Khi nào KHÔNG cần đồng thuận

- Chỉ cần **giảm tranh nhau** (idempotent worker): random delay + claim là đủ — sai thì làm lại;
- Single writer cho khoá + hàng đợi: giao bài toán cho queue (→5.7);
- Cấu hình tĩnh, ít đổi: file + restart, đừng nuôi cluster đồng thuận để đọc config;
- Đồng thuận là hạ tầng **đắt để vận hành** (backup, nâng cấp, monitoring riêng) — chỉ thật sự cần khi "hai giá trị cùng tồn tại" là **thiệt hại nghiệp vụ lớn" (leader bầu, chọn primary DB, phân phối việc).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Quorum | đa số (N=3 chịu 1; N=5 chịu 2) | V | |
| Election timeout | ~10× RTT chéo node | I | khuyến nghị Raft |
| etcd write throughput | ~vài nghìn ops/s (khối nhỏ) | I | không phải DB chính |
| Kafka KRaft | thay ZooKeeper hoàn tất (3.x–4.x) | V | 2024+ |
| Lease điển hình | 10–30 s, gia hạn 1/3 | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Đồng thuận mua **tính đúng đắn của một quyết định** với giá: cluster riêng + mất đa số = dừng — chỉ dùng cho số lượng nhỏ quyết định sinh tử (leader, lock, config); dữ liệu nghiệp vụ đi DB/queue.
- **S2:** Tham số trụ: term/leader thay đổi theo tuần, quorum latency p99, số lock holder bị từ chối vì fencing (không = 0 là cảnh báo).
- **S3:** Lease đổi độ trễ phát hiện chết lấy đơn giản; fencing đổi một bước kiểm tra ở storage lấy tính đúng đắn tuyệt đối cho lock — hai kỹ thuật đi cặp, không thay nhau.
- **S4:** Watch/notify của etcd/ZK là **cấu trúc dữ liệu nền** của control plane hiện đại (K8s, service mesh) — hiểu chương này = hiểu nửa nền tảng ở P9.
- **S5:** Đồng thuận "managed" (cloud lock table, managed etcd) giảm vận hành nhưng fencing vẫn là trách nhiệm **caller-storage** — không có SaaS nào "sửa giúp" node ngủ quên (thiết kế bài toán, không phải dịch vụ).
- **S6:** Khi có hai node cùng "tin mình là chủ": đó không phải bug hiếm — đó là **kịch bản đã được dự đoán** (GC/lease/mạng); nếu kiến trúc không trả lời được "ai chặn cái nào" bằng fencing thì sự cố chỉ chưa tới.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Leader flap liên tục (I-054) | RTT chéo node > election timeout | ping chéo node; tăng timeout | §2.2 |
| Dữ liệu bị ghi đè "bởi ma" (I-055) | GC pause + lease hết hạn, thiếu fencing | GC log + audit token | §2.4–2.5 |
| Hai primary cùng nhận ghi (I-053) | Split-brain do fencing thiếu ở storage | kiểm tra storage có verify token | §2.5 |
| Cluster "đông cứng" không ghi | Mất đa số (2/5 node) | quorum status | §2.1 |
| Watch chậm/lost | Session hết hạn giữa chừng | keepalive; watch lại từ revision | §2.3 |
| etcd full / chậm | Dùng làm DB nghiệp vụ | chuyển sang DB thật (→5.x) | §2.6 |

---

## 6. Cách đo

```bash
# etcd: sức khoẻ quorum + leader ổn định
etcdctl endpoint status -w table   (xem leader, term, raftIndex)
etcdctl endpoint health

# Kịch bản "ngủ quên" — tái lập an toàn ở staging:
#   1. process A giữ lock; 2. pause nó (kill -STOP); 3. đợi lease hết;
#   4. process B lấy lock + ghi; 5. CONT process A — nó có ghi đè không?
#   Nếu có: fencing không có/không được kiểm — sửa trước khi production dạy bạn
```

Nguyên tắc: **mọi lock phân tán phải qua bài test "STOP–CONT"** ở trên; qua được mới được gọi là lock đúng đắn, không qua được là "gợi ý lịch trình".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự vận hành etcd/ZK:** dùng managed K8s/managed lock (thuê người trực) — hợp lệ; **thay lock phân tán:** single-writer queue (→5.7) hoặc optimistic concurrency (version column — DB từ chối ghi cũ) — thường rẻ và đủ, fencing tự nhiên theo version.

Năm thấu kính:
- **Kinh tế:** Cluster đồng thuận là ~3–5 máy + kỹ năng vận hành hiếm; nếu nó chỉ phục vụ một use case nhỏ, hóa đơn per-use-case kinh khủng — gom use case hoặc bỏ.
- **Vận hành:** Backup etcd/ZK là **nghệ thuật riêng** (snapshot + member restore) — drill định kỳ; mất cluster này mà không khôi nổi = mất cả K8s/control plane.
- **An ninh:** Control plane này là mục tiêu giá trị nhất (ai cầm lock/config cầm hành vi toàn hệ) — ACL/mTLS + audit log mọi thao tác; bỏ ngỏ = chiếm giữa chừng không ai biết.
- **Lịch sử:** Paxos (1990, "nổi tiếng khó hiểu") → Chubby/ZAB (2000s, Google nội bộ) → Raft (2014, "understandable by design") → KRaft (Kafka bỏ ZK, 2020s): 30 năm nỗ lực làm cho đúng đắn trở nên **học được** — mỗi thế hệ dễ dùng hơn và phổ biến hơn (đúng theo chu kỳ của 7.1).
- **Người dùng:** Người dùng không thấy đồng thuận — họ thấy "không bao giờ có hai hóa đơn cùng số" hoặc "đèn điều khiển không xanh hai hướng cùng lúc". Đồng thuận là kỹ thuật đứng sau những cam kết "không bao giờ" đó.

---

## 8. Đọc tiếp & bài tập

- Thời gian & giới hạn: **8.1** · Giao dịch phân tán: **8.3** · K8s control plane (etcd thật): **9.1** · Kafka/KRaft: **5.7** · Queue single-writer: **5.7**
- **Bài tập 1:** Liệt kê mọi lock/leader election trong hệ thống bạn. Mỗi cái trả lời: lease TTL? fencing? ai kiểm token? Bảng này thường trống — và mỗi ô trống là một sự cố tương lai.
- **Bài tập 2:** Chạy kịch bản STOP–CONT (§6) với lock của bạn. Ghi lại kết quả; nếu bị đè — đó là 10 phút đáng giá nhất tháng này.
- **Bài tập 3:** Đo RTT chéo node của cluster đồng thuận bạn; so với election timeout. Tỉ lệ < 5×? Đang mời leader flap (I-054).
