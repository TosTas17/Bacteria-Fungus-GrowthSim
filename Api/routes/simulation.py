from fastapi import APIRouter, HTTPException
from DataBase.database import SessionLocal, engine
from DataBase.db_models import Base, Simulation, SimulationResult
from SimulationService.models import SimulationRequest

from zoneinfo import ZoneInfo


LISBON_TZ = ZoneInfo("Europe/Lisbon")

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

    db.close()

    return {"simulation_id": sim.id, "status": "waiting"}


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

@router.get("/simulations/{sim_id}/status")
def get_simulation_status(sim_id: int):
    db = SessionLocal()

    sim = db.query(Simulation).filter_by(id=sim_id).first()

    if not sim:
        db.close()
        raise HTTPException(status_code=404, detail="Simulation not found")

    def to_lisbon(dt):
        if dt is None:
            return None
        return dt.astimezone(LISBON_TZ).isoformat()

    response = {
        "simulation_id": sim.id,
        "status": sim.status,
        "created_at": to_lisbon(sim.created_at),
        "started_at": to_lisbon(sim.started_at),
        "finished_at": to_lisbon(sim.finished_at),
    }

    db.close()
    return response


@router.get("/simulations")
def get_all_simulations():
    db = SessionLocal()

    simulations = db.query(Simulation).order_by(Simulation.created_at.desc()).all()

    result = []
    for sim in simulations:
        result.append({
            "simulation_id": sim.id,
            "model": sim.model,
            "initial_population": sim.initial_population,
            "growth_rate": sim.growth_rate,
            "carrying_capacity": sim.carrying_capacity,
            "steps": sim.steps,
            "status": sim.status,
            "created_at": sim.created_at.astimezone(LISBON_TZ).isoformat() if sim.created_at else None,
        })

    db.close()
    return result