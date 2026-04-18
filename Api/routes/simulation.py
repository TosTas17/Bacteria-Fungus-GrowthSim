from fastapi import APIRouter, HTTPException
from DataBase.database import SessionLocal, engine
from DataBase.db_models import Base, Simulation, SimulationResult
from SimulationService.models import SimulationRequest
from MessageBroker.rabbitmq import publish_simulation

router = APIRouter()

@router.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@router.post("/simulate")
def simulate(data: SimulationRequest):

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

    publish_simulation({
        "simulation_id": sim.id,
        "model": data.model,
        "initial_population": data.initial_population,
        "growth_rate": data.growth_rate,
        "carrying_capacity": data.carrying_capacity,
        "steps": data.steps
    })

    db.close()

    return {"simulation_id": sim.id, "status": "processing"}


@router.get("/simulations/{sim_id}")
def get_simulation(sim_id: int):

    db = SessionLocal()

    results = db.query(SimulationResult).filter_by(simulation_id=sim_id).all()

    db.close()

    if not results:
        raise HTTPException(status_code=404)

    return [
        {"time": r.time, "population": r.population}
        for r in results
    ]