from fastapi import FastAPI

from app.core.config import settings
from app.db import get_pool, close_pool
from app.routers import health
from app.routers.v1.contacts import router as contacts_router
from app.routers.v1.intake import router as intake_router
from app.routers.v1.oportunidades import router as oportunidades_router
from app.routers.v1.pendientes import router as pendientes_router
from app.routers.v1 import timeline

app = FastAPI(
    title="Composable CRM API",
    version="v1",
    root_path=settings.crm_base_path or "",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Routers principales
app.include_router(health.router)
app.include_router(contacts_router)
app.include_router(intake_router)
app.include_router(oportunidades_router)
app.include_router(pendientes_router)

# Routers de módulos internos
app.include_router(timeline.router)

@app.on_event("startup")
async def on_startup() -> None:
    """
    Inicializa el pool de conexiones a la base de datos al arrancar la aplicación.
    Esto ayuda a detectar errores de conexión tempranamente durante el despliegue.
    """
    await get_pool()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Cierra el pool de conexiones a la base de datos al apagar la aplicación.
    """
    await close_pool()