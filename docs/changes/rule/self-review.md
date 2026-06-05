# Tự review — rule (Personal Trading Rules)

> Ngày: 2026-06-05
> Nguồn: `docs/changes/rule/spec-pack.md`, `docs/changes/rule/impl-plan.md`, `docs/changes/rule/review-checklist.md`
> Được developer/agent điền sau khi hoàn thành code, trước khi review thủ công.
> Mọi checkbox đều phải có bằng chứng: kết quả lệnh, hoặc tham chiếu tệp + số dòng.

---

## 1. Trạng thái hoàn thành AC

> ✅ = đạt | ❌ = chưa đạt | 🔶 = một phần (kèm ghi chú lý do)

| #   | AC | Trạng thái | Bằng chứng (file:line, hoặc kết quả test) |
| --- | -- | ---------- | ----------------------------------------- |
| 1   | [AC-RULES-1/v1] | ✅ | **FE:** [PersonalRules.tsx](file:///d:/Traider/frontend/src/pages/PersonalRules.tsx#L70-L90) (tải danh sách quy tắc khi render trang), **BE:** [rules.py](file:///d:/Traider/backend/app/api/rules.py#L15-L22) (endpoint `GET /api/v1/rules`). |
| 2   | [AC-RULES-2/v1] | ✅ | **FE:** [PersonalRules.tsx](file:///d:/Traider/frontend/src/pages/PersonalRules.tsx#L92-L99) (cập nhật trạng thái switch toggle nháp), [PersonalRules.tsx](file:///d:/Traider/frontend/src/pages/PersonalRules.tsx#L185-L188) (đồng bộ trạng thái gạt sang server khi ấn Save), **BE:** [rules.py](file:///d:/Traider/backend/app/api/rules.py#L24-L47) (endpoint `PUT /api/v1/rules/{id}/toggle`). |
| 3   | [AC-RULES-3/v1] | ✅ | **FE:** [PersonalRules.tsx](file:///d:/Traider/frontend/src/pages/PersonalRules.tsx#L101-L163) (form cập nhật giá trị trong modal), [PersonalRules.tsx](file:///d:/Traider/frontend/src/pages/PersonalRules.tsx#L180-L183) (đồng bộ giá trị cập nhật lên server), **BE:** [rules.py](file:///d:/Traider/backend/app/api/rules.py#L49-L135) (endpoint `PUT /api/v1/rules/{id}/value` với xử lý đồng bộ chuỗi & số hợp lệ). |
| 4   | [AC-RULES-4/v1] | ✅ | **FE:** [PersonalRules.tsx](file:///d:/Traider/frontend/src/pages/PersonalRules.tsx#L109-L141) (chặn giá trị không hợp lệ ngay tại client), **BE:** [rules.py](file:///d:/Traider/backend/app/api/rules.py#L67-L121) (endpoint validate nghiêm ngặt và trả về HTTP 400 Bad Request kèm message Việt hóa). |
| 5   | [AC-RULES-5/v1] | ✅ | **FE:** [PersonalRules.tsx](file:///d:/Traider/frontend/src/pages/PersonalRules.tsx#L223-L227) (banner cảnh báo cố định Disclaimer nhắc nhở quy tắc huấn luyện kỷ luật, không cấu thành tín hiệu giao dịch). |

---

## 2. Các hạng mục checklist (từ `review-checklist.md`)

| RC#   | Trạng thái | Bằng chứng / Ghi chú |
| ----- | ---------- | -------------------- |
| RC-01 | [x] | Toàn bộ AC-RULES-1 đến AC-RULES-5 đã được triển khai, kiểm thử thành công. |
| RC-02 | [x] | Chỉ quản lý bộ luật mặc định và giá trị số của chúng, không cho phép tạo custom rule tự do. |
| RC-03 | [x] | Không có Open Issue phát sinh chưa giải quyết trong code. |
| RC-04 | [x] | Thiết kế UI Bento Grid đúng đặc tả spec. |
| RC-05 | [x] | State rules quản lý tập trung ở [PersonalRules.tsx](file:///d:/Traider/frontend/src/pages/PersonalRules.tsx#L55-L60). |
| RC-06 | [x] | Gọi API thông qua wrapper [api.ts](file:///d:/Traider/frontend/src/services/api.ts). |
| RC-07 | [x] | Quy trình dependencies sạch sẽ, không tạo vòng lặp phụ thuộc. |
| RC-08 | [x] | Đúng contract API đã mô tả trong impl-plan.md. |
| RC-09 | [x] | Cấu hình rules lưu trữ độc lập tại bảng `rules` trong database, tách biệt với bảng `users`. |
| RC-10 | [x] | Thiết kế visual phân lớp rõ rệt giữa rule active (Emerald highlights) và inactive (muted card styles). |
| RC-11 | [x] | Validate kỹ lưỡng ở cả Client ([PersonalRules.tsx:109-141](file:///d:/Traider/frontend/src/pages/PersonalRules.tsx#L109-L141)) và Server ([rules.py:67-121](file:///d:/Traider/backend/app/api/rules.py#L67-L121)). |
| RC-12 | [x] | Tách biệt quyền sở hữu bằng cách so khớp `current_user.id` ([rules.py:31](file:///d:/Traider/backend/app/api/rules.py#L31), [rules.py:57](file:///d:/Traider/backend/app/api/rules.py#L57)). |
| RC-13 | [x] | Tuyệt đối không log thông tin nhạy cảm của người dùng. |
| RC-14 | [x] | Ràng buộc bảo mật query filter theo `current_user.id` trả 404 nếu không khớp sở hữu. |
| RC-15 | [x] | Dữ liệu rule không được lưu ở LocalStorage, chỉ lưu động trong state React. |
| RC-16 | [x] | Toggles xử lý mượt mà trên UI nháp (draft state), chỉ lưu khi ấn Save Settings. |
| RC-17 | [x] | Client chặn định dạng không hợp lệ sớm trước khi submit. |
| RC-18 | [x] | Tránh re-render các khung ngoài (Sidebar/Header) do state cô lập tại trang PersonalRules. |
| RC-19 | [x] | Truy vấn tối ưu hóa thông qua ORM filter theo khóa ngoại. |
| RC-20 | [x] | Đăng ký tài khoản tự động seed 7 luật chuẩn, cấu trúc schema tương thích hoàn toàn. |
| RC-21 | [ ] | Chưa cấu hình Alembic migration cho MVP. |
| RC-22 | [x] | Toggle trạng thái hoạt động cập nhật trường `is_active` tức thì trong database. |
| RC-23 | [x] | Seeding rules tự động tại [auth.py:50-60](file:///d:/Traider/backend/app/api/auth.py#L50-L60) và cơ chế lazy-seeding tại [rules.py:22-38](file:///d:/Traider/backend/app/api/rules.py#L22-38). |
| RC-24 | [ ] | Hệ thống audit log chưa cần phát triển trong phase MVP này. |
| RC-25 | [ ] | Hệ thống audit log chưa cần phát triển trong phase MVP này. |
| RC-26 | [ ] | Hệ thống audit log chưa cần phát triển trong phase MVP này. |
| RC-27 | [x] | Từ chối lưu và hiển thị thông báo lỗi chi tiết khi nhập sai định dạng / sai biên giới hạn. |
| RC-28 | [x] | Lỗi server/mạng không xóa đi draftState người dùng đang chỉnh sửa. |
| RC-29 | [x] | Xử lý lỗi trùng lặp bằng ràng buộc Unique `uq_user_rule_type` trong DB schema. |
| RC-30 | [x] | Việt hóa đầy đủ các thông điệp trả về qua [message.ts](file:///d:/Traider/frontend/src/services/message.ts). |
| RC-31 | [x] | Unit test `test_rule_seeding_on_registration` ([test_rules.py:55-106](file:///d:/Traider/backend/app/tests/test_rules.py#L55-106)) và `test_rule_lazy_seeding_for_existing_user` ([test_rules.py:252-290](file:///d:/Traider/backend/app/tests/test_rules.py#L252-290)) đã chạy thành công. |
| RC-32 | [x] | Unit test `test_rule_value_validation_limits` đã chạy thành công ([test_rules.py:107-177](file:///d:/Traider/backend/app/tests/test_rules.py#L107-177)). |
| RC-33 | [x] | Unit test `test_rule_isolation` đã chạy thành công ([test_rules.py:209-250](file:///d:/Traider/backend/app/tests/test_rules.py#L209-250)). |
| RC-34 | [x] | Integration test `test_rule_toggle_behavior` đã chạy thành công ([test_rules.py:178-208](file:///d:/Traider/backend/app/tests/test_rules.py#L178-208)). |
| RC-35 | [x] | Đã kiểm tra trực quan visual các hiệu ứng, modal, switch và toast. |
| RC-36 | [ ] | Tính năng reset rules chưa được phát triển trong MVP. |
| RC-37 | [x] | Caution Alert Banner hiển thị đầy đủ ở đầu trang. |
| RC-38 | [x] | Nút Discard hoạt động chính xác hoàn trả lại trạng thái cũ từ DB. |
| RC-39 | [x] | Spinner mini và Success Toast trượt hoạt động mượt mà. |

---

## 3. Các lệnh đã chạy

### 3.1. Lint
*Không chạy linter ngoài do chưa cấu hình chính thức.*

### 3.2. Type-check
```bash
# Lệnh:
cd frontend && npm run build
# Kết quả:
# tsc -b && vite build hoàn thành với 0 lỗi.
```

### 3.3. Unit / Integration test
```bash
# Lệnh:
python -m unittest app/tests/test_rules.py
# Kết quả:
# Ran 5 tests in 2.901s - OK
```

### 3.4. Build
```bash
# Lệnh:
cd frontend && npm run build
# Kết quả:
# built successfully in 206ms (index-O48B0yRT.js, index-DrumksU9.css).
```

### 3.5. Manual / E2E (nếu có)

| #   | Scenario | Mode | Kết quả | Ghi chú |
| --- | -------- | ---- | ------- | ------- |
| 1   | Xem danh sách luật mặc định của tài khoản | Đăng nhập | ✅ | Hiển thị đủ 7 luật mặc định đã seed. |
| 2   | Bật/tắt hoạt động của quy tắc bất kỳ | Đăng nhập | ✅ | Chuyển đổi trạng thái nháp, nhấn Save đồng bộ lên DB thành công. |
| 3   | Sửa đổi giá trị luật trong Modal hợp lệ | Đăng nhập | ✅ | Client tự bổ sung kí tự `%` cho Max Risk và đồng bộ DB. |
| 4   | Sửa đổi giá trị luật không hợp lệ | Đăng nhập | ✅ | Chặn hiển thị lỗi đỏ ngay lập tức tại modal, server chặn tiếp. |

---

## 4. Tổng quan diff

| Loại | File / module | Vai trò chính trong PR |
| ---- | ------------- | ---------------------- |
| Thêm mới | backend/app/models/rule.py | Model bảng `rules` chứa các cấu hình luật |
| Thêm mới | backend/app/schemas/rule_schema.py | Pydantic validation DTO cho rules API |
| Thêm mới | backend/app/api/rules.py | API endpoints xử lý GET, toggle và update rules |
| Thêm mới | backend/app/tests/test_rules.py | Bộ unit/integration tests kiểm thử rules |
| Thêm mới | frontend/src/components/Bottombar.tsx | Component bottom bar chân trang dùng chung |
| Thêm mới | frontend/src/components/Bottombar.module.css | Styling cho Bottombar chân trang |
| Sửa đổi | backend/app/api/auth.py | Seed 7 default rules khi đăng ký tài khoản thành công |
| Sửa đổi | backend/app/core/security.py | Ép kiểu user_id string từ JWT thành uuid.UUID |
| Sửa đổi | frontend/src/components/Layout.tsx | Tích hợp Bottombar chân trang vào cấu trúc chung |
| Sửa đổi | frontend/src/services/message.ts | Bổ sung Việt hóa các từ khóa liên quan đến rules và bottombar |

---

## 5. Rủi ro đã biết / Chưa bao phủ / Công việc còn lại

### 5.1. Known risks

| #   | Rủi ro | Mức độ ảnh hưởng | Cách giảm thiểu / Theo dõi |
| --- | ------ | ---------------- | -------------------------- |
| 1   | Xung đột UNIQUE `(user_id, rule_type)` nếu seed lặp | Low | Thực hiện bulk save an toàn ngay khi đăng ký tài khoản. |

### 5.2. Not handled yet

| #   | Hạng mục | Lý do chưa bao phủ | Hành động được đề xuất |
| --- | -------- | ------------------ | ---------------------- |
| 1   | Quản lý custom rules ngoài danh sách hệ thống | Ngoài phạm vi MVP | Triển khai ở Phase sau |

---

## 6. Confirmations cuối cùng

| #   | Confirmation | Trạng thái |
| --- | ------------ | ---------- |
| 1   | Không thêm scope ngoài spec-pack mục 1 (Trong phạm vi MVP) | [x] |
| 2   | Mọi Open Issue vẫn open đều được nêu ở mục 5.4 | [x] |
| 3   | Mọi RC mức Blocker đã ✅ hoặc đã nêu lý do ở mục 5 | [x] |
| 4   | Lint / type-check / build pass; nếu fail đã được giải trình ở mục 3 | [x] |
| 5   | Không có console log, debug code, commented-out code còn sót | [x] |
| 6   | Không log PII / secret / raw business data vượt mức cần thiết | [x] |
| 7   | Migration/schema/data change có rollback hoặc có giải trình nếu không cần | [x] |
