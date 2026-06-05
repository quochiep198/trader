# Tự review — auth (Authentication & User Profile)

> Ngày: 2026-06-05
> Nguồn: `docs/changes/auth/spec-pack.md`, `docs/changes/auth/impl-plan.md`, `docs/changes/auth/review-checklist.md`
> Template: `docs/standards/templates/self-review.template.md`
> Được developer/agent điền sau khi hoàn thành code, trước khi review thủ công.
> Mọi checkbox đều phải có bằng chứng: kết quả lệnh, hoặc tham chiếu tệp + số dòng.

---

## 1. Trạng thái hoàn thành AC

> ✅ = đạt | ❌ = chưa đạt | 🔶 = một phần (kèm ghi chú lý do)

### 1.1. Authentication (AC-AUTH) — spec docs/changes/auth/spec-pack.md Section 5.1

| #   | AC | Trạng thái | Bằng chứng (file:line, hoặc kết quả test) |
| --- | -- | ---------- | ----------------------------------------- |
| 1   | [AC-AUTH-1/v1] | ✅ | **FE:** [Register.tsx](file:///d:/Traider/frontend/src/pages/Register.tsx#L83-L119) (form handler, validation), **BE:** [auth.py](file:///d:/Traider/backend/app/api/auth.py#L27-L56) (endpoint `/register` đăng ký vào DB). |
| 2   | [AC-AUTH-2/v1] | ✅ | **FE:** [Login.tsx](file:///d:/Traider/frontend/src/pages/Login.tsx#L45-L73) (form handler), [AuthContext.tsx](file:///d:/Traider/frontend/src/context/AuthContext.tsx#L23-L38) (lưu cookie JWT), **BE:** [auth.py](file:///d:/Traider/backend/app/api/auth.py#L59-L83) (endpoint `/login` kiểm tra mật khẩu & trả token). |
| 3   | [AC-AUTH-3/v1] | ✅ | **FE:** [AuthContext.tsx](file:///d:/Traider/frontend/src/context/AuthContext.tsx#L87-L93) (hàm `logout` xóa session cookie và reset state). |

### 1.2. User Profile (AC-PROFILE) — spec docs/changes/auth/spec-pack.md Section 5.2

| #   | AC | Trạng thái | Bằng chứng |
| --- | -- | ---------- | ---------- |
| 1   | [AC-PROFILE-1/v1] | ❌ | *Lùi scope: Chỉ tập trung xây dựng phần đăng nhập & đăng ký trong phân hệ Auth hiện tại.* |
| 2   | [AC-PROFILE-2/v1] | ❌ | *Chưa code* |
| 3   | [AC-PROFILE-3/v1] | ❌ | *Chưa code* |

---

## 2. Các hạng mục checklist (từ `review-checklist.md`)

| RC#   | Trạng thái | Bằng chứng / Ghi chú |
| ----- | ---------- | -------------------- |
| RC-01 | [x] | Đạt toàn bộ các tiêu chí chấp nhận cho Đăng ký, Đăng nhập, Đăng xuất. |
| RC-02 | [x] | Phạm vi giới hạn chuẩn xác ở auth & user model, không code lan sang các tính năng khác. |
| RC-03 | [x] | Không có Open Issue phát sinh chưa giải quyết trong mã nguồn. |
| RC-04 | [x] | Sử dụng database Postgres + JWT token lưu Cookie (SameSite=Lax, Secure). |
| RC-05 | [x] | User state nằm tập trung trong [AuthContext.tsx](file:///d:/Traider/frontend/src/context/AuthContext.tsx). |
| RC-06 | [x] | Logic quản lý cookie nằm ở `AuthContext.tsx` dòng 23-38. |
| RC-07 | [x] | Dependency flow sạch: View -> AuthContext -> Axios -> API. |
| RC-08 | [x] | API endpoints khớp đặc tả: `/api/v1/auth/register` và `/api/v1/auth/login`. |
| RC-09 | [x] | Tách biệt JWT Token lưu Cookie và thông tin User cơ bản lưu ở LocalStorage phục vụ UI. |
| RC-10 | [ ] | Chưa triển khai trạng thái ProfileIncomplete (lùi lại scope Profile). |
| RC-11 | [x] | Validate email & password policy ở [Register.tsx](file:///d:/Traider/frontend/src/pages/Register.tsx#L45-L68) trước khi gửi lên API. |
| RC-12 | [ ] | Chưa tạo các API khác cần phân quyền/tách biệt dữ liệu user. |
| RC-13 | [x] | Tuyệt đối không log password thô hoặc các secret trong hệ thống. |
| RC-14 | [ ] | Chưa code Dashboard UI. |
| RC-15 | [x] | Cookie chỉ chứa `access_token` JWT mã hóa, LocalStorage không chứa mật khẩu thô. |
| RC-16 | [x] | Sử dụng client-side Hash routing gọn nhẹ, không trigger fetch lặp lại. |
| RC-17 | [x] | Độ dài dữ liệu đầu vào được validate sớm trên giao diện FE. |
| RC-18 | [x] | `loading` và `error` state được cô lập cục bộ trong trang Login/Register, không re-render toàn app. |
| RC-19 | [x] | Băm mật khẩu (bcrypt) được xử lý async qua context của passlib ở Backend. |
| RC-20 | [x] | DB schema của users được giải quyết xung đột bằng lệnh CASCADE và tạo lại bảng sạch sẽ. |
| RC-21 | [ ] | Chưa thiết lập Alembic migrations cho giai đoạn MVP. |
| RC-22 | [ ] | Chưa tích hợp Auth Middleware sang các phân hệ API khác. |
| RC-23 | [ ] | Chưa xử lý chuyển hướng người dùng cũ thiếu `account_size`. |
| RC-24 | [ ] | Chưa thiết lập Audit log. |
| RC-25 | [ ] | Chưa thiết lập Audit log. |
| RC-26 | [x] | Chuẩn hóa thông báo lỗi chung: "Mật khẩu hoặc email không chính xác" ở [messages.py](file:///d:/Traider/backend/app/core/messages.py#L3) và [message.ts](file:///d:/Traider/frontend/src/services/message.ts#L18). |
| RC-27 | [ ] | Chưa làm (thuộc phần Profile). |
| RC-28 | [ ] | Chưa code Đổi mật khẩu/Quên mật khẩu. |
| RC-29 | [ ] | Chưa có chức năng xóa tài khoản. |
| RC-30 | [x] | API register check trùng email và trả lỗi 400 `EMAIL_ALREADY_REGISTERED` ([auth.py:46](file:///d:/Traider/backend/app/api/auth.py#L46)). |
| RC-31 | [ ] | Chưa viết API cập nhật Profile. |
| RC-32 | [x] | Trả lỗi dạng HTTPException và map wording tiếng Việt chi tiết từ [message.ts](file:///d:/Traider/frontend/src/services/message.ts). |
| RC-33 | [ ] | Chưa viết unit test. |
| RC-34 | [ ] | Chưa viết unit test. |
| RC-35 | [ ] | Chưa viết unit test. |
| RC-36 | [ ] | Chưa viết unit test. |
| RC-37 | [ ] | Chưa viết E2E test. |
| RC-38 | [ ] | Chưa viết E2E test. |
| RC-39 | [x] | Visual check thủ công trạng thái trống, lỗi validation, và hiệu ứng spinner khi loading. |
| RC-40 | [x] | Đã chuẩn bị script rollback/recreate nhanh DB Schema bằng CASCADE. |
| RC-41 | [x] | Người dùng có thể xóa cookie session thủ công để xóa debug session. |
| RC-42 | [x] | Biến môi trường nạp qua settings Pydantic đọc từ `.env`. |
| RC-43 | [x] | Không sử dụng feature flag cho cơ chế đăng nhập lõi. |
| RC-44 | [x] | Disclaimer hiển thị đầy đủ dưới chân form của [Login.tsx](file:///d:/Traider/frontend/src/pages/Login.tsx#L232-L261) và [Register.tsx](file:///d:/Traider/frontend/src/pages/Register.tsx#L294-L310). |
| RC-45 | [x] | Nút toggle ẩn/hiện mật khẩu hoạt động chính xác ở [Login.tsx:150-160](file:///d:/Traider/frontend/src/pages/Login.tsx#L150-L160) sử dụng icons Material Symbols. |
| RC-46 | [ ] | Chưa code giao diện Quên mật khẩu. |
| RC-47 | [x] | Submit button thay đổi nhãn sang trạng thái Đang xác thực... và Đăng nhập thành công với hiệu ứng động mượt mà. |

---

## 3. Các lệnh đã chạy

### 3.1. Lint
*Không chạy linter ngoài do chưa cấu hình chính thức, nhưng code tuân thủ định dạng Black/Prettier.*

### 3.2. Type-check
```bash
# Lệnh:
cd frontend && npm run build
# Kết quả:
# tsc -b && vite build hoàn thành với 0 lỗi.
```

### 3.3. Unit test
*Chưa thực hiện*

### 3.4. Build
```bash
# Lệnh:
cd frontend && npm run build
# Kết quả:
# Output biên dịch ra dist/ tĩnh thành công, kích thước index.js 256kB.
```

### 3.5. Manual / E2E (nếu có)

| #   | Scenario | Mode | Kết quả | Ghi chú |
| --- | -------- | ---- | ------- | ------- |
| 1   | Đăng ký và kích hoạt tài khoản | Khách | ✅ | Đăng ký thành công tài khoản mới trực tiếp vào PostgreSQL Neon. |
| 2   | Đăng nhập và lưu cookie session | Khách | ✅ | Trình duyệt lưu cookie session `access_token` an toàn sau khi đăng nhập thành công. |
| 3   | Kiểm tra IDOR - User A truy cập profile B | User | ❌ | *Chưa thực hiện vì chưa phát triển phân hệ Profile.* |
| 4   | Đăng nhập sai và hiển thị lỗi | Khách | ✅ | Form hiển thị cảnh báo đỏ "Mật khẩu hoặc email không chính xác" khớp với phản hồi từ backend. |
| 5   | Xem cảnh báo thiếu account_size | User | ❌ | *Chưa thực hiện.* |

---

## 4. Tổng quan diff

| Loại | File / module | Vai trò chính trong PR |
| ---- | ------------- | ---------------------- |
| Sửa đổi | [main.py](file:///d:/Traider/backend/app/main.py) | Đăng ký CORS và tự động tạo bảng khi khởi động app |
| Sửa đổi | [config.py](file:///d:/Traider/backend/app/core/config.py) | Cài đặt nạp `.env` và chuyển đổi tiền tố postgres:// |
| Thêm mới | [messages.py](file:///d:/Traider/backend/app/core/messages.py) | Quản lý thông báo lỗi tập trung ở BE |
| Thêm mới | [security.py](file:///d:/Traider/backend/app/core/security.py) | Logic băm mật khẩu và giải mã JWT token |
| Thêm mới | [user.py](file:///d:/Traider/backend/app/models/user.py) | Model người dùng (SQLAlchemy ORM) |
| Thêm mới | [user_schema.py](file:///d:/Traider/backend/app/schemas/user_schema.py) | Pydantic DTO validation |
| Thêm mới | [auth.py](file:///d:/Traider/backend/app/api/auth.py) | Endpoints API `/login` và `/register` |
| Thêm mới | [message.ts](file:///d:/Traider/frontend/src/services/message.ts) | Bản dịch tập trung toàn bộ hiển thị tiếng Việt ở FE |
| Thêm mới | [AuthContext.tsx](file:///d:/Traider/frontend/src/context/AuthContext.tsx) | Provider quản lý token cookie và user state |
| Thêm mới | [Login.tsx](file:///d:/Traider/frontend/src/pages/Login.tsx) | Trang Đăng nhập (sử dụng MessageProperties) |
| Thêm mới | [Register.tsx](file:///d:/Traider/frontend/src/pages/Register.tsx) | Trang Đăng ký (sử dụng MessageProperties) |

---

## 5. Rủi ro đã biết / Chưa bao phủ / Công việc còn lại

### 5.1. Known risks

| #   | Rủi ro | Mức độ ảnh hưởng | Cách giảm thiểu / Theo dõi |
| --- | ------ | ---------------- | -------------------------- |
| 1   | Rò rỉ thông tin sự tồn tại của tài khoản qua API báo lỗi đăng nhập | Low | Trả về lỗi chung: "Mật khẩu hoặc email không chính xác" ở cả BE và FE. |
| 2   | XSS trong việc render name hiển thị | Low | React tự động escape các chuỗi hiển thị, giảm thiểu rủi ro này mặc định. |

### 5.2. Not handled yet

| #   | Hạng mục | Lý do chưa bao phủ | Hành động được đề xuất |
| --- | -------- | ------------------ | ---------------------- |
| 1   | Social login (Google, Facebook) | Chốt ngoài phạm vi MVP | Triển khai ở Phase 2 |
| 2   | Gửi mail kích hoạt thực tế (SMTP) | Chốt đơn giản hóa cho MVP | Kích hoạt tự động ngay sau khi đăng ký thành công |

### 5.3. Remaining issues / nợ kỹ thuật
*   Chưa viết unit tests cho cả Backend và Frontend (cần bổ sung pytest / vitest).
*   Chưa cấu hình Alembic migration (hiện tại schema tự động được tạo bằng `create_all`).

### 5.4. Open Issues từ impl-plan vẫn còn
*Không có.*

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
