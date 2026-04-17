import redis
from datetime import datetime
from fastapi import HTTPException
from .config import settings

r = redis.from_url(settings.redis_url, decode_responses=True)

def check_budget(user_id: str):
    """
    Check budget cost per month ($10 per month mặc định).
    Sử dụng redis INCRBYFLOAT. Trả về Exception 402 nếu quá budget.
    """
    # Chi phí giả định mỗi query tốn chừng $0.01 (Mọi thao tác gọi API Ask đều tốn)
    estimated_cost = 0.01

    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    # Kéo cost đã dùng xuống
    current = r.get(key)
    current = float(current) if current else 0.0

    if current + estimated_cost > settings.monthly_budget_usd:
        raise HTTPException(
            status_code=402, 
            detail=f"Payment Required. Vượt quá budget {settings.monthly_budget_usd}$/tháng của bạn."
        )
    
    # Lưu lại budget mới lên
    r.incrbyfloat(key, estimated_cost)
    # Giữ lưu cache trong đúng 1 tháng + 1 xíu dằn túi (~32 ngày)
    r.expire(key, 32 * 24 * 3600)
    
    return True
