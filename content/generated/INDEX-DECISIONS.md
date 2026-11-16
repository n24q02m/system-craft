# INDEX-DECISIONS — Danh mục 139 Quyết định Kiến trúc

| ID | Quyết định | Câu hỏi tự vấn | Chương |
|---|---|---|---:|
| `D-001` | Ranh giới đồng bộ/bất đồng bộ | Gọi nào nằm trên đường người dùng, gọi nào phải async? | `1.1` |
| `D-002` | Vị trí tầng giữ dữ liệu | Cache trong tiến trình / ngoài / replica / đĩa? | `1.1` |
| `D-003` | Ngân sách hop mạng | Bao nhiêu hop × 0,5 ms được phép trong budget? | `1.1` |
| `D-004` | Chọn vùng triển khai | Người dùng ở đâu, dữ liệu gốc ở đâu, RTT chấp nhận? | `1.1` |
| `D-005` | Bố cục dữ liệu thân thiện vi kiến trúc | SoA vs AoS, alignment 64B, chống false sharing? | `1.2` |
| `D-006` | Chọn dòng CPU / instance | IPC, cache L3, SIMD (AVX-512/SVE2), ISA x86/ARM/RISC-V? | `1.2` |
| `D-007` | Dung lượng vs băng thông bộ nhớ | Bao nhiêu kênh DDR5, băng thông cần cho workload? | `1.3` |
| `D-008` | NUMA policy | Bind, interleave hay default? HugePages cho DB? | `1.3` |
| `D-009` | Chọn loại ổ theo workload | SLC/TLC/QLC, NVMe/SATA/HDD, DWPD bao nhiêu? | `1.4` |
| `D-010` | Bảo vệ dữ liệu trên đĩa | RAID 0/10/5/6 hay erasure coding? CMR hay SMR? | `1.4` |
| `D-011` | GPU vs CPU cho bài toán | Arithmetic intensity có vượt ridge point không? | `1.5` |
| `D-012` | Chia GPU đa thuê bao | MIG, time-slicing hay dedicated? | `1.5` |
| `D-013` | Phân bổ lane PCIe | NIC/GPU/NVMe chia x16/x8 thế nào cho đủ? | `1.6` |
| `D-014` | RDMA vs TCP nội bộ | RoCEv2/IB đáng chi phí & vận hành không? | `1.6` |
| `D-015` | MTU & topology | Jumbo frame? Tỷ lệ oversubscription bao nhiêu? | `1.7` |
| `D-016` | TEE cho dữ liệu nhạy cảm | SEV-SNP/TDX đáng chi phí hiệu năng không? | `1.8` |
| `D-017` | NTP vs PTP + lưu timestamp | Độ chính xác thời gian cần bao nhiêu; UTC/monotonic? | `1.9` |
| `D-018` | Chọn region theo điện/nhiệt/carbon | Giá điện, PUE, carbon intensity ảnh hưởng chi phí? | `1.10` |
| `D-019` | Chính sách overcommit bộ nhớ | Chấp nhận OOM killer hay từ chối cấp phát? | `2.1` |
| `D-020` | Chọn allocator | glibc / jemalloc / mimalloc cho workload? | `2.2` |
| `D-021` | Đặt requests/limits & QoS | Guaranteed/Burstable; limits.cpu có gây throttle? | `2.3` |
| `D-022` | Ngữ nghĩa bền vững ghi đĩa | fsync/fdatasync/O_DIRECT cho DB? | `2.4` |
| `D-023` | Chọn mô hình I/O | epoll + worker, io_uring, hay thread-per-conn? | `2.5` |
| `D-024` | Tuning netstack | somaxconn, backlog, conntrack, TIME_WAIT? | `2.6` |
| `D-025` | Mức cô lập cho code không tin cậy | Container / gVisor / Firecracker / Kata? | `2.7` |
| `D-026` | Khi nào dùng eBPF | Quan sát/hạn tốc không xâm lấn đáng dùng không? | `2.8` |
| `D-027` | Chọn runtime cho workload | I/O-bound / CPU-bound / mixed → Python/Node/Go/Rust/Java/C++? | `3.9` |
| `D-028` | Mô hình đồng thời | Event-loop, thread pool, green threads, async/await? | `3.1` |
| `D-029` | Python song song | GIL, free-threaded 3.13t+, multiprocess, hay C-ext? | `3.2` |
| `D-030` | Node mở rộng | cluster, worker_threads; cái gì được phép chặn loop? | `3.3` |
| `D-031` | Go vận hành | GOMAXPROCS container-aware, pprof, chặn goroutine? | `3.4` |
| `D-032` | Rust async | Tokio vs current-thread; spawn_blocking cho việc nặng? | `3.5` |
| `D-033` | JVM hiện đại | Virtual threads hay pool; G1 vs ZGC generational? | `3.6` |
| `D-034` | C++ async | std::execution, Seastar, hay thread pool? | `3.7` |
| `D-035` | Wasm dùng ở đâu | Edge runtime, plugin, isolate đa ngôn ngữ? | `3.8` |
| `D-036` | Số worker / pool size | Công thức theo Little & tỷ lệ chờ? | `3.10` |
| `D-037` | Timeout budget toàn trình | Chia timeout qua 9 trạm phục vụ thế nào? | `3.10` |
| `D-038` | Chọn HTTP stack | Uvicorn/Fastify/net-http/Hyper/Netty theo workload? | `3.11` |
| `D-039` | Chọn họ giao thức | REST / gRPC-Connect / GraphQL / SSE / WS / WebTransport? | `4.9` |
| `D-040` | Bật HTTP/3 QUIC | Đáng giá với người dùng mobile không? | `4.2` |
| `D-041` | Cấu hình TLS | 1.3, 0-RTT (replay risk), mTLS nội bộ? | `4.1` |
| `D-042` | Đặc tả hợp đồng | OpenAPI 3.2 (SSE/QUERY) áp khi nào? | `4.3` |
| `D-043` | Phiên bản hoá API | URI / header / date-based; chính sách deprecate? | `4.8` |
| `D-044` | Idempotency | Idempotency-Key cho POST đặt hàng/thanh toán? | `4.8` |
| `D-045` | Pagination | Cursor/keyset hay offset? | `4.8` |
| `D-046` | Rate limiting | Token bucket / sliding window; theo tenant hay IP? | `4.8` |
| `D-047` | Chuẩn báo lỗi | RFC 9457 Problem Details? | `4.8` |
| `D-048` | Webhooks | Ký HMAC, replay protection, retry policy? | `4.8` |
| `D-049` | GraphQL vận hành | Depth/cost limit, persisted queries, DataLoader? | `4.5` |
| `D-050` | Realtime channel | SSE đủ hay cần WS/WebTransport datagrams? | `4.6` |
| `D-051` | Hợp đồng sự kiện | AsyncAPI + Schema Registry; compatibility mode nào? | `4.7` |
| `D-052` | Chọn họ datastore | Workload → RDBMS/document/KV/wide/search/queue/OLAP/object/vector/graph/TS? | `5.15` |
| `D-053` | Isolation level | Read committed đủ không; khi nào cần serializable? | `5.2` |
| `D-054` | Chiến lược index | B-tree/GIN/BRIN; index nào đáng tiền? | `5.2` |
| `D-055` | Connection pool | Pool size theo core & latency; PgBouncer mode? | `5.2` |
| `D-056` | Thiết kế document | Embedding vs referencing? | `5.3` |
| `D-057` | SQLite ở production | Server/edge dùng SQLite khi nào? | `5.3` |
| `D-058` | Chiến lược cache | TTL, jitter, single-flight chống stampede? | `5.4` |
| `D-059` | Redis vs Valkey | Giấy phép AGPL vs BSD-3, vận hành? | `5.4` |
| `D-060` | Partition key | Thiết kế key chống hot partition? | `5.5` |
| `D-061` | Consistency level | QUORUM / LOCAL_QUORUM / ONE theo use case? | `5.5` |
| `D-062` | Queue vs log | RabbitMQ vs Kafka vs NATS; share groups + DLQ? | `5.7` |
| `D-063` | OLAP layout | MergeTree/partitioning/nén; nhánh LTS ClickHouse? | `5.8` |
| `D-064` | Lakehouse layout | Iceberg v3 partition/sort order, compaction service? | `5.9` |
| `D-065` | ANN index | HNSW/IVF-PQ/DiskANN; pgvector hay dedicated store? | `5.10` |
| `D-066` | Graph & time-series | Graph chuyên dụng vs SQL đệ quy; TSDB vs ClickHouse? | `5.11` |
| `D-067` | Nhất quán đa store | Outbox + CDC hay dual-write? | `5.15` |
| `D-068` | Multi-tenancy dữ liệu | Silo / Bridge / Pool + RLS? | `5.14` |
| `D-069` | Retention & xoá thật | TTL, GDPR erasure xuyên cache/log/backup? | `5.13` |
| `D-070` | Nền tảng client | Web / mobile / desktop / embedded; native vs cross? | `6.2` |
| `D-071` | Offline-first | Có cần sync engine local-first không? | `6.3` |
| `D-072` | Giải quyết xung đột | LWW / OT / CRDT (Yjs, Automerge)? | `6.3` |
| `D-073` | Chiến lược push | APNs/FCM/WebPush; nền tĩnh & pin? | `6.4` |
| `D-074` | Edge & CDN | Cache header, surrogate key, edge compute ở đâu? | `6.5` |
| `D-075` | Giao thức IoT | MQTT/CoAP/Matter; fleet provisioning? | `6.6` |
| `D-076` | Tin cậy client | Attestation, keychain, không lưu secret? | `6.7` |
| `D-077` | Chiến lược rendering | CSR/SSR/SSG/ISR/RSC/Islands theo trang? | `7.1` |
| `D-078` | Phân loại state | Server cache / URL / UI / form / client store? | `7.2` |
| `D-079` | Performance budget | Bundle size, INP target, code-split? | `7.3` |
| `D-080` | Design system | Tokens, versioning, breaking change? | `7.4` |
| `D-081` | Phạm vi a11y & i18n | WCAG 2.2, RTL, ICU? | `7.5` |
| `D-082` | Kiểm thử FE | Unit/component/visual/E2E chọn gì? | `7.6` |
| `D-083` | Bảo mật FE | CSP nonce, Trusted Types, SSR/RSC leak? | `7.7` |
| `D-084` | Có cần đồng thuận | Raft/etcd, hay lease đủ, hay không cần? | `8.2` |
| `D-085` | Lock phân tán | Lock cho hiệu năng hay đúng đắn; fencing token? | `8.2` |
| `D-086` | Giao dịch xuyên service | 2PC / Saga / Outbox? | `8.3` |
| `D-087` | Sharding key | Range/hash/consistent + virtual nodes; reshard? | `8.4` |
| `D-088` | Replication factor & quorum | R+W>N; sloppy quorum? | `8.4` |
| `D-089` | Chính sách retry | Backoff + jitter, retry budget ≤10%? | `8.5` |
| `D-090` | Circuit breaker & bulkhead | Kích hoạt khi nào; pool riêng cho dependency? | `8.5` |
| `D-091` | Load shedding | Ưu tiên huỷ gì khi quá tải? | `8.5` |
| `D-092` | Multi-region | Active-active vs passive; conflict resolution? | `8.7` |
| `D-093` | Kích thước cell | Blast radius chấp nhận được? | `8.7` |
| `D-094` | Event sourcing | Có thật sự cần không? | `8.6` |
| `D-095` | Migration không downtime | Expand-contract, Strangler, flags? | `8.8` |
| `D-096` | requests vs limits | Chính sách cho CPU/mem; tránh CFS throttle? | `9.1` |
| `D-097` | PDB & graceful drain | minAvailable; terminationGracePeriod? | `9.1` |
| `D-098` | Autoscaler | HPA / VPA / KEDA (scale-to-0) / Karpenter? | `9.2` |
| `D-099` | Ingress → Gateway API | Envoy Gateway vs Cilium; sidecar vs ambient? | `9.4` |
| `D-100` | Serverless vs container | Cold start, hoà vốn chi phí? | `9.5` |
| `D-101` | Thiết kế VPC | CIDR, NAT avoidance bằng PrivateLink? | `9.3` |
| `D-102` | IaC & state | Terraform/OpenTofu/Crossplane; drift detection? | `9.6` |
| `D-103` | GitOps | Argo CD / Flux pull model? | `9.6` |
| `D-104` | Chiến lược build | Monorepo, remote cache, hermetic? | `9.7` |
| `D-105` | Progressive delivery | Canary + auto rollback theo SLO? | `9.7` |
| `D-106` | Phạm vi threat model | STRIDE/LINDDUN; trust boundary nào? | `10.1` |
| `D-107` | Lộ trình PQC | Hybrid X25519MLKEM768 khi nào; dữ liệu lưu dài hạn? | `10.2` |
| `D-108` | AuthN flow | OAuth 2.1 + PKCE, passkeys, device flow? | `10.3` |
| `D-109` | Session vs JWT | Thu hồi được không; lưu đâu? | `10.3` |
| `D-110` | Mô hình phân quyền | RBAC / ABAC / ReBAC (Zanzibar)? | `10.3` |
| `D-111` | Mức SLSA & SBOM | L1-L3; CycloneDX/SPDX; EPSS/KEV ưu tiên vá? | `10.5` |
| `D-112` | Quản lý secrets | Dynamic (Vault) vs static; workload identity? | `10.6` |
| `D-113` | Detection engineering | Rule nào, log nào, alert fatigue? | `10.7` |
| `D-114` | Phạm vi tuân thủ | CRA / NIS2 / DORA / GDPR/PDPD áp cho sản phẩm? | `10.8` |
| `D-115` | Chính sách license OSS | MIT/Apache vs GPL/AGPL/SSPL trong SaaS? | `10.8` |
| `D-116` | Chọn SLI | Metric nào phản ánh nỗi đau người dùng? | `11.1` |
| `D-117` | Đặt SLO & error budget | Con số 9 nào; chính sách tiêu budget? | `11.1` |
| `D-118` | Cảnh báo | Multi-window burn-rate thay ngưỡng tĩnh? | `11.1` |
| `D-119` | Sampling trace | Head vs tail; tỷ lệ bao nhiêu? | `11.2` |
| `D-120` | Cardinality | Cái gì được làm label; chống nổ Prometheus? | `11.2` |
| `D-121` | Incident roles | IC / Ops / Comms; mitigate trước? | `11.4` |
| `D-122` | Capacity model | Little + USL dự báo; chaos kiểm chứng? | `11.3` |
| `D-123` | Unit economics | Chi phí / 1k request / tenant / triệu token? | `11.5` |
| `D-124` | Team topology | Stream-aligned / platform / enabling? | `11.6` |
| `D-125` | ADR & sunset | Quy trình quyết định; khi nào khai tử hệ thống? | `11.6` |
| `D-126` | Serving engine | vLLM / SGLang / TensorRT-LLM / Dynamo disaggregated? | `12.2` |
| `D-127` | Batching & prefix cache | Continuous batching; RadixAttention đáng dùng? | `12.2` |
| `D-128` | Quantization | FP8 / NVFP4 / AWQ; độ chính xác đổi lấy gì? | `12.2` |
| `D-129` | RAG vs long-context | Prefix cache đủ hay cần retrieval; ACL-aware? | `12.3` |
| `D-130` | Eval gate | Golden set, LLM-judge; chặn CI/CD khi trượt? | `12.5` |
| `D-131` | Model routing | Cascading nhỏ→lớn; semantic cache? | `12.6` |
| `D-132` | Guardrails | Chống prompt injection trực tiếp/gián tiếp; PII? | `12.5` |
| `D-133` | Agent sandbox & MCP auth | Code exec isolate; OAuth 2.1 resource server? | `12.4` |
| `D-134` | Sổ cái & idempotency toàn trình | Double-entry, đối soát, khoá chống trừ 2 lần? | `13.1` |
| `D-135` | Fan-out realtime quy mô lớn | Presence, pub/sub đa node, reconnect storm? | `13.2` |
| `D-136` | Isolation SaaS b2b | Pool→Bridge→Silo theo tier khách hàng? | `13.7` |
| `D-137` | Khi nào gọi chuyên gia ngành | Biên giới 14 ngành; tự quyết tới đâu? | `14.11.2` |
| `D-138` | Carbon-aware & điện | Lịch job theo giờ điện sạch? | `1.10` |
| `D-139` | Build vs buy | Ma trận tự làm / mua / vendor lock-in? | `11.7` |
