from os import getenv

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.crm_access import bearer, crm_auth_enabled, require_crm_access
from app.db import get_pool, close_pool
from app.routers import health

from app.routers.v1.contacts import router as contacts_router
from app.routers.v1.intake import router as intake_router
from app.routers.v1.oportunidades import router as oportunidades_router
from app.routers.v1.pendientes import router as pendientes_router

from app.routers.v1 import timeline
from app.routers.v1 import presupuestos
from app.routers.v1 import utm
from app.routers.v1 import gastos, proveedores

# 🆕 LINKEDIN SOURCING ROUTERS
from app.routers.v1 import linkedin_leads
from app.routers.v1 import linkedin_approvals
from app.routers.v1 import linkedin_conversations_outcomes
from app.routers.v1.linkedin_knowledge_base import router as knowledge_base_router
from app.routers.v1.linkedin_rate_limits import router as rate_limits_router
from app.routers.v1.linkedin_activity_log import router as activity_log_router
from app.routers.v1.linkedin_cooldowns import router as cooldowns_router
from app.routers.v1.linkedin_invite_templates import router as invite_templates_router


app = FastAPI(
    title="Composable CRM API",
    version="v1",
    root_path=settings.crm_base_path or "",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ============================================================
# 🔧 CORS HABILITADO PARA PRUEBAS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in getenv("CRM_UI_ORIGIN", "").split(",") if origin and origin != "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ============================================================

# -----------------------------
# Routers principales
# -----------------------------
def project_access(project):
    def authorize(request: Request, credentials=Depends(bearer)):
        if not crm_auth_enabled():
            return
        access = require_crm_access(credentials)
        write = request.method not in {"GET", "HEAD"}
        if not access.allows_project(project, write=write):
            raise HTTPException(403, "CRM project forbidden")
    return [Depends(authorize)]


form_entries = project_access("form_entries")
smart_management = project_access("smart_management")
linkedin = project_access("linkedin_sourcing")

app.include_router(health.router)
app.include_router(contacts_router, dependencies=form_entries)
app.include_router(intake_router)
app.include_router(oportunidades_router, dependencies=form_entries)
app.include_router(pendientes_router, dependencies=form_entries)

app.include_router(presupuestos.router, dependencies=form_entries)
app.include_router(utm.router, dependencies=form_entries)
app.include_router(gastos.router)
app.include_router(proveedores.router, dependencies=smart_management)

# -----------------------------
# Routers de módulos internos
# -----------------------------
app.include_router(timeline.router, dependencies=form_entries)

# -----------------------------
# 🆕 LINKEDIN SOURCING ROUTERS
# -----------------------------
app.include_router(linkedin_leads.router, dependencies=linkedin)
app.include_router(linkedin_leads.service_router)
app.include_router(linkedin_approvals.router, dependencies=linkedin)
app.include_router(linkedin_conversations_outcomes.router, dependencies=linkedin)
# ── Registrar routers (añadir después de los routers existentes) ──
app.include_router(knowledge_base_router, dependencies=linkedin)
app.include_router(rate_limits_router, dependencies=linkedin)
app.include_router(activity_log_router, dependencies=linkedin)
app.include_router(cooldowns_router, dependencies=linkedin)
app.include_router(invite_templates_router, dependencies=linkedin)

@app.on_event("startup")
async def on_startup() -> None:
    """
    Inicializa el pool de conexiones a la base de datos al arrancar la aplicación.
    """
    await get_pool()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Cierra el pool de conexiones a la base de datos al apagar la aplicación.
    """
    await close_pool()
