# 10.2 — Mật mã Thực hành, KMS & PQC (FIPS 203/204/205)

> **Tầng:** An ninh · **Quyển II** · **Trục đọc:** phòng thủ · **Động từ liên quan:** Bảo vệ · Chọn
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.1 (TLS 1.3 đã gặp) · 8.7 (khoá vùng, thảm hoạ).

**Sợi chỉ đỏ:** *Ranh giới vẽ xong, lớp khoá — mật mã nào đang dùng, và máy lượng tử đã tới cửa chưa?* — trả lời: lớp khoá — mật mã thực hành sống bằng ba quy tắc (đừng tự chế thuật toán, khoá là thứ phải quản); envelope encryption là kiến trúc chuẩn của mọi KMS; bảng chọn thuật toán 2026 có thêm PQC vì "harvest now, decrypt later" không phải viễn tưởng. Câu hỏi để lại cho chương sau: *Ai là ai, được làm gì — authn/authz và token xử lý thế nào cho 4 triệu user?*

**Thuật ngữ sẽ gặp:** *envelope encryption* — dữ liệu khoá bằng DEK, DEK được KEK bọc: kiến trúc chuẩn của mọi KMS; *DEK/KEK* — khoá dữ liệu sinh từng cái, khoá chủ quay vòng: tách vòng đời rõ ràng; *KMS* — dịch vụ giữ khoá: được quyền dùng khoá không đồng nghĩa đọc được khoá; *PQC* — mật mã hậu lượng tử, FIPS 203/204/205 chuẩn hoá 2024: lớp dự phòng cho ngày máy lượng tử; *harvest now, decrypt later* — ghi lưu lượng hôm nay, giải mã khi lượng tử tới: lý do chuyển PQC sớm;

**Ví dụ mở đầu:** DM mã hoá số thẻ và số điện thoại: một khoá duy nhất cho cả bảng nghĩa là lộ một lần là lộ tất cả. Envelope: mỗi bản ghi một DEK, DEK bị KEK bọc và KEK không bao giờ rời KMS. Kẻ ghi lại traffic hôm nay chờ máy lượng tử? PQC là cửa đóng trước khi cửa kia mở.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Ai giữ khoá: cloud KMS / self-managed HSM / client-side | Khoá mất thì ai chịu, khoá lộ thì ai biết? |
| 2 | Chiến lược khoá: envelope (DEK/KEK), rotation, vùng | Xoay khoá là thao tác nhàm chá hay dự án 6 tháng? |
| 3 | Thuật toán chuẩn nào dùng (TLS, at-rest, hash, KDF) | Tôi có dùng gì tự chế hoặc quá cũ (SHA-1, 3DES, RSA-1024)? |
| 4 | PQC lộ trình: hybrid khi nào, dữ liệu nào "lưu dài nhạy cảm" | Dữ liệu của tôi có cần bí mật tới 2035+ không (harvest-now-decrypt-later)? |

---

## 2. Cơ chế

### 2.1 Ba quy tắc sống còn của mật mã thực hành

1. **Không tự chế thuật toán/chế độ** (ECB, "xor của tôi", MD5 cho mật khẩu) — dùng thư viện chuẩn, cấu hình mặc định của nền tảng (libsodium/tink/age/bcrypt-argon2) đúng hơn code tay;
2. **Khoá tách dữ liệu** (khoá không nằm cùng file nó mã hoá; không commit — I-063 → 10.6);
3. **Mã hoá không thay quyền** (authz vẫn kiểm sau giải mã — mã hoá at-rest chỉ chặn "trộm đĩa", không chặn "query hợp lệ từ app bị chiếm").

### 2.2 Envelope encryption — kiến trúc chuẩn của mọi KMS

```
[KEK] nằm KMS/HSM (không bao giờ rời phần cứng — thao tác qua API)
  → KMS sinh/giải [DEK] (khoá dữ liệu, mỗi object 1 cái)
  → DEK mã hoá dữ liệu ở chỗ storage (nhanh — AES-GCM hardware)
  → DEK đã-mã-hoá-bởi-KEK nằm cạnh dữ liệu (envelope)
```
Lợi ích: KMS chỉ thấy khoá (không thấy dữ liệu — tách luồng), thao tác KMS đếm được (quota/chi phí), **xoay KEK = mã hoá lại các DEK** (không đụng hàng TB dữ liệu). Rotation chuẩn: DEK mỗi object tự nhiên (sinh mới khi ghi mới); KEK 90 ngày–1 năm (hoặc theo sự kiện) với lịch re-encrypt nền.

### 2.3 Chọn thuật toán — bảng tiêu dùng 2026

| Mục đích | Chuẩn | Ghi chú |
|---|---|---|
| TLS trong mạng | TLS 1.3 (X25519 + AES-GCM/ChaCha20) | →4.1 |
| Mã hoá at-rest | AES-256-GCM (đĩa/S3) | nền tảng lo |
| Hash chung | SHA-256/512, BLAKE3 (nhanh) | |
| Mật khẩu người dùng | **Argon2id** / bcrypt / scrypt (chậm + muối) | **không** SHA trơn |
| MAC | HMAC-SHA256 / Poly1305 | |
| KDF đối xứng | HKDF | dẫn khoá con đúng cách |
| Chữ ký | Ed25519 / ECDSA P-256 / RSA-3072+ | |
| TLS hậu lượng tử | **hybrid X25519MLKEM768** | §2.4 |

Muối/nonce: mỗi lần dùng một (random đủ hoặc counter) — sai nonce AES-GCM là lộ khoá (nghiêm trọng hơn "hỏng bản mã").

### 2.4 PQC — FIPS 203/204/205 và "harvest now, decrypt later"

NIST chuẩn hoá hậu lượng tử (8/2024): **FIPS 203 ML-KEM** (đổi khoá — dùng cho TLS), **FIPS 204 ML-DSA** (chữ ký), **FIPS 205 SLH-DSA** (chữ ký dựa hash — chậm, an toàn khác biệt). Đe doạ thật cho **hôm nay**: kẻ thu traffic bây giờ để giải **sau** khi có máy lượng tử ("harvest now, decrypt later") — chỉ nguy hiểm với dữ liệu cần bí mật > ~10 năm (y tế, quốc phòng, gene). Hành động 2026:
1. **TLS:** bật hybrid **X25519MLKEM768** (browser + cloud/CDN lớn đã hỗ trợ — tính năng cấu hình, không phải dự án);
2. **Ký artifact/commit dài hạn:** quy hoạch chuyển dịch sang PQC khi toolchain chín (→10.5);
3. **Mật mã đối xứng (AES-256, SHA-384+):** không cần đổi — an toàn trước Grover với kích thước khoá hiện có;
4. **Danh mục dữ liệu lưu dài:** biết mình có gì (thường ít hơn tưởng tượng) — ADR quyết định lộ trình, đừng chạy theo tin tức.

### 2.5 Vấn đề khoá vùng & thảm hoạ

KMS là **single point of failure bằng thiết kế** — mất quyền truy cập khoá = mất dữ liệu (mã hoá tốt quá). Ba câu phải trả lời trước khi architect: khoá có **backup/quorum** không (CloudHSM-style quorum 3/5, hoặc key escrow có kiểm soát)? **Vùng chết thì khoá sống ở đâu** (replicate KMS chéo vùng — →8.7)? **Ai có quyền phá huỷ vĩnh viễn** (đó là quyền lớn nhất hệ thống — audit + 2 người)? Một hệ mã hoá mà không trả lời được 3 câu này thì DR chưa từng được thiết kế — chỉ đang giả vờ.

### 2.6 Mã hoá phía ứng dụng — khi nào hơn KMS thuần

KMS + at-rest mã hoá "đĩa": chặn trộm đĩa/snapshot, **không chặn** cloud-admin/app-bug đọc query thường. Cần chặn cả hai (dữ liệu đặc biệt nhạy — y tế, ví tiền): **mã hoá client-side trước khi gửi** (app giữ khoá, hoặc KMS với grant hẹp per-tenant — →5.14); đánh đổi: mất query (mã hoá thì DB không select được — schema phải tách cột nhạy ra), mất tính năng server (search trên trường mã hoá phải làm ở client/app). Quyết định này là **kiến trúc dữ liệu**, không phải checkbox an ninh.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| FIPS 203/204/205 | chuẩn hoá 8/2024 | V | ML-KEM/ML-DSA/SLH-DSA |
| Hybrid TLS | X25519MLKEM768 triển khai rộng | V | cấu hình, 2025+ |
| KEK rotation | 90 ngày–1 năm | P | |
| Argon2id tham số | memory-hard ≥ 64 MB, t≥1 | P | OWASP khuyến nghị hướng |
| Thu hoạch-ngày-giải-sau | rủi ro dữ liệu sống > ~10 năm | I | |

---

## 4. Suy luận kiến trúc

- **S1:** Mật mã trong hệ thật là **quản lý khoá** (sinh, phân phát, xoay, thu hồi, phá huỷ) — thuật toán là phần dễ và đã giải; thiết kế giải bài khoá, thuật toán lấy từ bảng §2.3.
- **S2:** Tham số trụ: tuổi khoá (KEK/DEK), số thao tác KMS/giây (quota/chi phí), tỉ lệ dữ liệu nhạy không nằm trong envelope, thời gian thử phục hồi khoá (drill).
- **S3:** Client-side mã hoá đổi query/tính năng lấy tin cậy tuyệt đối với admin — chọn theo **loại dữ liệu** (cột), không theo hệ; giải pháp lai (mã hoá cột nhạy, phần còn lại thường) là chuẩn thực chiến.
- **S4:** PQC hôm nay là **cấu hình TLS + danh mục dữ liệu dài hạn** — không phải viết lại; kẻ sơ xuất là kẻ tin "chưa có máy lượng tử = chưa cần nghĩ".
- **S5:** AI tạo khoá dữ liệu mới: embedding/vector DB cũng là dữ liệu cá nhân (tái tạo được từ vector — →12.x/5.10) — chính sách mã hoá phải phủ cả pipeline AI, không chỉ RDBMS truyền thống.
- **S6:** Khi "mã hoá xong mà vẫn lộ": 90% là **khoá lộ** (log/commit/config — I-063) hoặc **quyền** (query hợp lệ), không phải thuật toán vỡ — chẩn theo trình tự đó đỡ mất tháng đuổi ma.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Khoá lộ qua log/commit (I-063) | Secret quản tay | →10.6 vault + scanner | §2.1 |
| Không giải được dữ liệu sau DR | Khoá không replicate chéo vùng | KMS DR plan (→8.7) | §2.5 |
| Hóa đơn KMS cao bất ngờ | Envelope thiếu (mọi byte qua KMS) | DEK tại chỗ + envelope | §2.2 |
| Mật khẩu người dùng lộ ở dạng đọc được | Hash nhanh không muối | Argon2id + rehash lúc login | §2.3 |
| TLS report "yesterday's crypto" | Chưa bật hybrid PQC | bật X25519MLKEM768 | §2.4 |
| Mã hoá at-rest nhưng admin đọc được | Thiếu client-side cho cột nhạy | kiến trúc lai §2.6 | §2.6 |

---

## 6. Cách đo

```bash
# Audit thuật toán cũ trong phụ thuộc (đơn giản, chạy định kỳ):
#   quét cấu hình TLS (sslyze/testssl.sh), quét library (trufflehog/gitleaks cho khoá)

# Drill khoá (mỗi quý): restore 1 object từ backup ở vùng phụ:
#   có giải mã được không? mất bao lâu? ai cần tham gia?
#   — không drill = không biết DR-khoá sống hay chết
```

Nguyên tắc: **khoá là hệ thống riêng có SLO riêng** (thao tác/giây, tuổi, drill) — không phải tham số config đặt một lần.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay cloud KMS:** HSM tự nuôi (Vault + thiết bị — kiểm soát tuyệt đối, vận hành nặng; hợp pháp lý một số ngành đặc thù); **thay envelope:** khoá duy nhất (đơn giản — nhỏ thì được, to thì xoay khoá = tái mã hoá toàn bộ = thảm hoạ vận hành).

Năm thấu kính:
- **Kinh tế:** KMS tính theo thao tác — envelope không chỉ an toàn hơn mà **rẻ hơn** vài bậc độ lớn với dữ liệu lớn; chi phí "quên" mật mã (sự cố lộ) là đơn vị hợp đồng pháp lý, không phải giờ công.
- **Vận hành:** Xoay khoá phải là scripts + drill (giống backup — thứ không drill là thứ không có); mỗi lần thêm vùng/tenant → kế hoạch khoá phải update trong cùng PR (IaC — →9.6).
- **An ninh:** Chuỗi tin mật mã: phần cứng (HSM/TEE) → KMS → DEK → dữ liệu; mạnh bằng mắt xích yếu nhất — thường là **con người giữ quyền admin KMS** (audit + quorum, đừng để một người giữ vương quốc).
- **Lịch sử:** DES (1977, 56-bit) → RSA/elliptic (1990s–2000s) → AES (2001) → SHA-3 (2012) → **PQC chuẩn hoá 2024**: mỗi ~10–15 năm một cuộc di dân; hệ sống sót là hệ **đổi thuật toán được mà không đổi kiến trúc khoá** — envelope + abstraction KMS chính là mua khả năng đó.
- **Người dùng:** Người dùng không thấy mật mã — họ thấy "thông báo: dữ liệu của bạn được bảo vệ" và (khi sự cố) "kẻ xấu không đọc được". Niềm tin đó là sản phẩm vô hình của chương này; làm đúng thì im lặng, làm sai thì ồn ào.

---

## 8. Đọc tiếp & bài tập

- Secrets & workload ID: **10.6** · TLS/QUIC: **4.1** · Crypto-shred/GDPR: **5.13** · Mã hoá cột/tenant: **5.14** · Supply chain ký: **10.5**
- **Bài tập 1:** Liệt kê mọi khoá trong tổ chức (KMS, SSH, signing, API key dài hạn): ai sinh, ai lưu, xoay khi nào, lộ thì ai biết. Bảng này luôn ngắn hơn sự thật — quét tiếp với gitleaks để tìm phần "không ai khai".
- **Bài tập 2:** Chạy drill khoá §6: restore một object mã hoá ở vùng phụ. Thời gian > 30 phút hoặc cần "gọi ai đó" — DR khoá chưa sẵn sàng (và đó là DR dữ liệu luôn).
- **Bài tập 3:** Kiểm cấu hình TLS endpoint chính: đã bật hybrid X25519MLKEM768 chưa? Nếu chưa — đó là thay đổi cấu hình một buổi chiều, đóng cửa "harvest now, decrypt later" cho traffic hôm nay.
