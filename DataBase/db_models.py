from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from DataBase.database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)
    initial_population = Column(Float)
    growth_rate = Column(Float)
    carrying_capacity = Column(Float, nullable=True)
    steps = Column(Integer)


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    time = Column(Integer)
    population = Column(Float)

    simulation = relationship("Simulation")