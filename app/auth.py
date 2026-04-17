from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Middleware xác thực qua X-API-Key header.
    Chặn request không có key hoặc có key sai.
    Trả về API Key nếu đúng để định danh request.
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include header: X-API-Key: <your-key>",
        )
    if api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key.",
        )
    return api_key
