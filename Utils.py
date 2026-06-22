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
class level_pos:
    tile_pos: Vector2 = None
    local_pos: Vector2 = None

    def __add__(self, other: level_pos) -> level_pos:
        new_tile = self.tile_pos + other.tile_pos
        new_local = self.local_pos + other.local_pos
        return level_pos.correct(level_pos(new_tile, new_local))
    
    def __sub__(self, other: level_pos) -> level_pos:
        new_tile = self.tile_pos - other.tile_pos
        new_local = self.local_pos - other.local_pos
        return level_pos.correct(level_pos(new_tile, new_local))
    
    def to_vector2(self) -> Vector2:
        return self.tile_pos + self.local_pos
    
    def vector2_to(self, other: level_pos) -> Vector2:
        return (other - self).to_vector2()

    @staticmethod
    def correct(pos: level_pos) -> level_pos:
        new_tile = pos.tile_pos.copy()
        new_local = pos.local_pos.copy()
        if(not in_right_interval(new_local.x, 0, 1)):
            dir = direction(new_local.x < 0)
            new_tile.x -= dir
            new_local.x += dir
        if(not in_right_interval(new_local.y, 0, 1)):
            dir = direction(new_local.y < 0)
            new_tile.y -= dir
            new_local.y += dir
        return level_pos(new_tile, new_local)

    @staticmethod
    def from_vector2(pos: Vector2):
        tile_pos = pos // 1
        local_pos = pos - tile_pos
        return level_pos(tile_pos, local_pos)

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