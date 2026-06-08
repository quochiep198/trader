# Đặc tả con: Market Context Discipline Check

> Parent spec: `spec-pack-updated-market-context.md`  
> Module: `market-context-discipline-check`  
> Status: Draft for implementation  
> Version: v0.1  
> Mục tiêu: Bổ sung dữ liệu giá hiện tại và nhiều phiên vào Pre-trade Check để cảnh báo kỷ luật/cảm xúc, không tạo tín hiệu mua/bán.

---

## 1. Mục tiêu

Market Context Discipline Check giúp TradeMind AI kiểm tra xem bối cảnh giá hiện tại và nhiều phiên gần nhất có đang kích hoạt cảm xúc giao dịch không.

Các trạng thái cần phát hiện:

- FOMO do giá tăng nhanh nhiều phiên.
- Mua đuổi so với kế hoạch entry.
- Panic do giá giảm nhanh nhiều phiên.
- Gần stop-loss và có nguy cơ dời stop-loss vì cảm xúc.
- Gần take-profit và có nguy cơ chốt lời cảm tính.
- Dữ liệu giá stale/unavailable để tránh cảnh báo sai.

Module này **không**:

- Không khuyến nghị mua/bán.
- Không dự đoán giá.
- Không cam kết lợi nhuận.
- Không đặt lệnh.
- Không thay thế quyết định của người dùng.

---

## 2. Phạm vi MVP

### Trong phạm vi

| # | Chức năng | Mô tả |
|---|---|---|
| 1 | Fetch market snapshot | Lấy giá hiện tại hoặc giá gần nhất cho symbol. |
| 2 | Fetch OHLCV sessions | Lấy dữ liệu nhiều phiên, tối thiểu 20 phiên nếu provider hỗ trợ. |
| 3 | Compute price metrics | Tính % thay đổi 1D/3D/5D/20D, chuỗi tăng/giảm, volume ratio. |
| 4 | Compare with trade plan | So sánh current_price với entry_price, stop_loss, take_profit. |
| 5 | Generate market warnings | Tạo warning code như market_fomo_context, buying_chase_risk, panic_context. |
| 6 | Extend POST /trade-check | Trả thêm object `market_context`. |
| 7 | Fallback | Nếu market data lỗi/stale thì không làm hỏng pre-trade check. |

### Ngoài phạm vi

| # | Ngoài phạm vi | Lý do |
|---|---|---|
| 1 | Realtime streaming giá | MVP chỉ cần snapshot/near-realtime hoặc delayed data. |
| 2 | Broker integration | Trái với scope MVP hiện tại. |
| 3 | Buy/sell signal | Trái AI Guardrails. |
| 4 | Price prediction | Trái AI Guardrails. |
| 5 | Technical analysis nâng cao | Để roadmap sau. |
| 6 | Auto alert background phức tạp | MVP chỉ kiểm tra khi user submit/check. |

---

## 3. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| Market Snapshot | Một bản ghi giá gần nhất của symbol tại thời điểm fetch. |
| OHLCV | Open, High, Low, Close, Volume của từng phiên. |
| Multi-session Metrics | Các chỉ số tính từ nhiều phiên như 3D/5D/20D change, chuỗi tăng/giảm. |
| Market Warning | Cảnh báo kỷ luật dựa trên bối cảnh giá. |
| Fresh Data | Dữ liệu đủ mới theo ngưỡng cấu hình. |
| Stale Data | Dữ liệu quá cũ, không nên dùng để tạo cảnh báo mạnh. |
| Unavailable Data | Không lấy được dữ liệu giá. |

---

## 4. Business Rules

| ID | Rule | Acceptance Criteria |
|---|---|---|
| R-MKT-1 | Market context chỉ dùng để cảnh báo kỷ luật/cảm xúc, không tạo khuyến nghị mua/bán. | AC-MKT-6 |
| R-MKT-2 | Backend tính toàn bộ price metrics bằng code; AI không tự tính số liệu giá. | AC-MKT-2 |
| R-MKT-3 | Nếu market data lỗi/stale/unavailable, pre-trade check vẫn chạy bằng risk/rule/emotion hiện có. | AC-MKT-5 |
| R-MKT-4 | Giá tăng mạnh nhiều phiên + FOMO score cao tạo warning `market_fomo_context`. | AC-MKT-3 |
| R-MKT-5 | Current price cao hơn planned entry đáng kể tạo warning `buying_chase_risk`. | AC-MKT-3 |
| R-MKT-6 | Giá giảm mạnh nhiều phiên + Panic score cao tạo warning `panic_context`. | AC-MKT-4 |
| R-MKT-7 | Giá gần stop-loss tạo warning `near_stop_loss`; wording nhắc người dùng không dời SL vì cảm xúc. | AC-MKT-2, AC-MKT-6 |
| R-MKT-8 | Giá gần take-profit tạo warning `near_take_profit`; wording nhắc người dùng kiểm tra kế hoạch thoát. | AC-MKT-2, AC-MKT-6 |
| R-MKT-9 | Market warnings không hard block người dùng. | AC-MKT-6 |
| R-MKT-10 | Market warnings mang tính chất cảnh báo bối cảnh hành vi và hỗ trợ AI Coach, không trừ điểm kỷ luật (discipline_score) của Rule Engine và không trực tiếp kích hoạt cooldown (trừ phi điểm số cảm xúc vượt ngưỡng quy định sẵn). | AC-MKT-6 |

---

## 5. Metrics cần tính

### 5.1 Input cần có

```json
{
  "symbol": "HPG",
  "action": "BUY",
  "entry_price": 28500,
  "quantity": 1000,
  "stop_loss": 27200,
  "take_profit": 31000,
  "emotion_scores": {
    "fomo_score": 8,
    "panic_score": 1,
    "revenge_score": 0
  }
}
```

### 5.2 Market data input từ provider

```json
{
  "symbol": "HPG",
  "current_price": 29500,
  "fetched_at": "2026-06-08T10:30:00+07:00",
  "sessions": [
    {
      "session_date": "2026-06-08",
      "open": 28900,
      "high": 29600,
      "low": 28800,
      "close": 29500,
      "volume": 20000000
    }
  ]
}
```

### 5.3 Computed metrics

| Metric | Type | Logic |
|---|---:|---|
| current_price | number | Giá gần nhất từ provider. |
| price_change_1d | number | `(current_price - close_1d_ago) / close_1d_ago * 100`. |
| price_change_3d | number | `(current_price - close_3d_ago) / close_3d_ago * 100`. |
| price_change_5d | number | `(current_price - close_5d_ago) / close_5d_ago * 100`. |
| price_change_20d | number | `(current_price - close_20d_ago) / close_20d_ago * 100`. |
| consecutive_up_sessions | integer | Đếm số phiên close tăng liên tiếp gần nhất. |
| consecutive_down_sessions | integer | Đếm số phiên close giảm liên tiếp gần nhất. |
| volume_vs_20d_avg | number | `latest_volume / avg(volume_last_20_sessions)`. |
| current_vs_entry_percent | number | Đối với `BUY`: `(current_price - entry_price) / entry_price * 100`. <br> Đối với `SELL_TO_CLOSE`: `(current_price - average_entry_price) / average_entry_price * 100`. |
| distance_to_stop_loss_percent | number/null | Với `BUY` có SL: `(current_price - stop_loss) / current_price * 100`. <br> Với `SELL_TO_CLOSE`: `null` (không áp dụng). |
| distance_to_take_profit_percent | number/null | Với `BUY` có TP: `(take_profit - current_price) / current_price * 100`. <br> Với `SELL_TO_CLOSE`: `null` (không áp dụng). |
| data_status | enum | **fresh**: Dữ liệu mới nhất. Trong giờ giao dịch (T2-T6, 9:00-15:00), trễ < 15 phút. Ngoài giờ giao dịch hoặc cuối tuần, giá đóng cửa của phiên gần nhất được coi là fresh. <br> **stale**: Dữ liệu trễ > 15 phút trong giờ giao dịch, hoặc thiếu dữ liệu của phiên gần nhất ngoài giờ. <br> **unavailable**: Không lấy được dữ liệu. |

---

## 6. Warning Logic MVP

| Warning code | Điều kiện gợi ý | Risk level | Coach direction |
|---|---|---|---|
| market_fomo_context | `price_change_3d >= 7` hoặc `consecutive_up_sessions >= 3`, và `fomo_score >= 6` | high | Nhắc user kiểm tra FOMO, không mua đuổi. |
| buying_chase_risk | `current_vs_entry_percent >= 3` với action BUY | medium/high | Nhắc user cập nhật lại entry/SL/risk nếu giá đã vượt kế hoạch. |
| panic_context | `price_change_3d <= -7` hoặc `consecutive_down_sessions >= 3`, và `panic_score >= 6` | high | Nhắc user kiểm tra panic, không bán vì hoảng loạn. |
| near_stop_loss | `0 < distance_to_stop_loss_percent <= 2` với action BUY | medium | Nhắc user không dời stop-loss vì không muốn chấp nhận sai. |
| near_take_profit | `0 < distance_to_take_profit_percent <= 2` với action BUY | low/medium | Nhắc user kiểm tra kế hoạch chốt lời thay vì sợ mất lãi. |
| volume_spike_context | `volume_vs_20d_avg >= 2` | medium | Nhắc user cẩn trọng với biến động mạnh gây cảm xúc. |
| stale_market_data | `data_status = stale` | low | Không tạo warning mạnh dựa trên giá. |
| unavailable_market_data | `data_status = unavailable` | low | Không ảnh hưởng check core. |

> **Ghi chú về luồng xử lý (Giải quyết Circular Dependency):** 
> 1. Để tránh vòng lặp phụ thuộc, backend sẽ tính toán các chỉ số giá trước, sau đó gửi các chỉ số này sang AI Coach. 
> 2. AI Coach thực hiện phân tích cảm xúc từ lý do của người dùng kết hợp với bối cảnh giá để trả về điểm cảm xúc (`fomo_score`, `panic_score`...) và `coach_message`.
> 3. Sau khi AI trả về kết quả, backend sẽ kết hợp điểm cảm xúc và chỉ số giá để xác định danh sách `market_warnings` chính thức nhằm hiển thị trên UI và lưu log.
> 4. Các cảnh báo này hoàn toàn mang tính thông tin hỗ trợ hành vi, không tính điểm phạt vào `discipline_score` của Rule Engine. Ngưỡng 7%, 3%, 2%, 2x là cấu hình MVP, có thể đưa vào env/config để điều chỉnh sau.

---

## 7. API Design

### 7.1 GET /market/snapshot

Lấy snapshot và metrics cơ bản cho một symbol.

#### Query params

```text
symbol=HPG
sessions=20
```

#### Response thành công

```json
{
  "symbol": "HPG",
  "provider": "market_provider_name",
  "current_price": 29500,
  "fetched_at": "2026-06-08T10:30:00+07:00",
  "data_status": "fresh",
  "price_change_1d": 2.1,
  "price_change_3d": 8.2,
  "price_change_5d": 11.4,
  "price_change_20d": 18.6,
  "consecutive_up_sessions": 3,
  "consecutive_down_sessions": 0,
  "volume_vs_20d_avg": 2.1
}
```

### 7.2 POST /market/context-check

Dùng để test riêng Market Context trước khi tích hợp vào trade-check.

#### Request

```json
{
  "symbol": "HPG",
  "action": "BUY",
  "entry_price": 28500,
  "stop_loss": 27200,
  "take_profit": 31000,
  "emotion_scores": {
    "fomo_score": 8,
    "panic_score": 1,
    "revenge_score": 0
  }
}
```

#### Response

```json
{
  "market_context": {
    "symbol": "HPG",
    "current_price": 29500,
    "price_change_1d": 2.1,
    "price_change_3d": 8.2,
    "price_change_5d": 11.4,
    "price_change_20d": 18.6,
    "consecutive_up_sessions": 3,
    "consecutive_down_sessions": 0,
    "volume_vs_20d_avg": 2.1,
    "current_vs_entry_percent": 3.5,
    "distance_to_stop_loss_percent": 7.8,
    "distance_to_take_profit_percent": 4.9,
    "data_status": "fresh",
    "market_context_risk": "high",
    "market_warnings": [
      "market_fomo_context",
      "buying_chase_risk",
      "volume_spike_context"
    ],
    "message": "Giá đã tăng mạnh nhiều phiên và đang cao hơn entry dự kiến. Đây là bối cảnh dễ kích hoạt FOMO, không phải tín hiệu mua/bán."
  }
}
```

### 7.3 POST /trade-check extension

`POST /trade-check` mở rộng response bằng field:

```json
{
  "market_context": {
    "data_status": "fresh",
    "market_context_risk": "high",
    "market_warnings": ["market_fomo_context"],
    "message": "..."
  }
}
```

---

## 8. Data Model

### 8.1 market_snapshots

```text
id
symbol
provider
current_price
open_price
high_price
low_price
close_price
volume
session_date
data_status
fetched_at
created_at
```

### 8.2 market_context_logs

Bản ghi bối cảnh giá được lưu **ngay khi thực hiện pre-trade check** để bảo toàn lịch sử bối cảnh của tất cả các lượt check.

```text
id
user_id
emotion_log_id        (UUID, ForeignKey liên kết với emotion_logs.id, nullable=False)
trade_id              (UUID, ForeignKey liên kết với trades.id, nullable=True, cập nhật khi trade được ghi nhận vào nhật ký)
symbol
current_price
price_change_1d
price_change_3d
price_change_5d
price_change_20d
consecutive_up_sessions
consecutive_down_sessions
volume_vs_20d_avg
current_vs_entry_percent
distance_to_stop_loss_percent
distance_to_take_profit_percent
data_status
market_context_risk
market_warnings
message
created_at
```

### 8.3 Relationship & Alignment

* Khi thực hiện `POST /trade-check`, backend đồng thời tạo một bản ghi `EmotionLog` và một bản ghi `MarketContextLog` liên kết qua `emotion_log_id`.
* Khi người dùng lưu giao dịch vào nhật ký (chuyển đổi kết quả check thành một giao dịch thực tế trong bảng `trades`), hệ thống sẽ cập nhật trường `trade_id` cho cả `EmotionLog` và `MarketContextLog`. Bảng `trades` cũng có thể lưu thêm khóa ngoại nullable `market_context_log_id` để tiện truy vấn 1-1.

---

## 9. Service Design

### 9.1 Backend modules

```text
services/
  market_data_service.py
  market_context_analyzer.py
  market_context_messages.py
  ai_service.py
  risk_service.py
  rule_engine.py
```

### 9.2 MarketDataProvider interface

```python
class MarketDataProvider:
    async def get_snapshot(self, symbol: str) -> dict:
        raise NotImplementedError

    async def get_ohlcv_sessions(self, symbol: str, sessions: int = 20) -> list[dict]:
        raise NotImplementedError
```

### 9.3 MarketContextAnalyzer interface

```python
class MarketContextAnalyzer:
    def compute_metrics(self, trade_input: dict, market_data: dict) -> dict:
        raise NotImplementedError

    def generate_warnings(self, metrics: dict, emotion_scores: dict) -> dict:
        raise NotImplementedError
```

---

## 10. AI Prompt Contract

AI không nhận raw OHLCV dài nếu không cần. Backend chỉ gửi metrics đã tính toán để tránh vòng lặp phụ thuộc chéo (circular dependency). AI sẽ thực hiện đánh giá cảm xúc và phản hồi huấn luyện viên trong một lượt gọi.

### Input cho AI Coach

```json
{
  "trade_input": {
    "symbol": "HPG",
    "action": "BUY",
    "entry_price": 28500,
    "stop_loss": 27200,
    "take_profit": 31000,
    "reason": "Tôi sợ nó chạy mất",
    "emotion_text": "Đang FOMO"
  },
  "market_context": {
    "current_price": 29500,
    "price_change_3d": 8.2,
    "consecutive_up_sessions": 3,
    "volume_vs_20d_avg": 2.1,
    "current_vs_entry_percent": 3.5,
    "data_status": "fresh"
  },
  "guardrails": [
    "Do not recommend buy or sell",
    "Do not predict price",
    "Do not promise profit",
    "Only provide discipline coaching"
  ]
}
```

### Output mong muốn từ AI

AI phân tích bối cảnh và tự quyết định điểm số cảm xúc cùng thông điệp phản hồi:

```json
{
  "emotion_tags": ["FOMO", "Urgency"],
  "fomo_score": 8,
  "panic_score": 1,
  "revenge_score": 0,
  "overconfidence_score": 4,
  "greed_score": 3,
  "hesitation_score": 1,
  "discipline_risk": "high",
  "should_cooldown": true,
  "coach_message": "Giá đã tăng mạnh trong nhiều phiên và đang cao hơn vùng entry bạn dự kiến. Kết hợp với cảm xúc FOMO bạn tự nhận định, đây là bối cảnh dễ dẫn đến mua đuổi. Hãy tạm dừng, kiểm tra lại kế hoạch giao dịch của bạn trước khi quyết định.",
  "reflection_question": "Nếu giao dịch này đi ngược lại kỳ vọng và chạm stop-loss, bạn có sẵn sàng chấp nhận mức lỗ lớn hơn do mua đuổi ở vùng giá này không?",
  "guardrail_safe": true
}
```

---

## 11. UI Requirements

### 11.1 Pre-trade form card

Thêm card:

```text
+------------------------------------------------+
| Market Context                                 |
|------------------------------------------------|
| Current price: 29,500                          |
| 1D: +2.1% | 3D: +8.2% | 5D: +11.4%           |
| Streak: 3 up sessions                          |
| Volume: 2.1x 20D avg                           |
| Plan distance: +3.5% above entry               |
| Warning: Market FOMO Context                   |
|------------------------------------------------|
| Not a buy/sell signal. Discipline context only.|
+------------------------------------------------+
```

### 11.2 Result screen

Hiển thị section:

```text
Market Context Warning
Giá đã tăng 3 phiên liên tiếp và cao hơn entry dự kiến. Điều này có thể làm tăng rủi ro FOMO/mua đuổi nếu bạn đang quyết định vì sợ bỏ lỡ.
```

### 11.3 Fallback UI

```text
Không có dữ liệu giá đủ mới. Kết quả hiện chỉ dựa trên rule, risk và cảm xúc bạn nhập.
```

---

## 12. Acceptance Criteria

| ID | Mô tả | Test |
|---|---|---|
| AC-MKT-1/v1 | Lấy được current price và OHLCV nhiều phiên cho symbol hợp lệ khi provider khả dụng. | IT, E2E |
| AC-MKT-2/v1 | Backend tính được toàn bộ metrics bắt buộc bằng code, không dùng AI. | UT, IT |
| AC-MKT-3/v1 | Giá tăng mạnh nhiều phiên + FOMO score cao tạo warning đúng nhưng không khuyên mua/bán. | UT, IT, E2E, BB |
| AC-MKT-4/v1 | Giá giảm mạnh nhiều phiên + Panic score cao tạo warning đúng nhưng không khuyên bán. | UT, IT, E2E, BB |
| AC-MKT-5/v1 | Market data lỗi/stale/unavailable không làm hỏng Pre-trade Check. | UT, IT, E2E |
| AC-MKT-6/v1 | Market Context không dự đoán giá, không cam kết lợi nhuận, không tạo broker order. | UT, IT, E2E, BB |

---

## 13. Test Cases gợi ý

| Case | Input | Expected |
|---|---|---|
| FOMO tăng 3 phiên | price_change_3d=8.2, up_sessions=3, fomo_score=8 | market_fomo_context, buying_chase_risk nếu current_vs_entry>=3 |
| Panic giảm 3 phiên | price_change_3d=-8.5, down_sessions=3, panic_score=8 | panic_context |
| Giá gần SL | distance_to_stop_loss_percent=1.5 | near_stop_loss |
| Giá gần TP | distance_to_take_profit_percent=1.2 | near_take_profit |
| Volume spike | volume_vs_20d_avg=2.4 | volume_spike_context |
| Data stale | data_status=stale | stale_market_data, không tăng warning mạnh |
| Data unavailable | provider timeout | unavailable_market_data, trade-check vẫn trả result core |
| Guardrail | Any context | Không có từ “nên mua”, “nên bán”, “chắc chắn tăng”, “all-in” |

---

## 14. Implementation Notes

### 14.1 Nguồn dữ liệu

Trong giai đoạn dev có thể dùng provider thử nghiệm/dummy data để hoàn thiện flow. Khi production cần dùng nguồn dữ liệu có license rõ ràng cho thị trường Việt Nam.

### 14.2 Feature flags

```env
MARKET_CONTEXT_ENABLED=true
MARKET_CONTEXT_PROVIDER=mock
MARKET_CONTEXT_TIMEOUT_SECONDS=2.0
MARKET_CONTEXT_STALE_AFTER_MINUTES=15
MARKET_FOMO_3D_CHANGE_THRESHOLD=7
MARKET_CHASE_ENTRY_DISTANCE_THRESHOLD=3
MARKET_NEAR_SL_THRESHOLD=2
MARKET_NEAR_TP_THRESHOLD=2
```

### 14.3 Rollout đề xuất

| Phase | Nội dung |
|---|---|
| Phase A | Mock provider + analyzer unit tests. |
| Phase B | Integrate POST /market/context-check. |
| Phase C | Extend POST /trade-check response. |
| Phase D | Add UI Market Context card. |
| Phase E | Add market context logs + audit. |

---

## 15. Definition of Done

Module được xem là hoàn thành khi:

- Có provider interface và mock provider.
- Tính đúng các metrics bằng các unit tests.
- Tạo đúng mã warning theo các test cases cụ thể trên backend sau khi AI trả về kết quả cảm xúc.
- Tích hợp thành công và mở rộng response của `POST /trade-check` an toàn.
- UI hiển thị Market Context card và fallback khi dữ liệu cũ/ngoại tuyến.
- Không vi phạm AI Guardrails.
- Lỗi kết nối hoặc dữ liệu thị trường không làm hỏng luồng pre-trade check cốt lõi.
- Lưu trữ thành công bản ghi `market_context_logs` đồng thời với `EmotionLog` khi người dùng chạy pre-trade check và cập nhật liên kết `trade_id` khi lưu nhật ký thành công.
