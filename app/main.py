import time
import json
import logging
import signal
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Optional
from pydantic import BaseModel

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import redis

from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget
# Lưu ý: do utils đứng ngoài thư mục package Python nên khi copy lên repo ta có cách import chéo hoặc copy thẳng.
# Trong case này vì utils nằm cùng cấp trên level cha, ta xài PYTHONPATH=/app trong docker xử lý
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from utils.mock_llm import ask
except ImportError:
    # Dự phòng giả tạo nếu không tìm thấy module utils
    def ask(q): return f"Mocked reply for: {q}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# State
START_TIME = time.time()
_is_ready = False
_in_flight_requests = 0

r = redis.from_url(settings.redis_url, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info("Agent is booting up...")
    
    # Setup - ping tới Redis
    try:
        r.ping()
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.error(f"Cannot connect to Redis: {e}")

    # Đánh dấu ready
    _is_ready = True
    logger.info("✅ Agent ready.")
    
    yield

    # Teardown / Graceful Shutdown
    _is_ready = False
    logger.info("🔄 Initiating Graceful Shutdown...")

    timeout = 30
    elapsed = 0
    while _in_flight_requests > 0 and elapsed < timeout:
        logger.info(f"Waiting for {_in_flight_requests} requests to finish...")
        time.sleep(1)
        elapsed += 1

    logger.info("✅ Graceful Shutdown Completed.")

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

@app.middleware("http")
async def track_in_flight_requests(request: Request, call_next):
    global _in_flight_requests
    _in_flight_requests += 1
    try:
        return await call_next(request)
    finally:
        _in_flight_requests -= 1

# -- Endpoints ---

@app.get("/health")
def health_endpoint():
    """Liveness probe. Luôn trả về 200 OK nếu process còn sống."""
    return {"status": "ok", "uptime_seconds": round(time.time() - START_TIME, 1)}

@app.get("/ready")
def ready_endpoint():
    """Readiness probe. Check dependencies như Redis."""
    if not _is_ready:
        raise HTTPException(status_code=503, detail="Service not initialized.")
    try:
        r.ping()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Dependencies (Redis) failure: {e}")
    return {"status": "ready"}

class AskRequest(BaseModel):
    user_id: str
    question: str

@app.post("/ask")
def ask_agent(
    payload: AskRequest,
    _key: str = Depends(verify_api_key),
):
    """
    Core AI Agent logic với Stateless design
    - Require Header X-API-Key
    - Đã xác nhận cost guard và rate limiter
    """
    user_id = payload.user_id
    question = payload.question
    
    # 1. Gọi hệ thống Redis Limits
    check_rate_limit(user_id)
    check_budget(user_id)
    
    # 2. Xử lý Logic trò chuyện (Mock logic)
    history_key = f"chat_history:{user_id}"
    history = r.lrange(history_key, 0, -1)
    
    logger.info(f"User {user_id} requested: '{question}'. Past messages: {len(history)}")
    
    # Call Mock Model
    answer = ask(question)
    
    # 3. Stateless lưu Log quay lại Local Store của hệ thống Redis (Bảo vệ bộ nhớ Server App)
    r.rpush(history_key, f"Q: {question}", f"A: {answer}")
    r.expire(history_key, 24 * 3600)  # Lịch sử biến mất mất sau 24h
    
    return {
        "user_id": user_id,
        "question": question,
        "answer": answer
    }
