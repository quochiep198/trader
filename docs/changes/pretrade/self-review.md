# Tự review — pretrade (Pre-trade Check & AI Emotion Analysis)

> Ngày: 2026-06-05
> Nguồn: `docs/changes/pretrade/spec-pack.md`, `docs/changes/pretrade/impl-plan.md`, `docs/changes/pretrade/review-checklist.md`
> Được developer/agent điền sau khi hoàn thành code, trước khi review thủ công.
> Mọi checkbox đều phải có bằng chứng: kết quả lệnh, hoặc tham chiếu tệp + số dòng.

---

## 1. Trạng thái hoàn thành AC

> ✅ = đạt | ❌ = chưa đạt | 🔶 = một phần (kèm ghi chú lý do)

| #   | AC | Trạng thái | Bằng chứng (file:line, hoặc kết quả test) |
| --- | -- | ---------- | ----------------------------------------- |
| 1   | [AC-TCHECK-1/v1] | [ ] | **FE:** [file_name](line) (Gửi form nhập lệnh), **BE:** [file_name](line) (API xử lý check). |
| 2   | [AC-TCHECK-2/v1] | [ ] | **FE:** [file_name](line) (Hiển thị đủ thông số), **BE:** [file_name](line) (Phản hồi đủ 7 trường đầu ra). |
| 3   | [AC-TCHECK-3/v1] | [ ] | **FE:** [file_name](line) (Disabled SL/TP khi chọn SELL), **BE:** [file_name](line) (Chặn validation đối với lệnh BUY/SELL). |
| 4   | [AC-EMOTION-2/v1] | [ ] | **FE:** [file_name](line) (Overlay Soft Cooldown & Textarea phản tỉnh), **BE:** [file_name](line) (API Acknowledge lưu câu trả lời). |
| 5   | [AC-EMOTION-5/v1] | [ ] | **BE:** [file_name](line) (Luồng xử lý Exception Timeout 4.5s trả về thông điệp dự phòng). |
| 6   | [AC-GUARD-1/v1] | [ ] | **BE:** [file_name](line) (System prompt cấm đưa ra lời khuyên đầu tư cụ thể). |
| 7   | [AC-GUARD-3/v1] | [ ] | **FE:** [file_name](line) (Hiển thị Disclaimer pháp lý Việt Nam mặc định ở chân biểu mẫu). |
| 8   | [AC-GUARD-4/v1] | [ ] | **BE:** [file_name](line) (Background Cron task dọn dẹp log AI cũ định kỳ hàng tuần). |

---

## 2. Các hạng mục checklist (từ `review-checklist.md`)

| RC#   | Trạng thái | Bằng chứng / Ghi chú |
| ----- | ---------- | -------------------- |
| RC-01 | [ ] | |
| RC-02 | [ ] | |
| RC-03 | [ ] | |
| RC-04 | [ ] | |
| RC-05 | [ ] | |
| RC-06 | [ ] | |
| RC-07 | [ ] | |
| RC-08 | [ ] | |
| RC-09 | [ ] | |
| RC-10 | [ ] | |
| RC-11 | [ ] | |
| RC-12 | [ ] | |
| RC-13 | [ ] | |
| RC-14 | [ ] | |
| RC-15 | [ ] | |
| RC-16 | [ ] | |
| RC-17 | [ ] | |
| RC-18 | [ ] | |

---

## 3. Các lệnh đã chạy

### 3.1. Lint
*Không chạy linter ngoài do chưa cấu hình chính thức.*

### 3.2. Type-check
```bash
# Lệnh:
# ...
# Kết quả:
# ...
```

### 3.3. Unit / Integration test
```bash
# Lệnh:
# ...
# Kết quả:
# ...
```

### 3.4. Build
```bash
# Lệnh:
# ...
# Kết quả:
# ...
```

---

## 4. Tổng quan diff

| Loại | File / module | Vai trò chính trong PR |
| ---- | ------------- | ---------------------- |
| | | |

---

## 5. Rủi ro đã biết / Chưa bao phủ / Công việc còn lại

### 5.1. Known risks

| #   | Rủi ro | Mức độ ảnh hưởng | Cách giảm thiểu / Theo dõi |
| --- | ------ | ---------------- | -------------------------- |
| 1   | Lỗi quá tải hạn ngạch OpenRouter/Gemini API | High | Đảm bảo luồng Fallback toán học được kiểm thử kỹ lưỡng. |

### 5.2. Not handled yet

| #   | Hạng mục | Lý do chưa bao phủ | Hành động được đề xuất |
| --- | -------- | ------------------ | ---------------------- |
| 1   | Lưu trữ đầy đủ lịch sử hội thoại AI ngoài log thô | Ngoài phạm vi MVP | Triển khai ở Phase sau nếu cần |

---

## 6. Confirmations cuối cùng

| #   | Confirmation | Trạng thái |
| --- | ------------ | ---------- |
| 1   | Không thêm scope ngoài spec-pack mục 1 (Trong phạm vi MVP) | [ ] |
| 2   | Mọi Open Issue vẫn open đều được nêu ở mục 5 | [ ] |
| 3   | Mọi RC mức Blocker đã ✅ hoặc đã nêu lý do ở mục 5 | [ ] |
| 4   | Lint / type-check / build pass; nếu fail đã được giải trình ở mục 3 | [ ] |
| 5   | Không có console log, debug code, commented-out code còn sót | [ ] |
| 6   | Không log PII / secret / raw business data vượt mức cần thiết | [ ] |
| 7   | Migration/schema/data change có rollback hoặc có giải trình nếu không cần | [ ] |
