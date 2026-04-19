import asyncio
import json
import os
import aio_pika
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Store active WebSocket connections per simulation
simulation_connections: dict[str, set[WebSocket]] = {}
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

# Readiness signal
consumer_ready = asyncio.Event()


async def consume_rabbitmq():
    """Consume messages from simulation_updates queue and broadcast to WebSocket clients."""
    print("[*] Starting RabbitMQ consumer...")
    await asyncio.sleep(5)  # Wait for RabbitMQ to be ready
    
    while True:
        try:
            print(f"[*] Connecting to RabbitMQ at {RABBITMQ_HOST}...")
            connection = await aio_pika.connect_robust(
                f"amqp://guest:guest@{RABBITMQ_HOST}/",
                timeout=10,
                reconnect_interval=5
            )
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            
            queue = await channel.declare_queue("simulation_updates", durable=True)
            
            print("[*] Waiting for simulation updates...")
            consumer_ready.set()  # Signal that consumer is ready
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        data = json.loads(message.body.decode())
                        print(f"[→] Received update: {data}")
                        sim_id = str(data.get("simulation_id"))
                        
                        # Broadcast to all WebSocket clients for this simulation
                        if sim_id in simulation_connections:
                            disconnected = set()
                            for websocket in simulation_connections[sim_id]:
                                try:
                                    await websocket.send_json(data)
                                    print(f"[→] Sent to WS client {sim_id}")
                                except Exception as e:
                                    print(f"[!] Error sending to WS: {e}")
                                    disconnected.add(websocket)
                            
                            # Remove disconnected clients
                            for ws in disconnected:
                                simulation_connections[sim_id].discard(ws)

        except Exception as e:
            print(f"[!] RabbitMQ connection error: {e}")
            consumer_ready.clear()
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    print("[*] Starting up...")
    task = asyncio.create_task(consume_rabbitmq())
    await consumer_ready.wait()  # Wait for consumer to be ready
    print("[*] Consumer ready!")
    yield
    # Shutdown
    print("[*] Shutting down...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/{simulation_id}")
async def websocket_endpoint(websocket: WebSocket, simulation_id: str):
    """WebSocket endpoint for receiving simulation updates."""
    await websocket.accept()

    # Add connection to simulation's group
    if simulation_id not in simulation_connections:
        simulation_connections[simulation_id] = set()
    simulation_connections[simulation_id].add(websocket)

    print(f"[+] Client connected to simulation {simulation_id}")

    try:
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"[-] Client disconnected from simulation {simulation_id}")
    finally:
        if simulation_id in simulation_connections:
            simulation_connections[simulation_id].discard(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)