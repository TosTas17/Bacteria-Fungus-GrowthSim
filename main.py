from fastapi import FastAPI
from simulator import exponential_growth, logistic_growth
from models import SimulationRequest, SimulationResponse

app = FastAPI()

@app.post("/simulate", response_model=SimulationResponse)
def simulate(data: SimulationRequest):
    if data.model == "exponential":
        result = exponential_growth(
            data.initial_population,
            data.growth_rate,
            data.steps
        )

    elif data.model == "logistic":
        result = logistic_growth(
            data.initial_population,
            data.growth_rate,
            data.carrying_capacity,
            data.steps
        )

    else:
        return {"error": "Invalid model"}

    return {"result": result}