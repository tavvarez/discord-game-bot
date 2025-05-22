from dataclasses import dataclass

@dataclass
class Player:
    name: str
    vocation: str
    level: int
    guild: str