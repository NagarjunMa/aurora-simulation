from dataclasses import dataclass

@dataclass
class Profile:
    energy: int
    strain: int
    momentum: int

@dataclass
class Environment:
    demand: int
    recovery: int 
    opportunity: int
