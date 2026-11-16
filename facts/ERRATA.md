# Nhật ký Hiệu đính (ERRATA)

Mọi thay đổi hiệu đính nguồn đều ghi tại đây: vị trí · cũ → mới · lý do · ngày.
Định vị: mã chương + dòng gốc có thể tìm lại bằng grep chuỗi "cũ".

| # | Ngày | Vị trí | Cũ → Mới | Lý do |
|---|------|--------|----------|-------|
| 1 | 2026-11-04 | 14.7.2 §2 (Hai thế giới thời gian) | "Một hệ 10 msdeadline có thể là…" → "Một hệ deadline 10 ms có thể là…" | Dính chữ Latin-Việt do soạn thảo |
| 2 | 2026-11-04 | 14.7.2 §2 (Jitter là kẻ giết kín) | "network stack trong đườngcriticism" → "network stack trong đường critical path" | Dính chữ, sai thuật ngữ |
| 3 | 2026-11-04 | 14.8.1 §6 | "dựng kế thoại upgrade khi draft đổi" → "dựng kế hoạch upgrade khi draft đổi" | Typo tiếng Việt |
| 4 | 2026-11-04 | 14.8.1 "Đọc gì tiếp" | 'RFC 9075-class "The Tao of IETF"' → 'RFC 6722 "The Tao of IETF"' | Sai số RFC: Tao of IETF hiện hành là RFC 6722 (2024, thay RFC 4677) |
| 5 | 2026-11-16 | 14.8.1 §7 (An ninh) | "TLS 1.0/1.1RFC" + "(→9.8/2.4)" → "TLS 1.0/1.1 RFC" + "(→4.8/2.4)" | Erratum E-1: P9 chỉ có 9.1–9.7; đích đúng là 4.8 (vòng đời/khai tử API & chuẩn) |

## Lịch sử kiểm tra

- 2026-11-16: Đã sửa phép #5 (E-1) trong `content/book/P14-14.8.1-ietf-process.md`, đồng bộ bảng CS2023 và tầng học vào `content/book/P15-00-tang-hoc-cach-dung.md`, hoàn thiện 4 văn kiện lab/quiz nâng cao (`L12–L14`, `P15-02-QA`) và đóng sổ `facts/versions.csv`.
- 2026-11-04: 4 phép trên đã fix trong nguồn; verify pymupdf toàn văn PDF không còn chuỗi cũ ("msdeadline", "đườngcriticism", "kế thoại", "RFC 9075").
- Kèm theo: nâng cấp §0 của 14.5.2 từ template v1 sang v2 (không đổi nội dung chuyên môn, chỉ đổi khuôn Nhập môn).
