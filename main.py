from fastapi import FastAPI

from workspace.model import Profile, Environment
from workspace.evaluate import evaluate_paths
from workspace.models import SimulationRequest, SimulationResponse


app = FastAPI(title="Aurora Genesis Path Simulation")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/simulate", response_model=SimulationResponse)
def simulate(request: SimulationRequest):
    """
    Simulate multiple paths from the same initial state.
    """

    # Convert Pydantic profile into dataclass
    profile = Profile(
        energy=request.initial_state.energy,
        strain=request.initial_state.strain,
        momentum=request.initial_state.momentum
    )

    # Convert Pydantic environment inputs into dataclasses
    paths = {}

    for path_name, steps in request.paths.items():
        paths[path_name] = [
            Environment(
                demand=step.demand,
                recovery=step.recovery,
                opportunity=step.opportunity
            )
            for step in steps
        ]

    # Run all paths independently
    results = evaluate_paths(profile, paths)

    # Return structured response
    return {"results": results}
