from pygame import Vector2
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

class Command(Enum):
    WAIT = auto()
    SWITCH_UI = auto()
    OPEN_LEVEL = auto()
    RESTART_LEVEL = auto()
    CLOSE_LEVEL = auto()
    CLOSE_GAME = auto()

class Control:
    def __init__(self, command: Command, parameter: str | None):
        self.command: Command = command
        self.parameter: Any = parameter

    @staticmethod
    def wait() -> Control:
        return Control(Command.WAIT, None)
    
    @staticmethod
    def switch_ui(screen: UI_Screen) -> Control:
        return Control(Command.SWITCH_UI, screen)
    
    @staticmethod
    def open_level(level_name: str) -> Control:
        return Control(Command.OPEN_LEVEL, level_name)
    
    @staticmethod
    def restart_level() -> Control:
        return Control(Command.RESTART_LEVEL, None)
    
    @staticmethod
    def close_level() -> Control:
        return Control(Command.CLOSE_LEVEL, None)
    
    @staticmethod
    def close_game() -> Control:
        return Control(Command.CLOSE_GAME, None)

@dataclass
class jump_struct:
    on_ground: bool = False
    force: int = 5
    air_jumps: int = 0
    def_air_jumps: int = 0

@dataclass
class dash_struct:
    is_active: bool = False
    speed: float = 3
    distance: float = 3
    left: float = 0
    count: int = 0
    def_count: int = 0

@dataclass
class character_diff:
    air_jumps: int = 0
    def_air_jumps: int = 0
    dashes: int = 0
    def_dashes: int = 0

@dataclass
class tilemap_info:
    size: Vector2 = None
    tile_size: Vector2 = None

def direction(statement: bool) -> int:
    return 2 * statement - 1

def in_interval(value: float, min: float, max: float) -> bool:
    return min <= value and value <= max

def in_left_interval(value: float, min: float, max: float) -> bool:
    return min < value and value <= max

def in_right_interval(value: float, min: float, max: float) -> bool:
    return min <= value and value < max

def in_open_interval(value: float, min: float, max: float) -> bool:
    return min < value and value < max

def vector2_div(dividend_vector: Vector2, divisor_vector: Vector2) -> Vector2:
    return Vector2(dividend_vector.x / divisor_vector.x, dividend_vector.y / divisor_vector.y)

def vector2_mult(first_vector: Vector2, second_vector: Vector2) -> Vector2:
    return Vector2(first_vector.x * second_vector.x, first_vector.y * second_vector.y)

def trunc_vector2(vector: Vector2) -> Vector2:
    return Vector2(int(vector.x), int(vector.y))

def abs_vector2(vector: Vector2) -> Vector2:
    return Vector2(abs(vector.x), abs(vector.y))

def round_vector2(vector: Vector2, digits: int = 0) -> Vector2:
    return Vector2(round(vector.x, digits), round(vector.y, digits))