from pydantic import BaseModel
from typing import Optional, List


class SimulationRequest(BaseModel):
    preset: Optional[str] = None

    model: Optional[str] = None
    initial_population: Optional[float] = None
    growth_rate: Optional[float] = None
    steps: int = 50
    carrying_capacity: Optional[float] = None


class SimulationPoint(BaseModel):
    time: int
    population: float


class SimulationResponse(BaseModel):
    simulation_id: int
    result: List[SimulationPoint]