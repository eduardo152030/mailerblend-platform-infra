from fastapi import Header, HTTPException
from app.core.config import settings

def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if not settings.crm_api_key:
        raise HTTPException(status_code=500, detail="CRM_API_KEY not configured")
    if x_api_key != settings.crm_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
