# Tự review — auth (Authentication & User Profile)

> Ngày: 2026-06-05
> Nguồn: `docs/changes/auth/spec-pack.md`, `docs/changes/auth/impl-plan.md`, `docs/changes/auth/review-checklist.md`
> Template: `docs/standards/templates/self-review.template.md`
> Được developer/agent điền sau implementation, trước khi review thủ công.
> Mọi checkbox đều phải có bằng chứng: kết quả lệnh, hoặc tham chiếu tệp + số dòng.

---

## 1. Trạng thái hoàn thành AC

> ✅ = đạt | ❌ = chưa đạt | 🔶 = một phần (kèm ghi chú lý do)
> *Lưu ý: Hiện tại dự án đang ở giai đoạn thiết kế đặc tả và kiến trúc, chưa triển khai code. Các trạng thái dưới đây được để trống hoặc đánh dấu ❌ và sẽ được cập nhật sau khi hoàn thành code.*

### 1.1. Authentication (AC-AUTH) — spec docs/changes/auth/spec-pack.md Section 5.1

| #   | AC | Trạng thái | Bằng chứng (file:line, hoặc kết quả test) |
| --- | -- | ---------- | ----------------------------------------- |
| 1   | [AC-AUTH-1/v1] | ❌ | *Chưa code* |
| 2   | [AC-AUTH-2/v1] | ❌ | *Chưa code* |
| 3   | [AC-AUTH-3/v1] | ❌ | *Chưa code* |

### 1.2. User Profile (AC-PROFILE) — spec docs/changes/auth/spec-pack.md Section 5.2

| #   | AC | Trạng thái | Bằng chứng |
| --- | -- | ---------- | ---------- |
| 1   | [AC-PROFILE-1/v1] | ❌ | *Chưa code* |
| 2   | [AC-PROFILE-2/v1] | ❌ | *Chưa code* |
| 3   | [AC-PROFILE-3/v1] | ❌ | *Chưa code* |

---

## 2. Các hạng mục checklist (từ `review-checklist.md`)

| RC#   | Trạng thái | Bằng chứng / Ghi chú |
| ----- | ---------- | -------------------- |
| RC-01 | [ ] | *Chưa code* |
| RC-02 | [ ] | *Chưa code* |
| RC-03 | [ ] | *Chưa code* |
| RC-04 | [ ] | *Chưa code* |
| RC-05 | [ ] | *Chưa code* |
| RC-06 | [ ] | *Chưa code* |
| RC-07 | [ ] | *Chưa code* |
| RC-08 | [ ] | *Chưa code* |
| RC-09 | [ ] | *Chưa code* |
| RC-10 | [ ] | *Chưa code* |
| RC-11 | [ ] | *Chưa code* |
| RC-12 | [ ] | *Chưa code* |
| RC-13 | [ ] | *Chưa code* |
| RC-14 | [ ] | *Chưa code* |
| RC-15 | [ ] | *Chưa code* |
| RC-16 | [ ] | *Chưa code* |
| RC-17 | [ ] | *Chưa code* |
| RC-18 | [ ] | *Chưa code* |
| RC-19 | [ ] | *Chưa code* |
| RC-20 | [ ] | *Chưa code* |
| RC-21 | [ ] | *Chưa code* |
| RC-22 | [ ] | *Chưa code* |
| RC-23 | [ ] | *Chưa code* |
| RC-24 | [ ] | *Chưa code* |
| RC-25 | [ ] | *Chưa code* |
| RC-26 | [ ] | *Chưa code* |
| RC-27 | [ ] | *Chưa code* |
| RC-28 | [ ] | *Chưa code* |
| RC-29 | [ ] | *Chưa code* |
| RC-30 | [ ] | *Chưa code* |
| RC-31 | [ ] | *Chưa code* |
| RC-32 | [ ] | *Chưa code* |
| RC-33 | [ ] | *Chưa code* |
| RC-34 | [ ] | *Chưa code* |
| RC-35 | [ ] | *Chưa code* |
| RC-36 | [ ] | *Chưa code* |
| RC-37 | [ ] | *Chưa code* |
| RC-38 | [ ] | *Chưa code* |
| RC-39 | [ ] | *Chưa code* |
| RC-40 | [ ] | *Chưa code* |
| RC-41 | [ ] | *Chưa code* |
| RC-42 | [ ] | *Chưa code* |
| RC-43 | [ ] | *Chưa code* |

---

## 3. Các lệnh đã chạy

### 3.1. Lint
```bash
# Lệnh:
# npm run lint (Frontend) hoặc flake8/black (Backend)
# Kết quả:
# Chưa thực hiện
```

### 3.2. Type-check
```bash
# Lệnh:
# npm run type-check (Frontend) hoặc mypy (Backend)
# Kết quả:
# Chưa thực hiện
```

### 3.3. Unit test
```bash
# Lệnh:
# npm run test (Frontend) hoặc pytest (Backend)
# Kết quả:
# Chưa thực hiện
```

### 3.4. Build
```bash
# Lệnh:
# npm run build (Frontend) hoặc docker build (Backend)
# Kết quả:
# Chưa thực hiện
```

### 3.5. Manual / E2E (nếu có)

| #   | Scenario | Mode | Kết quả | Ghi chú |
| --- | -------- | ---- | ------- | ------- |
| 1   | Đăng ký và kích hoạt tài khoản | Khách | ❌ | *Chưa thực hiện* |
| 2   | Đăng nhập và lưu cookie session | Khách | ❌ | *Chưa thực hiện* |
| 3   | Kiểm tra IDOR - User A truy cập profile B | User | ❌ | *Chưa thực hiện* |
| 4   | Đăng nhập sai và hiển thị lỗi | Khách | ❌ | *Chưa thực hiện* |
| 5   | Xem cảnh báo thiếu account_size | User | ❌ | *Chưa thực hiện* |

---

## 4. Tổng quan diff

*Giai đoạn thiết kế: Chưa có code thay đổi.*

| Loại | File / module | Vai trò chính trong PR |
| ---- | ------------- | ---------------------- |
| Thêm mới | docs/changes/auth/spec-pack.md | Bản đặc tả phân hệ Auth & Profile |
| Thêm mới | docs/changes/auth/impl-plan.md | Kế hoạch triển khai kỹ thuật Auth & Profile |
| Thêm mới | docs/changes/auth/review-checklist.md | Danh sách kiểm tra review Auth & Profile |
| Thêm mới | docs/changes/auth/self-review.md | Bản tự review ban đầu của Dev |

---

## 5. Rủi ro đã biết / Chưa bao phủ / Công việc còn lại

### 5.1. Known risks

| #   | Rủi ro | Mức độ ảnh hưởng | Cách giảm thiểu / Theo dõi |
| --- | ------ | ---------------- | -------------------------- |
| 1   | Rò rỉ thông tin sự tồn tại của tài khoản qua API báo lỗi đăng nhập | Low | Trả về lỗi chung: "Email hoặc mật khẩu không chính xác" |
| 2   | Lỗi gửi mail verify (SMTP timeout) block luồng đăng ký | Medium | Thực hiện gửi mail bất đồng bộ (Background Tasks) |

### 5.2. Not handled yet

| #   | Hạng mục | Lý do chưa bao phủ | Hành động được đề xuất |
| --- | -------- | ------------------ | ---------------------- |
| 1   | Social login (Google, Facebook) | Chốt ngoài phạm vi MVP | Triển khai ở Phase 2 |

### 5.3. Remaining issues / nợ kỹ thuật
*Không có.*

### 5.4. Open Issues từ impl-plan vẫn còn
*Không có.*

---

## 6. Confirmations cuối cùng

| #   | Confirmation | Trạng thái |
| --- | ------------ | ---------- |
| 1   | Không thêm scope ngoài spec-pack mục 1 (Trong phạm vi MVP) | [x] |
| 2   | Mọi Open Issue vẫn open đều được nêu ở mục 5.4 | [x] |
| 3   | Mọi RC mức Blocker đã ✅ hoặc đã nêu lý do ở mục 5 | [x] |
| 4   | Lint / type-check / build pass; nếu fail đã được giải trình ở mục 3 | [ ] |
| 5   | Không có console log, debug code, commented-out code còn sót | [x] |
| 6   | Không log PII / secret / raw business data vượt mức cần thiết | [x] |
| 7   | Migration/schema/data change có rollback hoặc có giải trình nếu không cần | [x] |
