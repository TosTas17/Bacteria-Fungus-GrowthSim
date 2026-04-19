class ConnectionManager:
    def __init__(self):
        self.active = {}  # {sim_id: [ws1, ws2, ...]}

    async def connect(self, sim_id, websocket):
        await websocket.accept()
        self.active.setdefault(sim_id, []).append(websocket)

    def disconnect(self, sim_id, websocket):
        if sim_id in self.active:
            self.active[sim_id].remove(websocket)

    async def send(self, sim_id, data):
        for ws in self.active.get(sim_id, []):
            await ws.send_json(data)

manager = ConnectionManager()