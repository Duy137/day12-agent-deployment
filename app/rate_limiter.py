import time
import redis
from fastapi import HTTPException
from .config import settings

# Khởi tạo kết nối Redis tĩnh
r = redis.from_url(settings.redis_url, decode_responses=True)

def check_rate_limit(user_id: str):
    """
    Sliding window trên Redis.
    Giới hạn user có thể call max N req/min (thừa hưởng từ env variable).
    """
    now = time.time()
    window_seconds = 60
    max_requests = settings.rate_limit_per_minute
    
    key = f"rate_limit:{user_id}"

    # Pipeline để gửi lệnh Redis liền mạch Atomic
    pipeline = r.pipeline()
    
    # 1. Clean up logs cũ đã qua cửa sổ thời gian
    pipeline.zremrangebyscore(key, 0, now - window_seconds)
    
    # 2. Đếm số lệnh còn lại
    pipeline.zcard(key)
    
    # 3. Add thời điểm request mới này vào (score, member)
    pipeline.zadd(key, {str(now): now})
    
    # 4. Set expire 60s trên root key để khỏi tốn RAM
    pipeline.expire(key, window_seconds)
    
    results = pipeline.execute()
    current_count = results[1]
    
    if current_count >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {max_requests} requests per minute."
        )
    
    return True
