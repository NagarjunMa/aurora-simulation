
from pydantic import BaseModel, Field


class State(BaseModel):
    energy: int = Field(ge=0, le=100)
    strain: int = Field(ge=0, le=100)
    momentum: int = Field(ge=0, le=100)


class Environment(BaseModel):
    demand: int = Field(ge=0, le=10)
    recovery: int = Field(ge=0, le=10)
    opportunity: int = Field(ge=0, le=10)


class SimulationRequest(BaseModel):
    initial_state: State
    paths: dict[str, list[Environment]] = Field(min_length=1)


class PathResult(BaseModel):
    trajectory: list[State]
    final_state: State


class SimulationResponse(BaseModel):
    results: dict[str, PathResult]
