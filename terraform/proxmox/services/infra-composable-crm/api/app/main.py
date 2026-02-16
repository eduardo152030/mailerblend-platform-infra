from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 🔧 CORS para pruebas

from app.core.config import settings
from app.db import get_pool, close_pool
from app.routers import health

from app.routers.v1.contacts import router as contacts_router
from app.routers.v1.intake import router as intake_router
from app.routers.v1.oportunidades import router as oportunidades_router
from app.routers.v1.pendientes import router as pendientes_router

from app.routers.v1 import timeline
from app.routers.v1 import presupuestos  # 👈 NUEVO: módulo presupuestos
from app.routers.v1 import utm
from app.routers.v1 import gastos, proveedores



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
# ⚠️ ADVERTENCIA: Esto permite peticiones desde cualquier origen
# Para eliminar CORS: comentar o borrar las siguientes 2 líneas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ============================================================

# -----------------------------
# Routers principales
# -----------------------------
app.include_router(health.router)
app.include_router(contacts_router)
app.include_router(intake_router)
app.include_router(oportunidades_router)
app.include_router(pendientes_router)

# 👇 NUEVO: registrar presupuestos
app.include_router(presupuestos.router)
app.include_router(utm.router)
app.include_router(gastos.router)
app.include_router(proveedores.router)

# -----------------------------
# Routers de módulos internos
# -----------------------------
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