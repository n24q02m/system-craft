# P15-05 — Ma trận Ranh giới Kỹ thuật: Khi nào SAI & Ba Ngưỡng Quy mô

> **Tầng học mở rộng** · Đọc kèm [11.5 (Kinh tế học Kỹ thuật & FinOps)](./P11-05-finops.md), [13.7 (Playbook B2B SaaS)](./P13-07-saas-b2b.md) và [P15-00 (Cách dùng tầng học)](./P15-00-tang-hoc-cach-dung.md).
> **Trạng thái:** VIẾT XONG · Không có giải pháp "tốt nhất mọi lúc" — mọi lựa chọn kiến trúc đều là một hợp đồng ngắn hạn có ngưỡng gãy rõ ràng.

---

## 1. Vì sao phải học "Khi nào SAI" trước khi học "Cách cài"?

Phần lớn nợ kỹ thuật không đến từ chọn công nghệ lỗi thời, mà từ **bê đúng giải pháp ở quy mô `Enterprise` về cài cho `Startup`**, hoặc ngược lại: **giữ thói quen `Startup` qua điểm uốn `Scale-up`**. Chương này đóng gói 12 đường ranh giới hay chọn nhầm nhất của toàn bộ 145 chương thành hai công cụ tra nhanh: bảng **Khi nào SAI** và ma trận **3 ngưỡng quy mô (`Startup` · `Scale-up` · `Enterprise`)**.

---

## 2. Mười hai Đường Ranh giới Phổ biến & Điểm "Khi nào SAI"

| # | Lựa chọn hay bị thổi phồng | Dùng ĐÚNG khi | Khi nào SAI (Anti-pattern & Hậu quả) | Chương neo |
|---:|---|---|---|---|
| 1 | **Microservices sớm** | Nhiều miền nghiệp vụ độc lập, > 4–6 squad deploy lệch nhịp | **Team < 15 kỹ sư**, boundary miền còn đổi mỗi tuần → nhân gấp đôi hop mạng (`0.5 ms` thành nhiều lần), phân tán giao dịch trước khi hiểu miền | `8.6`, `11.6`, `1.1` |
| 2 | **Kafka / Flink thay queue đơn giản** | Cần replay log nhiều consumer, throughput > `50k msg/s` hoặc CDC/Outbox dài ngày | Chỉ cần hàng đợi job nền `50–500 msg/s` → vác thêm ZooKeeper/KRaft, rebalance storm (`I-043`), chi phí ops ăn hết thời gian product | `5.7`, `5.12`, `5.15` |
| 3 | **Sharding DB thủ công** | 1 primary write đã chạm trần IOPS/WAL hoặc > `10 TB` bảng nóng không tách lạnh được | Đọc còn đang nghẽn vì **thiếu index / N+1 query (`I-040`)**, dữ liệu < `1 TB` → tự chặt mất `JOIN` & `ACID` đơn giản | `5.2`, `8.4`, `5.16` |
| 4 | **Cache phân tán (Valkey/Redis) mặc định mọi endpoint** | Tỷ lệ đọc/ghi > `20:1`, tính lại tốn > `10 ms` hoặc khoá nóng cục bộ | Thêm cache cho dữ liệu vừa sửa vừa đọc, TTL sai → stale read, cache stampede (`I-033`) sập luôn DB khi cache restart (`I-052`) | `5.4`, `8.5` |
| 5 | **Multi-region Active-Active** | RPO ~ 0 xuyên lục địa, traffic toàn cầu thật sự có quy định cư trú dữ liệu địa phương | Người dùng tập trung 1 vùng, chưa làm nổi DR Active-Passive chuẩn → viết đa vùng không vector clock/consensus gây split-brain (`8.2`), RTT ghi tăng `50–150 ms` | `8.1`, `8.2`, `8.7` |
| 6 | **Kubernetes + Service Mesh (mTLS Istio) ngay từ đầu** | Hàng chục service, cần bin-packing/GPU scheduling, squad platform chuyên trách > 2 người | < 5 service trên 2–3 VM → YAML phức tạp, `ndots:5` nhân 5 truy vấn DNS (`I-061`), CPU proxy sidecar ngốn 15–30% compute | `9.1`, `9.3`, `9.4` |
| 7 | **Vector DB chuyên dụng tách rời từ ngày 1** | > `10M` vector, lọc metadata phức tạp, QPS tìm kiếm ngữ nghĩa > `500/s` | Kho tri thức RAG < `500k` chunks → `pgvector` HNSW trên Postgres sẵn có vừa đủ, lại tránh lệch đồng bộ dual-write (`I-045`) & rò ACL (`I-068`) | `5.10`, `12.3`, `12.5` |
| 8 | **Tự host vLLM/SGLang mọi model** | Traffic ổn định lấp > `50–60%` công suất GPU 24/7, cần residency/compliance nội bộ | Traffic giật cục vài giờ cao điểm → GPU rảnh vẫn trả tiền thuê theo giờ, TTFT tăng vì queueing/cold-start (`I-066`) đắt hơn API Gateway theo token | `12.2`, `12.6`, `1.5` |
| 9 | **Sync RPC chuỗi dài trên đường người dùng** | Nghiệp vụ thực sự đòi kết quả tức thì ở `p99 < 200 ms` | Chuỗi A → B → C → D đều đồng bộ → tổng lỗi nhân chéo, retry storm (`I-050`) đánh sập dây chuyền (`I-051`) khi 1 mắt xích chậm nhẹ | `1.1`, `4.8`, `8.5` |
| 10 | **NoSQL Wide-Column (Cassandra/Scylla) cho dữ liệu quan hệ** | Write-heavy theo partition key cố định, multi-DC AP với SLA vài ms | Truy vấn ad-hoc nhiều chiều, `DELETE` liên tục sinh tombstone (`I-035`) → chậm dần theo thời gian, dev tự viết lại join ở tầng app | `5.5`, `5.15` |
| 11 | **GraphQL Federation / BFF phức tạp quá sớm** | Nhiều client khác hẳn payload, nhiều team backend độc lập sở hữu subgraph | 1 app web + 1 backend team → mở cửa N+1 ẩn (`I-040`), mất cache HTTP đơn giản, khó rate limit theo độ sâu query | `4.3`, `4.5`, `4.8` |
| 12 | **Mật mã biên giới (FHE/ZK) & TEE khi chưa vá lớp nền** | Yêu cầu tính toán trên dữ liệu mã hoá (FHE/MPC) hoặc attestation phần cứng không tin cậy host (TEE) | Bỏ ngỏ TLS, RBAC/ReBAC, secret scanning (`I-063`) & JWT revocation (`I-064`) → trả `10–1000×` overhead vô ích trong khi bị đánh sập qua SSRF (`I-065`) | `1.8`, `10.3`, `10.4`, `14.10.3` |

---

## 3. Ba Ngưỡng Quy mô: `Startup` · `Scale-up` · `Enterprise`

Dùng bảng này khi rà soát kiến trúc (cũng là khung quyết định cho `13.1`–`13.7` và `11.5`):

| Trục | **Startup** (`1–15` kỹ sư · `< 50k MAU` · `< 200 RPS`) | **Scale-up** (`15–120` kỹ sư · `50k–5M MAU` · `200–10k RPS`) | **Enterprise** (`> 120` kỹ sư · `> 5M MAU` · `> 10k RPS` / compliance chặt) |
|---|---|---|---|
| **Kiến trúc & Deploy** | Modular Monolith trên 2 VM / PaaS; Compose / systemd; Zero k8s nếu chưa cần | Tách 3–8 dịch vụ theo boundary ổn định; Managed K8s + GitOps (`9.6`) + HPA/Karpenter (`9.2`) | Cell-based architecture (`8.7`) cô lập blast radius (`I-056`); Platform IDP (`9.6`); Multi-region DR định kỳ chaos (`11.3`) |
| **Cơ sở dữ liệu** | 1 Managed PostgreSQL Primary + Backup PITR (`5.2`), pgvector cho RAG nhỏ | Primary + Read Replicas + Connection Pooler (`PgBouncer`), partitioning bảng lớn, tách OLAP sang DuckDB/ClickHouse (`5.8`) | Sharding theo tenant/key (`8.4`), Iceberg v3 lakehouse (`5.9`), DAMA lineage & PII governance (`5.13`), multi-tenant tiering (`5.14`) |
| **Cache & Async** | Postgres `SKIP LOCKED` queue hoặc 1 Redis/Valkey nhỏ; **Không** dual-write phức tạp | Valkey (`5.4`) cho hot read + single-flight (`I-033`); Transactional Outbox (`8.3`) sang Kafka/NATS (`5.7`) | Kafka đa AZ với schema registry (`4.7`) + Flink stream (`5.12`), load shedding & adaptive concurrency (`8.5`) |
| **Mạng & Edge** | Cloudflare/CDN miễn phí + HTTPS TLS 1.3 (`4.1`) + REST OpenAPI (`4.3`) | HTTP/2 + HTTP/3 cho mobile (`4.2`), Edge cache (`6.5`), gRPC/Connect nội bộ (`4.4`), PrivateLink (`9.3`) | Cilium eBPF mesh (`9.4`), Gateway API, Anycast/Geo-routing + Edge Workers (`6.5`), BGP/QUIC tối ưu tail |
| **An ninh & Danh tính** | Managed Auth / OAuth 2.1 + PKCE (`10.3`), pre-commit secret scan (`10.6`), least-privilege IAM | RBAC/ReBAC + short-lived JWT/jti revoke (`I-064`), Workload Identity (OIDC/SPIFFE), SBOM (`10.5`) | Zero Trust mTLS, KMS/HSM rotation, PQC hybrid TLS (`10.2`, `14.10.2`), SIEM + SOAR (`10.7`), audit DORA/CRA/GDPR (`10.8`) |
| **Quan sát & Độ tin cậy** | Structured JSON logs + uptime probe + 3 alert chính (5xx, latency p99, disk/OOM) | OpenTelemetry 4 tín hiệu (`11.2`), SLI/SLO & Error Budget (`11.1`), k8s PDB & CPU limit tuning (`2.3`, `9.1`) | Distributed trace sampling + eBPF profiling (`2.8`), Chaos engineering có lịch (`11.3`), On-call & Postmortem blameless chuẩn (`11.4`) |
| **AI / LLM** | Managed API qua 1 thin gateway, semantic cache, prompt versioning | Model routing (`12.6`) nhỏ/rẻ vs lớn, Evals tự động CI (`12.5`), ACL-aware RAG (`I-068`) | Self-host vLLM/SGLang (`12.2`) tách prefill/decode khi tải GPU ổn định `> 55%`, LoRA multi-adapter (`12.7`), AI FinOps quota theo tenant |

**Quy tắc chuyển tầng (khi nào ĐÁNG nâng từ cột trái sang cột phải):**
- Chỉ nâng từ `Startup` → `Scale-up` khi đo được **đúng nút cổ chai** (ví dụ DB CPU/WAL > 70% liên tục dù đã index chuẩn, hoặc 2+ team giẫm chân khi release chung mỗi ngày).
- Chỉ nâng từ `Scale-up` → `Enterprise` khi bài toán chuyển từ *hiệu năng trung bình* sang *bán kính nổ (`blast radius`)*, *tuân thủ pháp lý* hoặc *kinh tế ở biên độ hàng trăm nghìn USD/tháng* (`11.5`).

---

## 4. Năm Câu Hỏi Kiểm tra trước khi Ký ADR Thêm Hạ tầng

1. **Bài toán này nằm ở bậc thang độ trễ nào (`1.1`)?** Liệu 1 index B-Tree (`~0.1 ms` RAM) hay batching (`100` round-trip → `1`) có giải được trước khi thêm Redis/Kafka không?
2. **Nếu thành phần mới này sập hoặc chậm `10×` (`8.5`), request có rớt theo không?** Hay nó biến lỗi cục bộ thành sự cố toàn trang?
3. **Chi phí *nhân lực trực on-call* cho nó là bao nhiêu giờ/tháng (`11.5`)?** Một hệ không có người hiểu cách debug `2h sáng` có chi phí thật cao hơn tiền cloud gấp bội.
4. **Dấu hiệu *đo được* nào chứng minh giải pháp hiện tại đã hết hạn?** Gắn ngưỡng cụ thể (vd `p99 > 400 ms ở 500 RPS` hay `autovacuum không kịp xid`), không gắn cảm tính ("sợ sau này mở rộng").
5. **Đường rút lui / Rollback nếu sai trong `Expand-Contract` (`8.8`) là gì?** Không ký quyết định một chiều khi chưa viết rõ đường quay lại.
