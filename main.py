from fastapi import FastAPI, HTTPException

from DataBase.database import SessionLocal, engine
from DataBase.db_models import Base, Simulation, SimulationResult

from SimulationService.simulator import exponential_growth, logistic_growth
from SimulationService.models import SimulationRequest, SimulationResponse
from SimulationService.presets import PRESETS


app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.post("/simulate", response_model=SimulationResponse)
def simulate(data: SimulationRequest):

   
    if data.preset:
        preset = PRESETS.get(data.preset)
        if not preset:
            raise HTTPException(status_code=400, detail="Invalid preset")

        # sobrescreve apenas os campos que não vieram no request
        merged_data = preset.copy()
        user_data = data.dict(exclude_unset=True)

        merged_data.update(user_data)  # user pode fazer override

    else:
        merged_data = data.dict()


    model = merged_data.get("model")
    N0 = merged_data.get("initial_population")
    r = merged_data.get("growth_rate")
    steps = merged_data.get("steps", 50)
    K = merged_data.get("carrying_capacity")

   
    if model is None or N0 is None or r is None:
        raise HTTPException(status_code=400, detail="Missing required parameters")

    if model == "logistic" and K is None:
        raise HTTPException(
            status_code=400,
            detail="carrying_capacity is required for logistic model"
        )


    if model == "exponential":
        result = exponential_growth(N0, r, steps)

    elif model == "logistic":
        result = logistic_growth(N0, r, K, steps)

    else:
        raise HTTPException(status_code=400, detail="Invalid model")
            
    db = SessionLocal()
    try:
        sim = Simulation(
            model=model,
            initial_population=N0,
            growth_rate=r,
            carrying_capacity=K,
            steps=steps
        )

        db.add(sim)
        db.commit()
        db.refresh(sim)

        sim_id = sim.id

        for point in result:
            db.add(SimulationResult(
                simulation_id=sim_id,
                time=point["time"],
                population=point["population"]
            ))

        db.commit()

    finally:
        db.close()

    return {
    "simulation_id": sim_id,
    "result": result
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