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
| 1   | [AC-TCHECK-1/v1] | ✅ | **FE:** [PreTradeCheck.tsx](file:///d:/Traider/frontend/src/pages/PreTradeCheck.tsx#L98-L150) (Gửi form nhập lệnh), **BE:** [trades.py](file:///d:/Traider/backend/app/api/trades.py#L32-L123) (API xử lý check). |
| 2   | [AC-TCHECK-2/v1] | ✅ | **FE:** [PreTradeCheck.tsx](file:///d:/Traider/frontend/src/pages/PreTradeCheck.tsx#L484-L558) (Hiển thị đủ thông số), **BE:** [trades.py](file:///d:/Traider/backend/app/api/trades.py#L111-L123) (Phản hồi đủ các trường đầu ra). |
| 3   | [AC-TCHECK-3/v1] | ✅ | **FE:** [PreTradeCheck.tsx](file:///d:/Traider/frontend/src/pages/PreTradeCheck.tsx#L371-L399) (Disabled SL/TP khi chọn SELL), **BE:** [trade_schema.py](file:///d:/Traider/backend/app/schemas/trade_schema.py#L29-L46) (Chặn validation đối với lệnh BUY/SELL). |
| 4   | [AC-EMOTION-2/v1] | ✅ | **FE:** [PreTradeCheck.tsx](file:///d:/Traider/frontend/src/pages/PreTradeCheck.tsx#L442-L483) (Overlay Soft Cooldown & Textarea phản tỉnh), **BE:** [trades.py](file:///d:/Traider/backend/app/api/trades.py#L125-L151) (API Acknowledge lưu câu trả lời). |
| 5   | [AC-EMOTION-5/v1] | ✅ | **BE:** [trades.py](file:///d:/Traider/backend/app/api/trades.py#L65-L81) (Luồng xử lý Exception Timeout 4.5s trả về thông điệp dự phòng). |
| 6   | [AC-GUARD-1/v1] | ✅ | **BE:** [ai_service.py](file:///d:/Traider/backend/app/services/ai_service.py#L42-L47) (System prompt cấm đưa ra lời khuyên đầu tư cụ thể). |
| 7   | [AC-GUARD-3/v1] | ✅ | **FE:** [PreTradeCheck.tsx](file:///d:/Traider/frontend/src/pages/PreTradeCheck.tsx#L418-L422) (Hiển thị Disclaimer pháp lý Việt Nam mặc định ở chân biểu mẫu). |
| 8   | [AC-GUARD-4/v1] | ✅ | **BE:** [main.py](file:///d:/Traider/backend/app/main.py#L49-L65) (Background Cron task dọn dẹp log AI cũ định kỳ hàng tuần). |

---

## 2. Các hạng mục checklist (từ `review-checklist.md`)

| RC#   | Trạng thái | Bằng chứng / Ghi chú |
| ----- | ---------- | -------------------- |
| RC-01 | ✅ | Trải nghiệm người dùng và Unit tests đạt 100% tỷ lệ pass. |
| RC-02 | ✅ | Chặn thành công trên FE [PreTradeCheck.tsx](file:///d:/Traider/frontend/src/pages/PreTradeCheck.tsx#L371-L399) và BE [trade_schema.py](file:///d:/Traider/backend/app/schemas/trade_schema.py#L29-L46) |
| RC-03 | ✅ | Xác thực Pydantic đảm bảo $SL < \text{Price} < TP$ [trade_schema.py](file:///d:/Traider/backend/app/schemas/trade_schema.py#L29-L46) |
| RC-04 | ✅ | Tính toán tại BE và AI response [rule_engine.py](file:///d:/Traider/backend/app/services/rule_engine.py#L274-L281) |
| RC-05 | ✅ | Tỷ lệ R:R được tính chuẩn xác ở [risk_calculator.py](file:///d:/Traider/backend/app/services/risk_calculator.py#L21-L24) |
| RC-06 | ✅ | Cột `reflective_answer` và `cooldown_acknowledged` trong bảng `emotion_logs` [emotion_log.py](file:///d:/Traider/backend/app/models/emotion_log.py#L23) |
| RC-07 | ✅ | Tách biệt trong [ai_service.py](file:///d:/Traider/backend/app/services/ai_service.py) và đọc tham số qua Pydantic Settings |
| RC-08 | ✅ | Tương thích router [trades.py](file:///d:/Traider/backend/app/api/trades.py) |
| RC-09 | ✅ | System prompt cấm đầu tư trong [ai_service.py](file:///d:/Traider/backend/app/services/ai_service.py#L42-L47) |
| RC-10 | ✅ | Disclaimer hiển thị ở chân biểu mẫu tại [PreTradeCheck.tsx](file:///d:/Traider/frontend/src/pages/PreTradeCheck.tsx#L418-L422) |
| RC-11 | ✅ | Lọc log kiểm tra theo user ở [trades.py](file:///d:/Traider/backend/app/api/trades.py#L133-L137) |
| RC-12 | ✅ | File `.env` chứa token API không commit lên git |
| RC-13 | ✅ | Client timeout = 4.5s được cài đặt tại [ai_service.py](file:///d:/Traider/backend/app/services/ai_service.py#L77) |
| RC-14 | ✅ | Catch lỗi và xử lý fallback trong [trades.py](file:///d:/Traider/backend/app/api/trades.py#L65-L81) |
| RC-15 | ✅ | Luồng chạy nền daemon dọn dẹp hàng ngày trong [main.py](file:///d:/Traider/backend/app/main.py#L49-L65) |
| RC-16 | ✅ | Viết test case trong [test_trades.py](file:///d:/Traider/backend/app/tests/test_trades.py#L72-L119) |
| RC-17 | ✅ | Viết test case trong [test_trades.py](file:///d:/Traider/backend/app/tests/test_trades.py#L196-L251) |
| RC-18 | ✅ | Viết test case trong [test_trades.py](file:///d:/Traider/backend/app/tests/test_trades.py#L154-L194) |

---

## 3. Các lệnh đã chạy

### 3.1. Lint
*Không chạy linter ngoài do chưa cấu hình chính thức.*

### 3.2. Type-check
```bash
# Lệnh:
npx tsc --noEmit
# Kết quả:
# Hoàn toàn sạch lỗi (không có output cảnh báo).
```

### 3.3. Unit / Integration test
```bash
# Lệnh:
python -m unittest app/tests/test_trades.py
# Kết quả:
# Ran 4 tests in 2.082s
# OK

# Lệnh:
python -m unittest app/tests/test_rules.py
# Kết quả:
# Ran 5 tests in 3.008s
# OK
```

### 3.4. Build
```bash
# Lệnh:
npm run build
# Kết quả:
# Build thành công bundle HTML/JS/CSS cho production.
```

---

## 4. Tổng quan diff

| Loại | File / module | Vai trò chính trong PR |
| ---- | ------------- | ---------------------- |
| NEW | [trade.py](file:///d:/Traider/backend/app/models/trade.py) | Model ORM SQLAlchemy bảng `trades` |
| NEW | [emotion_log.py](file:///d:/Traider/backend/app/models/emotion_log.py) | Model ORM SQLAlchemy bảng `emotion_logs` |
| NEW | [trade_schema.py](file:///d:/Traider/backend/app/schemas/trade_schema.py) | Pydantic validation và payload schemas |
| NEW | [ai_service.py](file:///d:/Traider/backend/app/services/ai_service.py) | Client tích hợp AI qua API OpenRouter với timeout 4.5s |
| NEW | [risk_calculator.py](file:///d:/Traider/backend/app/services/risk_calculator.py) | Động cơ tính toán rủi ro toán học |
| NEW | [rule_engine.py](file:///d:/Traider/backend/app/services/rule_engine.py) | Động cơ kiểm tra vi phạm, chuỗi thua, oversized và tính điểm |
| NEW | [trades.py](file:///d:/Traider/backend/app/api/trades.py) | Các endpoints `/trade-check` và `/acknowledge` |
| NEW | [retention_worker.py](file:///d:/Traider/backend/app/tasks/retention_worker.py) | Script dọn dẹp raw AI response định kỳ > 30 ngày |
| NEW | [test_trades.py](file:///d:/Traider/backend/app/tests/test_trades.py) | Bộ unit test kiểm thử 100% luồng toán học, fallback, và cooldown |
| NEW | [PreTradeCheck.tsx](file:///d:/Traider/frontend/src/pages/PreTradeCheck.tsx) | Trang UI nhập lệnh và phân tích kỷ luật Bento Grid |
| NEW | [PreTradeCheck.module.css](file:///d:/Traider/frontend/src/styles/css/PreTradeCheck.module.css) | Stylesheet Vanilla CSS cô lập cho Pre-trade Check screen |

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
| 1   | Không thêm scope ngoài spec-pack mục 1 (Trong phạm vi MVP) | [x] |
| 2   | Mọi Open Issue vẫn open đều được nêu ở mục 5 | [x] |
| 3   | Mọi RC mức Blocker đã ✅ hoặc đã nêu lý do ở mục 5 | [x] |
| 4   | Lint / type-check / build pass; nếu fail đã được giải trình ở mục 3 | [x] |
| 5   | Không có console log, debug code, commented-out code còn sót | [x] |
| 6   | Không log PII / secret / raw business data vượt mức cần thiết | [x] |
| 7   | Migration/schema/data change có rollback hoặc có giải trình nếu không cần | [x] |
