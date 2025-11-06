from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import manager

router = APIRouter()

@router.websocket("/live")
async def live_updates(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # optional keepalive
    except WebSocketDisconnect:
        manager.disconnect(ws)
