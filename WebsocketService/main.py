from fastapi import FastAPI, WebSocket
from manager import manager

app = FastAPI()

@app.websocket("/ws/{simulation_id}")
async def websocket_endpoint(websocket: WebSocket, simulation_id: int):
    await manager.connect(simulation_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(simulation_id)