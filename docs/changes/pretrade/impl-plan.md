# Kế hoạch triển khai: Pre-trade Check & AI Emotion Analysis (impl-pretrade-check-ai)

Kế hoạch này chi tiết hóa cách thức xây dựng phân hệ Phân tích trước giao dịch (Pre-trade Check) tích hợp Đánh giá cảm xúc bằng AI (Gemini/OpenAI LLM) cho TradeMind AI MVP.

---

## 1. Mục tiêu chức năng

1. **Nhập lệnh dự định:** Thiết lập biểu mẫu gồm các trường Symbol, Action (BUY/SELL_TO_CLOSE), Price, Quantity, Stop-loss, Take-profit, Reason, Emotion text, Confidence.
2. **Quy tắc toán học & Quản trị rủi ro:**
   * Lệnh `BUY`: Bắt buộc nhập SL/TP. Giá trị phải tuân thủ $SL < \text{Price} < TP$. Tự động tính toán tỷ lệ Lợi nhuận/Rủi ro (Risk/Reward Ratio).
   * Lệnh `SELL_TO_CLOSE`: Vô hiệu hóa (disable) trường nhập SL/TP. Bỏ qua tính toán R:R.
3. **Phân tích cảm xúc qua AI (Gemini/OpenAI API):**
   * Gửi nội dung lý do giao dịch (`reason`) và văn bản cảm xúc (`emotion_text`) qua LLM.
   * AI phản hồi JSON có cấu trúc gồm điểm số cảm xúc (FOMO, Panic, Revenge, Overconfidence, Greed, Hesitation) từ 0-10 và sinh lời khuyên kỷ luật (`coach_message`).
4. **Cơ chế khóa kỷ luật (Soft Cooldown Trigger):**
   * Nếu điểm số từ AI báo cáo có nguy cơ kỷ luật cao (`revenge_score >= 8` hoặc `fomo_score >= 8`), kích hoạt Soft Cooldown.
   * Hiển thị màn hình phủ mờ bắt buộc trả lời câu hỏi tự phản tỉnh (`reflective_answer`) để tiếp tục.
5. **Cơ chế Fallback an toàn:**
   * Nếu API AI lỗi hoặc hết hạn timeout (4.5s), hệ thống tự động trả về tính toán rủi ro toán học từ Backend kèm thông điệp khuyên kỷ luật mặc định để không làm gián đoạn trải nghiệm người dùng.
6. **Chính sách lưu vết và dọn dẹp dữ liệu (Retention Policy):**
   * Log AI được lưu trữ tối đa 30 ngày. Thiết lập một Background Cron task dọn dẹp định kỳ hàng tuần.

---

## 2. Thiết kế dữ liệu (Database Schema)

### Cập nhật Bảng `emotion_logs`
```sql
CREATE TABLE emotion_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trade_id UUID REFERENCES trades(id) ON DELETE SET NULL, -- Liên kết sau khi thực thi giao dịch thực tế
    
    -- Dữ liệu nhập từ người dùng
    reason TEXT NOT NULL,
    emotion_text TEXT NOT NULL,
    emotion_tags VARCHAR(255) NOT NULL, -- Lưu trữ dạng tag ngăn cách bằng dấu phẩy (e.g. "FOMO,Calm")
    
    -- Điểm số cảm xúc từ AI (0 - 10)
    fomo_score INT NOT NULL DEFAULT 0,
    panic_score INT NOT NULL DEFAULT 0,
    revenge_score INT NOT NULL DEFAULT 0,
    overconfidence_score INT NOT NULL DEFAULT 0,
    greed_score INT NOT NULL DEFAULT 0,
    hesitation_score INT NOT NULL DEFAULT 0,
    
    -- Trạng thái rủi ro kỷ luật & Cooldown
    discipline_risk VARCHAR(50) NOT NULL, -- e.g. "Low", "Medium", "High"
    should_cooldown BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Dữ liệu tự phản tỉnh của người dùng (nếu có Soft Cooldown)
    reflective_answer TEXT,
    cooldown_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Lời khuyên của AI Coach và phản hồi thô
    coach_message TEXT NOT NULL,
    raw_ai_response TEXT, -- Lưu JSON thô từ AI phục vụ audit tối đa 30 ngày
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Các API Endpoints cần xây dựng

| Phương thức | Path | Body / Payload | Mô tả |
|-------------|------|----------------|-------|
| `POST` | `/api/v1/trade-check` | `{ symbol, action, price, quantity, stop_loss, take_profit, reason, emotion_text, confidence }` | Tiếp nhận thông tin giao dịch, gọi AI phân tích cảm xúc, tính toán rủi ro và trả về cấu trúc kết quả cùng cờ `should_cooldown`. |
| `POST` | `/api/v1/trade-check/{log_id}/acknowledge` | `{ reflective_answer }` | Người dùng xác nhận kỷ luật bằng cách trả lời câu hỏi tự phản tỉnh, lưu câu trả lời vào DB và mở khóa cho phép thực thi lệnh. |

---

## 4. Logic & Quy tắc xử lý tại Backend

### 4.1. Công thức toán học (Risk/Reward Calculation)
Với lệnh `BUY`, backend tính toán tỷ lệ R:R:
*   $$\text{Risk} = \text{Price} - \text{Stop Loss}$$
*   $$\text{Reward} = \text{Take Profit} - \text{Price}$$
*   Nếu $\text{Risk} \le 0$ hoặc $\text{Reward} \le 0$, trả về lỗi `400 Bad Request` với thông điệp: "Giá trị Stop-loss hoặc Take-profit không hợp lý".
*   $$\text{R:R Ratio} = \text{Reward} / \text{Risk}$$
    Ví dụ: Lợi nhuận gấp 2.4 lần rủi ro, hiển thị tỷ lệ là `1:2.4`.

### 4.2. Tích hợp AI (Gemini/OpenAI API) và Fallback
*   Sử dụng API của OpenRouter hoặc OpenAI/Gemini với chế độ **JSON Mode** để ép dữ liệu trả về theo schema định sẵn.
*   Thiết lập timeout cứng `4.5 giây` cho tác vụ gọi AI.
*   **Luồng Fallback:**
    Nếu gặp ngoại lệ `Timeout` hoặc lỗi API AI:
    * Gán toàn bộ `fomo_score`, `revenge_score`... về `0`.
    * Đặt `discipline_risk = "Low"` và `should_cooldown = False`.
    * Sinh `coach_message` dự phòng: *"Hệ thống không thể phân tích cảm xúc lúc này do sự cố kết nối. Hãy tự rà soát kỹ luật giao dịch của bạn trước khi tiếp tục."*
    * Trả về kết quả rủi ro toán học (R:R) đã tính toán bình thường.

### 4.3. Background Cron Task (Dọn dẹp log)
*   Xây dựng một script dọn dẹp (ví dụ bằng APScheduler chạy nền trong FastAPI hoặc Script độc lập kích hoạt hàng tuần):
    ```python
    # Logic dọn dẹp hàng tuần
    def cleanup_old_logs(db: Session):
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        db.query(EmotionLog).filter(EmotionLog.created_at < thirty_days_ago).delete()
        db.commit()
    ```

---

## 5. Thiết kế các trạng thái Giao diện (UI Flow)

1. **Form nhập thông tin giao dịch (Bento Grid):**
   * Các input `Stop-loss` và `Take-profit` tự động bị `disabled` và xóa giá trị khi người dùng chọn `Action Type: SELL`.
   * Khi chọn `BUY`, nếu `Stop-loss` trống, hiển thị cảnh báo đỏ trực quan dưới trường nhập liệu.
2. **Khối Loading (Backdrop blur):**
   * Phủ toàn màn hình với hiệu ứng mờ kính `backdrop-blur-md` hiển thị trạng thái đang gọi AI.
3. **Màn hình Soft Cooldown (Khóa kỷ luật):**
   * Nếu kết quả trả về `should_cooldown = true`, khóa toàn bộ màn hình bằng Overlay hổ phách.
   * Hiển thị nhận định lỗi cảm xúc của AI và hộp nhập văn bản (textarea) bắt buộc điền câu trả lời tự phản tỉnh.
   * Nút `Acknowledge & Proceed` chỉ sáng lên khi độ dài câu trả lời phản tỉnh tối thiểu là 10 ký tự.
4. **Thông báo Disclaimer mặc định:**
   * Hiển thị cảnh báo pháp lý VN-MVP-v1 dưới chân biểu mẫu: *"Mọi phân tích rủi ro và cảm xúc chỉ mang tính chất tham khảo kỷ luật cá nhân, không cấu thành khuyến nghị giao dịch tài chính."*

---

## 6. Kế hoạch kiểm thử (Verification Plan)

### 6.1. Kiểm thử tự động (Automated Tests)
*   `test_buy_order_rr_calculation`: Kiểm tra công thức tính R:R và chặn lỗi khi nhập SL sai vị trí đối với lệnh mua.
*   `test_sell_order_no_sl_tp`: Xác nhận lệnh SELL không báo lỗi khi để trống SL/TP.
*   `test_ai_timeout_fallback`: Giả lập AI phản hồi chậm hơn 4.5s để xác thực luồng fallback trả về dữ liệu toán học bình thường mà không gây crash API.
*   `test_cooldown_locking_and_acknowledgement`: Xác nhận log được gắn cờ `should_cooldown = true` và chỉ chuyển trạng thái `cooldown_acknowledged = true` sau khi gọi API xác nhận phản tỉnh thành công.

### 6.2. Kiểm thử thủ công (Manual Verification)
1. Thử nhập một lệnh BUY thiếu Stop-loss để kiểm tra cảnh báo trực quan.
2. Nhập một câu miêu tả cảm xúc tiêu cực để kích hoạt Soft Cooldown (ví dụ: *"Vừa lỗ lệnh trước nên quyết định all-in lệnh này để gỡ gạc"*).
3. Xác nhận màn hình Soft Cooldown xuất hiện, nhập câu hỏi phản tỉnh và kiểm tra xem dữ liệu trong cơ sở dữ liệu đã cập nhật câu trả lời phản tỉnh chính xác chưa.
4. Kiểm tra sự xuất hiện của Disclaimer pháp lý ở chân trang.
