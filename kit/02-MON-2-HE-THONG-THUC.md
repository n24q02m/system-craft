# MÔN 2 — HỆ THỐNG THỰC (4 tín)

### SYS102 · 45 tiết lý thuyết + 45 tiết thực hành · học kỳ 2 · sách: SYSTEMS ATLAS SA-2028.1, cụm **P5 (13 chương còn lại) + P6 + P7 + P9 + P10 + 8.1/8.2/8.3**

> **Một câu mô tả môn:** từ "máy chạy được" tới "hệ chạy được cho người khác" — dữ liệu, client, nền tảng và an ninh, mỗi thứ đều kèm cách **đo** và cách **hỏng**.
> **Điều kiện tiên quyết:** SYS101 (hoặc tương đương). Cần biết SQL cơ bản ở mức viết được `SELECT`.

---

## 1. Chuẩn đầu ra (CLO)

| # | Sinh viên **làm được** | Kiểm bằng |
|---|---|---|
| CLO1 | Chọn datastore cho một bài toán và **bảo vệ lựa chọn bằng 3 con số** (độ trễ, chi phí, hệ quả vận hành) | Bài kiểm 1 (tuần 4) |
| CLO2 | Thiết kế chống mất dữ liệu cho một luồng ghi: xác định **bước không hoàn tác được**, viết saga + compensation | Bài tập nhóm (tuần 8) |
| CLO3 | Viết một test **hai người dùng** phát hiện rò rỉ dữ liệu chéo (IDOR/tenant) và sửa ở tầng truy vấn | Lab 6 + thi cuối |
| CLO4 | Dựng một môi trường chạy (container/K8s local) có **health check, tài nguyên, và một alert đúng** | Lab 8–9 |
| CLO5 | Đưa ra **một quyết định bảo mật có chữ ký**: chống ai, không chống ai, vì sao | ADR an ninh (tuần 14) |

## 2. Lịch 15 tuần

| Tuần | Lý thuyết | Thực hành | Nộp |
|---|---|---|---|
| 1 | *(Ôn B-tree/LSM từ SYS101)* · 5.3 Document & SQLite · 5.5 Wide-column (tombstone, consistency) | Lab L5: đếm index + `idx_scan`, xoá index chết | Bảng index × dung lượng |
| 2 | *(Ôn RDBMS pool/KV từ SYS101)* · 5.6 Search (shard, ILM) · 5.8 OLAP & Columnar (ClickHouse/DuckDB) | Lab: Little's law cho pool + `--bigkeys` + `_cat/shards` | Phép tính pool + bảng ILM |
| 3 | 5.7 Queue/stream (DLQ, partition) · 5.9 Object/lakehouse (Iceberg v3) · 5.10 Vector databases & ANN | Lab: poison message DLQ + eval 50 câu vector | recall@10 + red team tenant |
| 4 | 5.11 Graph & time-series · 5.12 Batch/stream & freshness · 5.13 Quản trị dữ liệu (DAMA) | Lab: DuckDB trên Parquet thật + data map PII | **Bài kiểm 1** (CLO1) |
| 5 | 5.14 Đa thuê bao tầng dữ liệu · 5.15 Ma trận chọn datastore & CDC · 5.16 Công thức sizing | Lab: thiết kế Outbox/CDC + bảng sizing đa thuê bao | Bảng sizing + isolation |
| 6 | 8.1 Đồng hồ & thứ tự · 8.2 Đồng thuận (STOP–CONT, RTT vs election) · 8.3 Idempotency & saga | Lab L8: STOP–CONT + bơm trùng sự kiện | **Saga + compensation** (CLO2) |
| 7 | 6.1 8 ràng buộc ngược của client · 6.2 Bốn môi trường client · 6.3 Local-first & CRDT | Lab L6: airplane mode 60 giây + 3 kịch bản xung đột | Bảng 5 luồng chết + quyết định sync |
| 8 | 6.4 Push & năng lượng/mạng · 6.5 Edge/CDN (purge, TTL) · 6.6 Nhúng & IoT · 6.7 Bảo mật client & attestation | Lab: tính TTL 10′→1′ tải origin + kiểm định chữ ký client | Phép tính ×10 + attestation checklist |
| 9 | 7.1 Rendering (CSR/SSR/ISR/RSC) · 7.2 Trạng thái & data fetching · 7.3 Bundling & INP | Lab L7: tắt JS, đo INP p75 | Bảng route × INP |
| 10 | 7.4 Component API & Design System · 7.5 Accessibility (WCAG/EAA) & i18n · 7.6 Kiểm thử & RUM · 7.7 Bảo mật frontend | Lab: audit a11y + CSP/Trusted Types + RUM | Báo cáo WCAG + hardening |
| 11 | 9.1 K8s: request/limit, PDB · 9.2 Autoscaling & traffic · 9.3 Chi phí mạng, NAT & DNS | Lab L9: drain node, đo CPU throttle & egress cost | 3 số đo + 3 ticket |
| 12 | 9.4 Mesh & mTLS · 9.5 FaaS & cold start · 9.6 IaC, GitOps & CI/CD · 9.7 Triển khai & rollback | Lab: drill rollback & kiểm tra IaC drift (đo phút) | Bảng thời gian khôi phục |
| 13 | 10.1 Threat model & Zero Trust · 10.2 Mật mã thực hành, KMS & PQC · 10.3 AuthN & AuthZ (OAuth, Passkeys, RBAC/ABAC/ReBAC) | Lab L10: đo timing enumeration + đánh giá luồng AuthZ | Phép đo timing + bảng phân quyền |
| 14 | 10.4 An ninh Ứng dụng & API (OWASP Top 10:2025) · 10.5 Supply chain (SLSA, Sigstore, SBOM) · 10.6 Quản lý bí mật & workload identity | Lab: kiểm thử IDOR hai người dùng + dựng SBOM | **ADR an ninh** (CLO5) |
| 15 | 10.7 Phát hiện & phản ứng sự cố · 10.8 Tuân thủ pháp lý (CRA/NIS2/DORA/GDPR/PDPD) & OSS | Thi thực hành: IDOR + SBOM + sự cố rò rỉ bí mật | **Thi cuối** (CLO3) |

**Mười chương bắt buộc đọc kỹ:** 5.2 · 5.7 · 5.12 · 5.14 · 8.2 · 8.3 · 6.5 · 9.1 · 9.7 · 10.3.

## 3. Đánh giá

| Thành phần | Trọng số | Ghi chú |
|---|---|---|
| Bài kiểm 1 (tuần 4) | 10% | 5 tình huống "chọn datastore", trả lời bằng bảng 3 cột (chọn/lý do/rủi ro) |
| Lab (12 bài, chấm 6) | 25% | mỗi bài phải có **một con số** và **một hành động đề xuất** |
| Bài tập nhóm saga (tuần 8) | 15% | bảng bước + compensation + **bước không hoàn tác được** được đánh dấu |
| ADR an ninh (tuần 14) | 15% | 1 trang, có dòng "**không** chống ai" + chữ ký |
| Thi cuối | 35% | 3 bài tính + 2 câu thiết kế + 1 bài viết test IDOR (code 20 dòng) |

## 4. Ba điều môn này cố tình **không** dạy

1. **Không dạy cú pháp của 10 database.** Dạy **hình câu hỏi quyết định engine**: dữ liệu ghi nhiều hay đọc nhiều, cần thứ tự hay không, cần giao dịch hay không, dữ liệu có nóng theo một tenant hay không. Cú pháp tự học trong 1 tuần; chọn sai engine thì trả giá 3 năm.
2. **Không dạy "best practice".** Mọi khuyến nghị trong sách đều kèm điều kiện (khi nào sai), vì best practice không kèm điều kiện là mê tín.
3. **Không dạy bảo mật bằng danh sách.** Dạy **quy trình ra quyết định**: adversary → bề mặt → bằng chứng → ký nhận rủi ro. Danh sách Top 10 chỉ là bảng kiểm tra sau cùng.

## 5. Sản phẩm cuối môn (nhóm 3 người, chọn 1)

| Đề | Nộp | Chấm theo |
|---|---|---|
| **A. Thiết kế lại một hệ thật** (app quen thuộc) | bản đồ 7 trục + 3 ADR + 1 phép tính chi phí/tháng | số đúng, phương án bị loại có lý do |
| **B. Dựng một luồng ghi không mất dữ liệu** | schema + saga + test bơm trùng + đo | chạy được, chứng minh idempotency |
| **C. Hạ tầng chạy được với 1 alert đúng** | manifest + dashboard + 1 chaos nhỏ có biên bản | alert bắn đúng, không nhiễu |
