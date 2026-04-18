from fastapi import FastAPI
from Api.routes import simulation

app = FastAPI()

app.include_router(simulation.router)