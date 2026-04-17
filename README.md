# Day 12 Final Project: Production-Ready AI Agent

Dự án này là kết quả trọn vẹn của **Lab 12 - VinUni AICB Bootcamp**.
AI Agent ở repo này đáp ứng các chuẩn Môi trường Production bao gồm Docker hóa Multi-stage, Stateless System (Redis), thiết lập Rate Limiter và tính chi phí Cost Guard, bảo mật API Key.

## Cấu Trúc
- `app/`: Lõi Backend bằng FastAPI.
    - `main.py`: Luồng API xử lý Health Check gộp Dependency Injection.
    - `config.py`: Quản lý các Biến Pydantic Setting 12-Factors.
    - `auth.py`: X-API-Key check.
    - `rate_limiter.py`: Quản lý rate giới hạn theo UserId qua Redis Sliding Logs.
    - `cost_guard.py`: Limit Budget qua Redis TTL.
- `utils/`: Nơi móc nối tới Engine (Sử dụng Mock).
- `Dockerfile`: Multi-stage build.

## Hướng dẫn Chạy (Local Testing)
Để test tại máy của bạn nhanh nhất, bạn cần Docker.
```bash
# Sẽ build và chạy lên App + Redis Service đi kèm
docker compose up -d --build
```
Dịch vụ sẽ sẵn sàng ở `localhost:8000`. Cùng với cấu hình API Key test là `my-super-secret-key-123`.

## Test Health
```bash
curl http://localhost:8000/health
```

## Chạy lên Web (Railway & Render)
Hãy Push mã nguồn lên Github và trỏ cấu hình App của Render / Railway vào. 
Nhớ Inject cấu hình cho Redis.
