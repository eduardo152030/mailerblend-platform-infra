"""
main.py
=======
FastAPI application factory — Phase 2.

This file contains ONLY:
  - FastAPI app creation
  - CORS middleware
  - Router registration

Nothing else. If you find business logic here, it belongs elsewhere.

Where to look for bugs:
  Telegram webhook       → api/telegram_routes.py
  Reminder ACK/cancel    → services/reminder_handlers.py
  Content / pending task → services/content_handlers.py
  Health / ready         → api/health_routes.py
  Attachments            → api/attachment_routes.py
  Tasks CRUD             → api/task_routes.py
  Reminders REST         → api/reminder_routes.py
  Events                 → api/event_routes.py
  Digest                 → api/digest_routes.py
  Auth / admin           → auth.py, users.py
  Publishing             → publishing_channels.py
  Constants / env vars   → core/config.py
  Time utils             → utils/time_utils.py
  Text / intent parsing  → utils/text_utils.py
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import APP_NAME, UPLOADS_DIR

# ── Route modules ─────────────────────────────────────────────────────────
from api.health_routes     import router as health_router
from api.reminder_routes   import router as reminder_router
from api.event_routes      import router as event_router
from api.task_routes       import router as task_router
from api.attachment_routes import router as attachment_router
from api.digest_routes     import router as digest_router
from api.telegram_routes   import router as telegram_router

# ── App factory ───────────────────────────────────────────────────────────
app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(reminder_router)
app.include_router(event_router)
app.include_router(task_router)
app.include_router(attachment_router)
app.include_router(digest_router)
app.include_router(telegram_router)

# ── Auth / Admin / Publishing (existing standalone modules) ───────────────
try:
    from auth import router as auth_router
    from users import router as admin_router
    from publishing_channels import publishing_router
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(publishing_router)
    print("[startup] ✅ auth + admin + publishing routers registered")
except ImportError as _e:
    print(f"[startup] ⚠️  auth modules not loaded: {_e}")

# ── Admin backfill route (one-shot utility) ───────────────────────────────
from api.admin_routes import router as admin_backfill_router
app.include_router(admin_backfill_router)

os.makedirs(UPLOADS_DIR, exist_ok=True)
print(f"[startup] ✅ EVA API ready — {APP_NAME}")
