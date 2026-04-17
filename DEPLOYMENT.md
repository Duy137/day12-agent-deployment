# Deployment Information

## Public URL
- `https://your-agent.railway.app`
*(Hãy thay URL ở trên bằng URL Cloud thật của bạn)*

## Platform
- Render / Railway

## Test Commands

### Health Check (Kiểm tra xem hệ thống đã sống chưa)
```bash
curl https://your-agent.railway.app/health
```
*(Kỳ vọng API trả về : {"status": "ok", ...})*

### API Test (Test request thành công)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: my-super-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "SV01", "question": "Hệ Mặt Trời có mấy hành tinh?"}'
```

### Rate Limiting Test (Test gửi 15 lượt gọi nhanh liên tiếp)
```bash
for i in {1..15}; do 
  curl -H "X-API-Key: my-super-secret-key-123" https://your-agent.railway.app/ask \
    -X POST -d '{"user_id":"test_limit","question":"test"}'; 
done
```
*(Kỳ vọng từ request thứ 11 trả đi nhận được lỗi HTTP 429)*

## Environment Variables Set
Tại môi trường Production (Dashboard của Railway / Render), các Env Variable sau đã được set:
- `PORT=8000`
- `REDIS_URL=redis://...`  *(Đường dẫn URL service Redis Internal)*
- `AGENT_API_KEY=my-super-secret-key-123`
- `LOG_LEVEL=INFO`

## Screenshots
Xin mời xem các file trong thư mục `screenshots/`:
- `[✅] Cấu hình Deployment dashboard`
- `[✅] Service đang running`
- `[✅] Result test (Terminal)`
