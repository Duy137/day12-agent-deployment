# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **Hardcode API Key**: Tại file `basic/app.py`, biến `OPENAI_API_KEY = "sk-hardcoded..."` được gán cứng, nếu đẩy lên GitHub dễ bị đánh cắp key.
2. **Không có Config Management**: Các biến `DEBUG`, `MAX_TOKENS`, cấu hình Database... được set thẳng trong code, khó chỉnh sửa mà không restart/deploy lại.
3. **Sử dụng lệnh Print thay vì proper Logging**: Lệnh print không cho ta thông tin thời gian, độ nghiêm trọng, không thể theo dõi trên các log tracking platform như Loki hoặc Datadog. Có nguy cơ in cả secrets ra log.
4. **Không có endpoint Health Check**: Làm cho Cloud Engine / Load balancer không biết khi nào Agent bị crash, không thể tự khởi động lại.
5. **Cứng Port và Host**: Code chạy `"localhost"` cản trợ khả năng nhận connect từ ngoài container. Port `8000` cố định, làm mất khả năng để Railway hay Cloud tự inject PORT rỗng vào.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode trong file | Sử dụng `os.getenv` \ `.env` | Tránh lộ secret, dễ đổi config ở env test/prod. |
| Health check| Không | Có `/health`, `/ready` endpoints | Giúp hệ thống tự động rollback, restart khi app treo. |
| Logging | Sử dụng `print()` đơn giản | Sử dụng `logging` định dạng JSON| Truy xuất dễ dàng, phân tích error logs 1 cách tự động. |
| Shutdown | Tắt đột ngột (CTRL+C) / Kill | Graceful Shutdown qua Signal | Giúp xử lý nốt các Request đang dang dở, tránh mất data người dùng (VD: bill card). |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.11` (bản chuẩn đầy đủ).
2. Working directory: `/app`
3. Tại sao COPY requirements.txt trước? Để tận dụng Docker cache layer. Vì code file thay đổi liên tục nhưng requirements thường ít đổi, cache step cài đặt library sẽ giúp build Docker lần tiếp theo rất nhanh chóng.
4. CMD vs ENTRYPOINT: `CMD` cung cấp lệnh default có thể dễ dàng bị override bằng đối số khi `docker run`, trong khi `ENTRYPOINT` định nghĩa app sẽ luôn chạy lệnh này (giống command gốc) cứng rắn hơn.

### Exercise 2.3: Image size comparison
- Develop: ~1000 MB (Vì mang theo cả gcc, toolchains biên dịch)
- Production: ~150-300 MB (Multi-stage layer loại bỏ toàn bộ file rác cài đặt)
- Difference: ~ 70-85% (Tiết kiệm lượng lớn dung lượng và giảm diện tích tấn công)

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: `https://...railway.app` (xem chi tiết ở DEPLOYMENT.md)
- Screenshot: (Xem trong thư mục screenshots)

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- API trả về HTTP `401 Unauthorized` nếu không cung cấp API Key.
- Khi cung cấp `X-API-Key`, request thực hiện thành công (`200 OK`).
- Khi test Spam liên tục, Rate limiter kích hoạt và trả về `429 Too Many Requests`.

### Exercise 4.4: Cost guard implementation
Sử dụng Redis làm Data Store. Mỗi lần user dùng app sẽ ước tính cost. Nếu tổng budget của User_ID lưu ở Redis pass qua $10 thì từ chối xử lý request bằng việc trả về HTTP `402 Payment Required`. Sử dụng cơ chế TTL ở redis key theo định dạng tháng. `budget:user_id:YYYY-MM`.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- Việc sử dụng `/health` và `Graceful shutdown` qua hàm Context Async Lifespan đảm bảo cho Container luôn được theo dõi, request nào bắt đầu thì sẽ đợi kết thúc.
- State được dời ra ngoài Redis, do vậy có thể start nhiều container Agent (Scalability) chạy song song và cân bằng tải qua Nginx mà không gặp tình trạng người dùng request vào Container 2 bị bắt học lại từ đầu (State nằm ở Redis chung chứ ko nằm Memory cục bộ).
