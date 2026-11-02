from pygame import Vector2

def clamp(value: float, min_val: float, max_val: float):
    return min(max_val, max(min_val, value))

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
