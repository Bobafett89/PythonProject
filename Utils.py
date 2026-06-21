from pygame import Vector2
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
    speed: float = 3
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

def vector2_add_num(vector: Vector2, num: float) -> Vector2:
    return Vector2(vector.x + num, vector.y + num)