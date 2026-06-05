# Kế hoạch triển khai: Risk Calculator, Rule Engine & Discipline Score (impl-risk-engine-score)

Kế hoạch này chi tiết hóa cách thức xây dựng công thức toán học tính toán rủi ro tài chính, bộ máy kiểm tra luật (Rule Engine), công thức điểm kỷ luật (Discipline Score) và cơ chế cảnh báo hạ nhiệt (Soft Cooldown) cho TradeMind AI MVP.

---

## 1. Mục tiêu chức năng

*   **Risk Calculator:** Thực hiện tính toán rủi ro lệnh bằng công thức cố định tại Backend. *Tuyệt đối không giao việc tính toán này cho AI*.
*   **Rule Engine:** Đối chiếu các thông số của lệnh giao dịch dự định với bộ luật cá nhân của user đang bật (active) để phát hiện các vi phạm (violations).
*   **Discipline Score:** Tính toán điểm kỷ luật cuối cùng từ 0-100 dựa trên các điểm trừ (penalty) cố định từ Backend.
*   **Soft Cooldown:** Kích hoạt cảnh báo dừng giao dịch nếu điểm cảm xúc quá cao hoặc vi phạm nghiêm trọng (Severity Critical), đưa ra các câu hỏi hướng dẫn người dùng tự kiểm duyệt tâm lý.

---

## 2. Quy tắc và Công thức toán học (Business Logic)

### 2.1 Risk Calculator (Chỉ áp dụng cho lệnh BUY)
*   `risk_per_share` (Rủi ro trên mỗi cổ phiếu) = `entry_price` - `stop_loss`
*   `total_risk` (Tổng số tiền chịu rủi ro) = `risk_per_share` * `quantity`
*   `risk_percent` (Tỉ lệ rủi ro tài khoản) = (`total_risk` / `account_size`) * 100
*   *Lưu ý đối với lệnh SELL (SELL_TO_CLOSE):* Không áp dụng công thức trên. Hệ thống tính `estimated_PL = (exit_price - entry_price) * quantity` nếu có dữ liệu vị thế cũ mua vào.

### 2.2 Quy tắc prevent_oversized_trade (Rule phát hiện lệnh quá cỡ)
Hệ thống kiểm tra 4 điều kiện để xác định lệnh có dung tích quá lớn hay không:
1.  **Vượt rủi ro tối đa:** `risk_percent` >= 1.5 * `max_risk_per_trade` (ví dụ: max risk là 2%, lệnh này có risk_percent = 3.5% -> Vi phạm).
    *   *Severity:* **Critical** | *Cooldown:* **True**
2.  **Vượt quy mô lịch sử:** `trade_value` >= 2 * `median_trade_value_last_20` (với `trade_value = entry_price * quantity`, `median_trade_value_last_20` là giá trị trung vị của 20 lệnh gần nhất trong Journal).
    *   *Severity:* **Medium** | *Cooldown:* **False**
3.  **Tài khoản mới giao dịch lớn:** User có dưới 5 trade lịch sử và `trade_value` > 50% `account_size`.
    *   *Severity:* **Medium** | *Cooldown:* **False**
4.  **Tăng quy mô sau chuỗi thua:** User đang có chuỗi thua liên tiếp `consecutive_losses` >= 2 và `trade_value` >= 1.5 * `median_trade_value_last_20`.
    *   *Severity:* **Critical** | *Cooldown:* **True**

### 2.3 Công thức Discipline Score
Backend nhận điểm số cảm xúc từ AI và thực hiện tính điểm kỷ luật:
```text
Discipline Score = max(0, 100 - Tổng các điểm phạt penalty hợp lệ)
```

**Bảng phạt penalty và phân cấp mức độ nghiêm trọng (Severity):**
| Tình huống vi phạm | Penalty | Severity | Trạng thái luật đi kèm |
|--------------------|---------|----------|------------------------|
| Thiếu Stop-loss | `-25` | High | `require_stop_loss` active |
| Điểm FOMO cao | `-15` | High | `max_fomo_score` active và `fomo_score > max_fomo_score` |
| Điểm Revenge cao | `-25` | Critical | `revenge_score >= 8` (Mặc định check) |
| Điểm Panic cao | `-20` | Critical | `panic_score >= 8` (Mặc định check) |
| Vượt rủi ro tài khoản | `-20` | High | `max_risk_per_trade` active và `risk_percent > max_risk_per_trade` |
| Lý do giao dịch quá ngắn | `-15` | Low | `reason` có độ dài < 15 ký tự |
| Giao dịch sau chuỗi thua | `-20` | Critical | `consecutive_losses >= max_consecutive_losses` active |
| Giao dịch quá cỡ (Oversized) | `-15` | Biến động | `prevent_oversized_trade` active và thỏa 1 trong 4 đk |

**Phân loại điểm số để hiển thị màu sắc trên UI:**
*   `80 - 100`: **Tốt** (Hiển thị màu Xanh lá)
*   `60 - 79`: **Cần cẩn trọng** (Hiển thị màu Vàng)
*   `40 - 59`: **Rủi ro cao** (Hiển thị màu Cam)
*   `0 - 39`: **Nên dừng giao dịch** (Hiển thị màu Đỏ)

---

## 3. Quy trình tính toán tại Backend (Rule Engine Sequence)

```text
Nhận input lệnh -> 
1. Query DB: Lấy profile (account_size) + active rules của user + lịch sử 20 lệnh gần nhất (để tính median và consecutive losses).
2. Chạy Risk Calculator: Tính risk_percent cho BUY (hoặc estimated P/L cho SELL).
3. Nhận structured data từ AI (hoặc mock data nếu AI fallback): Lấy các điểm số cảm xúc.
4. Chạy Rule Engine: Duyệt qua danh sách active rules để kiểm tra vi phạm.
5. Cộng dồn các điểm penalty của các luật bị vi phạm và các lỗi cảm xúc.
6. Tính Discipline Score = max(0, 100 - tổng penalty).
7. Kiểm tra điều kiện kích hoạt Cooldown:
   - Nếu có bất kỳ vi phạm nào có Severity = Critical, hoặc fomo_score/revenge_score/panic_score >= 8, hoặc emotion_text chứa từ khóa cấm ("all-in", "gỡ lỗ", "mua bằng mọi giá") -> Thiết lập should_cooldown = True.
8. Trả kết quả JSON về cho Frontend.
```

---

## 4. Các trạng thái giao diện UI cần thiết kế

1.  **Giao diện AI Analysis Result:**
    *   Hiển thị điểm số Discipline Score lớn, nổi bật với màu sắc tương ứng (Xanh, Vàng, Cam, Đỏ).
    *   Hiển thị chi tiết bảng tính rủi ro: Số tiền rủi ro ước tính (VND) và tỷ lệ % trên tài khoản.
    *   Liệt kê rõ ràng danh sách các luật bị vi phạm (Ví dụ: *"Vi phạm: Rủi ro vượt giới hạn tối đa (Mức phạt -20, Độ nghiêm trọng: High)"*).
2.  **Hộp thoại Cảnh báo Cooldown (Soft Cooldown Warning Modal):**
    *   Kích hoạt hiển thị nếu `should_cooldown = True`.
    *   Hiển thị cảnh báo màu cam/đỏ khuyên người dùng dừng lại.
    *   Hiển thị 3 câu hỏi tự kiểm duyệt tâm lý để người dùng đọc.
    *   **Nút bấm:** Vẫn hiển thị đầy đủ nút "Lưu Journal" (cho phép tiếp tục lưu nhưng có ghi nhận cảnh báo cooldown) và nút "Sửa kế hoạch" hoặc "Hủy lệnh" để khuyên người dùng suy nghĩ lại.

---

## 5. Kế hoạch kiểm thử (Verification Plan)

### 5.1 Unit Tests (Kiểm thử đơn vị)
*   `test_risk_calculation_buy`: Đảm bảo công thức risk_percent cho BUY tính toán chính xác số liệu dựa trên account size và stop loss.
*   `test_discipline_score_calculation`: Đảm bảo điểm số không bao giờ âm (kể cả khi tổng penalty vượt 100) và áp dụng đúng bảng penalty.
*   `test_prevent_oversized_trade_rule_1`: Thỏa điều kiện vượt 1.5x max_risk -> Severity Critical và `should_cooldown = True`.
*   `test_prevent_oversized_trade_rule_3`: Thỏa điều kiện tài khoản mới giao dịch lớn -> Severity Medium và `should_cooldown = False`.

### 5.2 Integration Tests
*   `test_rule_engine_active_rules_only`: Tắt rule `require_stop_loss` trong DB. Thực hiện check lệnh không có stop loss -> Đảm bảo hệ thống không tạo vi phạm cho rule này và không trừ điểm penalty.
