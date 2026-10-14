
from dataclasses import asdict

from .model import Profile, Environment


def clamp(value: int) -> int:
    return max(0, min(value, 100))


def evaluate(profile: Profile, environment: Environment) -> Profile:

    current_profile = profile

    new_energy = clamp(
        current_profile.energy
        - environment.demand
        + environment.recovery
    )

    new_strain = clamp(
        current_profile.strain
        + environment.demand
        - environment.recovery
    )

    new_momentum = clamp(
        current_profile.momentum
        + environment.opportunity
        - new_strain // 10
    )

    new_profile = Profile(
        energy=new_energy,
        strain=new_strain,
        momentum=new_momentum
    )

    return new_profile


def evaluate_path(
    profile: Profile,
    environment: list[Environment]
) -> dict:

    current_profile = profile
    # Index 0 is the starting profile; each subsequent item is one step.
    results = [asdict(current_profile)]

    for env in environment:

        current_profile = evaluate(current_profile, env)

        results.append(asdict(current_profile))

    return {
        "trajectory": results,
        "final_state": asdict(current_profile)
    }


def evaluate_paths(
    profile: Profile,
    paths: dict[str, list[Environment]]
) -> dict:

    results = {}

    for path_name, environments in paths.items():
        results[path_name] = evaluate_path(
            profile,
            environments
        )

    return results
