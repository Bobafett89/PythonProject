from dataclasses import dataclass

@dataclass
class jump_struct:
    on_ground: bool = False
    force: int = 5
    air_jumps: int = 0
    def_air_jumps: int = 0

@dataclass
class dash_struct:
    is_active: bool = False
    speed: float = 15
    distance: float = 3
    destination: float = None
    count: int = 0
    def_count: int = 0

@dataclass
class character_diff:
    air_jumps: int = 0
    def_air_jumps: int = 0
    dashes: int = 0
    def_dashes: int = 0