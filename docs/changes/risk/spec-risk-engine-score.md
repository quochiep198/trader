# Đặc tả chức năng: Risk Calculator, Rule Engine & Discipline Score (spec-risk-engine-score)

Tài liệu này đặc tả yêu cầu nghiệp vụ, thuật toán, công thức tính toán và tiêu chí chấp nhận cho bộ máy chấm điểm kỷ luật (Discipline Score), tính toán rủi ro tài chính (Risk Calculator), bộ máy kiểm tra luật (Rule Engine) và chế độ hạ nhiệt (Soft Cooldown).

---

## 1. Phạm vi nghiệp vụ (Scope)

### Trong phạm vi MVP:
*   Tính toán rủi ro toán học cho lệnh BUY (Entry, Stop-loss, Quantity, Account Size).
*   Kiểm tra sự tuân thủ các quy tắc cá nhân đang kích hoạt (active).
*   Tính toán điểm kỷ luật theo công thức trừ điểm penalty cố định: `Discipline Score = max(0, 100 - tổng penalty)`.
*   Cảnh báo Soft Cooldown khi điểm cảm xúc >= 8 hoặc vi phạm mức độ Critical. Cảnh báo hiển thị bộ câu hỏi tự kiểm điểm tâm lý, không khóa hay chặn thao tác lưu/sửa/hủy của user.

### Ngoài phạm vi MVP:
*   Khóa tài khoản cứng (Hard Cooldown) không cho lưu hoặc đặt lệnh.
*   Cộng dồn điểm thưởng (Discipline Rewards) để tăng điểm kỷ luật.

---

## 2. Quy tắc nghiệp vụ cứng (Business Rules)

| ID | Quy tắc nghiệp vụ | Mã AC tương ứng |
|---|---|---|
| **R-RISK-1** | Risk calculator dùng công thức cố định cho BUY: `risk_per_share = entry_price - stop_loss`, `total_risk = risk_per_share * quantity`, `risk_percent = total_risk / account_size * 100`. | AC-RISK-1/v1 |
| **R-RISK-2** | Lệnh BUY không nhập stop-loss thì rủi ro không đầy đủ; hệ thống báo lỗi hoặc tạo cảnh báo thiếu stop-loss. | AC-RISK-2/v1, AC-RENG-1/v1 |
| **R-RISK-3** | Điểm rủi ro tài chính và tỉ lệ % rủi ro bắt buộc phải tính bằng logic toán học Backend, AI không được phép tự tính toán. | AC-RISK-4/v1 |
| **R-RISK-4** | MVP chỉ hỗ trợ SELL đóng vị thế. SELL không tính `risk_percent` theo công thức BUY mà tính estimated P/L dựa trên thông tin vị thế mua cũ. | AC-RISK-1/v1 |
| **R-RENG-1** | `stop_loss` rỗng + rule `require_stop_loss` active → Vi phạm mức High. | AC-RENG-1/v1 |
| **R-RENG-2** | `consecutive_losses` >= `max_consecutive_losses` active → Vi phạm mức Critical. | AC-RENG-2/v1 |
| **R-RENG-3** | `fomo_score` > `max_fomo_score` active → Vi phạm mức High. | AC-RENG-3/v1 |
| **R-RENG-4** | `trades_today` >= `max_trades_per_day` active → Vi phạm mức Medium. | AC-RENG-4/v1 |
| **R-RENG-5** | Vi phạm phải trả đầy đủ thông tin: `rule_type`, `message`, `severity` (low, medium, high, critical). | AC-RENG-5/v1 |
| **R-RENG-6** | Lệnh giao dịch oversized thỏa 1 trong 4 đk (vượt 1.5x max_risk, 2x median_trade_value_last_20, >50% account size nếu <5 trades, hoặc 1.5x median_trade_value_last_20 sau khi thua >= 2) → Trừ `-15` penalty. | AC-RENG-5/v1 |
| **R-SCORE-1**| Điểm kỷ luật nằm trong khoảng `[0, 100]`, tính theo công thức: `Discipline Score = max(0, 100 - tổng penalty)`. | AC-SCORE-1/v1, AC-SCORE-3/v1 |
| **R-SCORE-2**| AI chỉ trả điểm cảm xúc; backend chịu trách nhiệm tính penalty và score. Severity critical chỉ trigger soft cooldown. | AC-SCORE-2/v1 |
| **R-CD-1** | FOMO/Revenge/Panic score >= 8 hoặc từ khóa nguy hiểm ("all-in", "gỡ lỗ") → kích hoạt Soft Cooldown. | AC-CD-1/v1, AC-CD-2/v1 |
| **R-CD-2** | Cooldown MVP là Soft Cooldown: chỉ nhắc dừng, đưa câu hỏi tự kiểm điểm, không chặn cứng. | AC-CD-3/v1 |
| **R-CD-3** | Cooldown wording không cam kết kết quả đầu tư và không tự nhận hệ thống cấm giao dịch. | AC-CD-4/v1 |

---

## 3. Quy tắc prevent_oversized_trade (Rule phát hiện lệnh quá cỡ)

Một trade được xem là oversized nếu thỏa ít nhất một điều kiện:
1.  `risk_percent` >= 1.5 * `max_risk_per_trade` (Severity: **Critical**, `should_cooldown` = true)
2.  `trade_value` >= 2 * `median_trade_value_last_20` (Severity: **Medium**, `should_cooldown` = false)
3.  Nếu user có dưới 5 trade lịch sử: `trade_value` > 50% `account_size` (Severity: **Medium**, `should_cooldown` = false)
4.  Nếu user có `consecutive_losses` >= 2: `trade_value` >= 1.5 * `median_trade_value_last_20` (Severity: **Critical**, `should_cooldown` = true)

---

## 4. Tiêu chí chấp nhận (Acceptance Criteria)

### 4.1 Risk Calculator (AC-RISK)
*   **AC-RISK-1/v1:** Tính đúng `risk_per_share`, `total_risk`, `risk_percent` cho BUY.
*   **AC-RISK-2/v1:** Nếu `stop_loss` trống, cảnh báo thiếu stop-loss.
*   **AC-RISK-3/v1:** Nếu `risk_percent` vượt `max_risk_per_trade` active, tạo rule violation tương ứng.
*   **AC-RISK-4/v1:** Backend tính toán rủi ro toán học, không để AI tính toán.

### 4.2 Rule Engine (AC-RENG) & Discipline Score (AC-SCORE)
*   **AC-RENG-1/v1 / 2/v1 / 3/v1 / 4/v1:** Tạo đúng các vi phạm và severity tương ứng với stop-loss, consecutive losses, fomo score, trades today.
*   **AC-RENG-5/v1:** Trả đầy đủ `rule_type`, `message`, `severity` trong mảng violations.
*   **AC-SCORE-1/v1:** Điểm kỷ luật nằm trong khoảng 0-100.
*   **AC-SCORE-2/v1:** Giảm score theo bảng penalty cố định đã chốt.
*   **AC-SCORE-3/v1:** Hiển thị đúng nhóm phân loại: Tốt (80-100), Cần cẩn trọng (60-79), Rủi ro cao (40-59), Nên dừng giao dịch (0-39).

### 4.3 Cooldown Mode (AC-CD)
*   **AC-CD-1/v1:** `should_cooldown = true` nếu điểm cảm xúc >= 8.
*   **AC-CD-2/v1:** Kích hoạt cooldown nếu văn bản cảm xúc chứa từ khóa nguy hiểm.
*   **AC-CD-3/v1:** Cooldown chỉ là soft cooldown (cho phép lưu hoặc hủy).

---

## 5. Bảng truy vết kiểm thử (Traceability Matrix)

| AC | Screen/API | DB | Logs | Permissions | Test type |
|---|---|---|---|---|---|
| **AC-RISK-1/v1** | POST /trade-check | users, rules | risk_calculated | Owner user | UT · IT · BB |
| **AC-RISK-3/v1** | POST /trade-check | users, rules | risk_calculated | Owner user | UT · IT · E2E · BB |
| **AC-RENG-1/v1** | POST /trade-check | rules, violations | rule_violation_created | Owner user | UT · IT · E2E · BB |
| **AC-SCORE-1/v1** | POST /trade-check | trades | score_calculated | Owner user | UT · IT · E2E · BB |
| **AC-CD-1/v1** | POST /trade-check | emotion_logs | cooldown_triggered | Owner user | UT · IT · E2E · BB |
| **AC-CD-3/v1** | UI result | N/A | cooldown_triggered | Owner user | IT · E2E · BB |
