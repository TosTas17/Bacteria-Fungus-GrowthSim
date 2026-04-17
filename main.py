from fastapi import FastAPI, HTTPException

from DataBase.database import SessionLocal, engine
from DataBase.db_models import Base, Simulation, SimulationResult

from SimulationService.simulator import exponential_growth, logistic_growth
from SimulationService.models import SimulationRequest, SimulationResponse
from SimulationService.presets import PRESETS

from MessageBroker.rabbitmq import publish_simulation


app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.post("/simulate")
def simulate(data: SimulationRequest):
    
    # guardar simulação na DB (como já fazes)
    db = SessionLocal()

    sim = Simulation(
        model=data.model,
        initial_population=data.initial_population,
        growth_rate=data.growth_rate,
        carrying_capacity=data.carrying_capacity,
        steps=data.steps
    )

    db.add(sim)
    db.commit()
    db.refresh(sim)

    sim_id = sim.id

    # enviar para fila
    publish_simulation({
        "simulation_id": sim_id,
        "model": data.model,
        "initial_population": data.initial_population,
        "growth_rate": data.growth_rate,
        "carrying_capacity": data.carrying_capacity,
        "steps": data.steps
    })

    db.close()

    return {
        "simulation_id": sim_id,
        "status": "processing"
    }


from fastapi import HTTPException

@app.get("/simulations/{sim_id}")
def get_simulation(sim_id: int):
    db = SessionLocal()

    results = db.query(SimulationResult).filter_by(simulation_id=sim_id).all()

    if not results:
        db.close()
        raise HTTPException(status_code=404, detail="Simulation not found")

    response = [
        {"time": r.time, "population": r.population}
        for r in results
    ]

    db.close()
    return response