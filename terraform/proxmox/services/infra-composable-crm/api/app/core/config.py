import os
from pydantic import BaseModel

class Settings(BaseModel):
    crm_db_dsn: str = os.getenv("CRM_DB_DSN", "")
    crm_api_key: str = os.getenv("CRM_API_KEY", "")
    # prod behind nginx: "/api"
    # local dev: ""
    crm_base_path: str = os.getenv("CRM_BASE_PATH", "")

settings = Settings()
