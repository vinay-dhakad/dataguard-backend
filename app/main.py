from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.websocket import manager
from app.api import events, alerts, users, files, dashboard, exceptions

app = FastAPI(
    title="DataGuard API",
    version="1.0.0",
    description="Real-time employee data exfiltration detection prototype"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"name": "DataGuard", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

app.include_router(events.router)
app.include_router(alerts.router)
app.include_router(users.router)
app.include_router(files.router)
app.include_router(dashboard.router)
app.include_router(exceptions.router)
