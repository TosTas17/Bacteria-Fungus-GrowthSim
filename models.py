from pydantic import BaseModel
from typing import Optional, List


class SimulationRequest(BaseModel):
    model: str  # "exponential" ou "logistic"
    initial_population: float
    growth_rate: float
    steps: int = 50
    carrying_capacity: Optional[float] = None


class SimulationPoint(BaseModel):
    time: int
    population: float


class SimulationResponse(BaseModel):
    result: List[SimulationPoint]