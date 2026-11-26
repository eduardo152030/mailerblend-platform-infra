"""Web-only API with GoTrue authorization on every business route."""

from fastapi import Depends, FastAPI
from fastapi.routing import APIRouter

from api.attachment_routes import router as attachments
from api.reminder_routes import router as reminders
from api.task_routes import router as tasks
from api.ui_board_routes import router as boards
from api.ui_session_routes import require_ui_owner, router as sessions
from publishing_channels import publishing_router

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/health")
async def health():
    return {"status": "ok"}


task_list = APIRouter()
task_list.routes = [route for route in reminders.routes if route.path == "/tasks"]
for router in (task_list, tasks, attachments, publishing_router):
    app.include_router(router, dependencies=[Depends(require_ui_owner)])
app.include_router(sessions)
app.include_router(boards)
