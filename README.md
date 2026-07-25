# Engineering Lessons

Ghi chép kỹ thuật về những hệ thống học máy đã từng xây: cách tiếp cận, đối chiếu với chuẩn ngành,
và những bài học còn lại sau khi mọi thứ đã chạy xong.

Nội dung hiện có bản tiếng Việt. Bản tiếng Anh sẽ được bổ sung sau — cấu trúc site đã sẵn sàng cho
song ngữ.

## Chạy tại máy

```bash
bun install
bun run dev      # http://localhost:4321/engineering-lessons/
bun run build    # xuất tĩnh ra dist/
```

## Cấu trúc

```
src/
  content/blog/vi/   bài viết tiếng Việt (tên tệp tiếng Anh)
  content/blog/en/   bản tiếng Anh, thêm sau
  pages/[lang]/      trang chỉ mục, trang bài, trang giới thiệu theo ngôn ngữ
  i18n.ts            danh sách ngôn ngữ đang bật và chuỗi giao diện
```

Thêm một ngôn ngữ: đặt tệp Markdown cùng tên vào `src/content/blog/<lang>/`, rồi thêm mã ngôn ngữ đó
vào `ACTIVE_LANGS` trong `src/i18n.ts`.

## Triển khai

Đẩy lên nhánh `main`; GitHub Actions build và xuất bản lên GitHub Pages.
