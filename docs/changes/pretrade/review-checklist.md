# Danh sách kiểm tra review — pretrade (Pre-trade Check & AI Emotion Analysis)

> Ngày: 2026-06-05
> Nguồn AC: `docs/changes/pretrade/spec-pack.md`
> Nguồn plan: `docs/changes/pretrade/impl-plan.md`
> Mức độ nghiêm trọng: **Blocker** = bắt buộc sửa trước khi merge | **Major** = phải sửa trong PR này | **Minor** = sửa hoặc ghi nhận là nợ kỹ thuật

---

## 1. Spec / AC

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-01 | Tất cả AC ở mục 5 (Tiêu chí chấp nhận) của spec-pack đã được triển khai và có bằng chứng xác thực | Blocker | [ ] |
| RC-02 | Chặn nhập SL/TP đối với lệnh `SELL_TO_CLOSE` trên cả giao diện và API | Blocker | [ ] |
| RC-03 | Bắt buộc nhập SL/TP đối với lệnh `BUY` và đảm bảo $SL < \text{Price} < TP$ | Blocker | [ ] |
| RC-04 | Kích hoạt Soft Cooldown hoàn toàn dựa trên điểm cảm xúc AI (`revenge_score >= 8` hoặc `fomo_score >= 8`) | Blocker | [ ] |

## 2. Thiết kế / Phụ thuộc

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-05 | Công thức tính tỷ lệ Risk/Reward chính xác: $\text{R:R Ratio} = 1 : (\text{Reward}/\text{Risk})$ | Major | [ ] |
| RC-06 | State lưu trữ câu trả lời phản tỉnh (`reflective_answer`) được cấu trúc đúng trong schema và lưu DB | Blocker | [ ] |
| RC-07 | Tách biệt hoàn toàn AI service gọi API ngoài (Gemini/OpenAI) thông qua file cấu hình riêng | Major | [ ] |
| RC-08 | Contract API khớp chính xác đặc tả: POST `/api/v1/trade-check` và POST `/api/v1/trade-check/{log_id}/acknowledge` | Blocker | [ ] |

## 3. Bảo mật & Quy định an toàn (Guardrails)

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-09 | AI Coach tuyệt đối không đưa ra khuyến nghị mua/bán cổ phiếu cụ thể hoặc hứa hẹn lợi nhuận | Blocker | [ ] |
| RC-10 | Hiển thị Disclaimer pháp lý Việt Nam mặc định dưới chân trang kết quả và báo cáo phân tích | Blocker | [ ] |
| RC-11 | Xác thực quyền sở hữu: Người dùng chỉ được xem và xác nhận (acknowledge) log của chính mình | Blocker | [ ] |
| RC-12 | Dữ liệu nhạy cảm (API Keys, prompt) được lưu an toàn trong biến môi trường, không bị lộ ra Git | Blocker | [ ] |

## 4. Hiệu năng & Hoạt động Fallback

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-13 | Tác vụ gọi AI được giới hạn timeout tối đa 4.5 giây để tránh treo luồng ứng dụng | Major | [ ] |
| RC-14 | Khi AI gặp sự cố kỹ thuật hoặc timeout, hệ thống kích hoạt fallback trả về phân tích rủi ro toán học và coach message dự phòng | Blocker | [ ] |
| RC-15 | Background Cron Task hoạt động đúng định kỳ hàng tuần để dọn dẹp log AI cũ hơn 30 ngày | Major | [ ] |

## 5. Kiểm thử

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-16 | Unit test kiểm thử đầy đủ các biên dữ liệu đầu vào của SL/TP và tính toán Risk/Reward | Major | [ ] |
| RC-17 | Unit test kiểm thử luồng hoạt động của Soft Cooldown và việc lưu trữ câu trả lời tự phản tỉnh | Major | [ ] |
| RC-18 | E2E/Integration test giả lập lỗi API AI để kiểm thử phản hồi Fallback hoạt động trơn tru | Major | [ ] |

---

## Bảng ánh xạ AC → Checklist items

| #   | AC | Các hạng mục checklist xác nhận |
| --- | -- | ------------------------------- |
| 1   | AC-TCHECK-1/v1 (Gửi check đầy đủ) | RC-01, RC-03, RC-05, RC-08 |
| 2   | AC-TCHECK-2/v1 (Kết quả check đủ 7 trường) | RC-01, RC-05, RC-08 |
| 3   | AC-TCHECK-3/v1 (Chặn lỗi input đầu vào) | RC-02, RC-03, RC-08 |
| 4   | AC-EMOTION-2/v1 (Soft Cooldown Trigger) | RC-04, RC-06, RC-11, RC-17 |
| 5   | AC-EMOTION-5/v1 (Luồng Fallback an toàn) | RC-13, RC-14, RC-18 |
| 6   | AC-GUARD-1/v1 (Không khuyến nghị mua bán) | RC-09, RC-12 |
| 7   | AC-GUARD-3/v1 ( disclaimer pháp lý VN) | RC-10 |
| 8   | AC-GUARD-4/v1 (Xóa log sau 30 ngày) | RC-15 |
