# RUNBOOK BẢO TRÌ DỮ KIỆN & ẤN BẢN — SYSTEMS ATLAS (`SA-2028.1`)

> Tài liệu vận hành cơ chế **F1 / F2 / F3** để giữ sách không bị mục nát giữa các ấn bản quý.

---

## 1. Bốn tầng phân rã (F3 Decay Cadence)

Mỗi công nghệ, phiên bản và chuẩn trong `facts/versions.csv` & `facts/watchlist.csv` thuộc một trong 4 tầng nhịp cập nhật khác nhau:

| Tầng | Nhóm đối tượng | Chu kỳ tối đa | Danh mục trong watchlist / sách |
|---|---|---:|---|
| 🔥🔥 **AI & Agent** | Engine serving LLM, runtime model local, giao thức agent | `7 ngày` / **mỗi lượt build** | `vLLM`, `SGLang`, `llama.cpp`, `Ollama`, `NVIDIA Dynamo`, `MCP spec` |
| 🔥 **Hạ tầng biên** | TLS, container, orchestration, service mesh, IaC | `14 ngày` / **mỗi lượt build** | `Kubernetes`, `Docker Engine`, `OpenSSL`, `Envoy`, `Cilium`, `Terraform`, `OpenTofu`, `gRPC`, `Istio`, `Argo CD`, `Flux` |
| 🌡 **Nền lõi** | Kernel, ngôn ngữ, datastore, streaming, lakehouse | `90 ngày` (**mỗi ấn bản quý**) | `Linux Kernel`, `Python`, `Node.js`, `Go`, `Rust`, `Java (Temurin)`, `PostgreSQL`, `MySQL`, `MongoDB`, `Redis`, `Valkey`, `Apache Kafka`, `RabbitMQ`, `Apache Cassandra`, `Elasticsearch`, `ClickHouse`, `SQLite`, `Prometheus`, `DuckDB`, `Apache Iceberg`, `Apache Arrow` |
| 🧊 **Chuẩn & Luật** | Tiêu chuẩn mật mã, RFC, luật dữ liệu & an toàn mạng | `180–365 ngày` (**6–12 tháng**) | `FIPS 203/204/205`, `GDPR`, `PDPD`, `CRA`, `NIS2`, `DORA`, `OWASP Top 10`, `WCAG`, `RFC` |

---

## 2. Quy trình chạy kiểm định chuẩn (Checklist trước mỗi lần đóng gói)

1. **Thiết lập token GitHub trong môi trường shell** *(tránh rate limit 60 req/giờ của REST API; tuyệt đối không ghi token vào repo)*:
   ```powershell
   $env:GITHUB_TOKEN = gh auth token
   $env:PYTHONIOENCODING = "utf-8"
   ```
2. **Kiểm tra độ tươi & tầng F3:**
   ```bash
   uv run python tools/freshness_check.py
   uv run python tools/maintenance_check.py --strict
   ```
   - Mọi sản phẩm mới xuất hiện trong §3 chương mới phải được phủ trong `facts/versions.csv` hoặc ghi miễn trừ tường minh trong `facts/product-candidates.txt` (`tools/ledger_coverage_check.py --strict`).
3. **Đồng bộ khi phát hiện `DRIFT`:**
   - Rà xem bản phát hành mới có làm thay đổi khuyến nghị hoặc con số bậc độ lớn trong thân chương hay chỉ cập nhật phiên bản ledger.
   - Chạy `uv run python tools/sync_ledger.py` để đồng bộ phiên bản mới vào `facts/versions.csv` và cập nhật baseline `facts/watchlist.csv`.
   - Ghi nhận **mỗi thay đổi sự thật hoặc lỗi kỹ thuật** vào `facts/ERRATA.md` kèm ngày, nguồn xác minh và danh sách chương liên quan.
4. **Kiểm tra tuyến học (F1) và đóng gói phát hành:**
   ```bash
   uv run python tools/red_thread_edu_check.py
   uv run python tools/ledger_coverage_check.py --strict
   uv run python tools/package_release.py
   uv run python tools/audit_release.py
   ```
5. **Làm mới Bộ môn học & Slide (`SA-2028.1-KIT`) và Bộ test toàn phần:**
   ```bash
   uv run python kit/make_kit.py
   uv run python kit/slides/build_slides.py
   uv run python tools/build_trial_pack.py
   uv run pytest -v
   ```

---

## 3. Chính sách `§0.0c` về thay đổi cấu trúc

- Mọi chỉnh sửa dữ kiện (`facts/versions.csv`, `facts/ERRATA.md`, `docs/`) chỉ giải quyết **lỗi chính xác (Accuracy)** và **độ tươi (Freshness)**.
- Không thay đổi cấu trúc 145 chương hay viết thêm `Option S` (~30.000 từ) nếu chưa thu thập kết quả đo từ [`trial-00c/PHIEU-CHAM-3-CHI-SO.md`](../trial-00c/PHIEU-CHAM-3-CHI-SO.md).
