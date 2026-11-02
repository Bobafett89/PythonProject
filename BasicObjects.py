import pygame
from pygame import Vector2
from enum import Enum, auto
from Utils import vector2_mult, vector2_div, round_vector2, abs_vector2, direction
from typing import Any
from dataclasses import dataclass
from os import path

class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, sprite_path: str | None, size: Vector2, pos: Vector2) -> None:
        super().__init__()
        self.__size: Vector2 = size
        self.__pos: Vector2 = pos
        self._load_image(sprite_path)

    @property
    def size(self) -> Vector2:
        return self.__size

    @property
    def pos(self) -> Vector2:
        return self.__pos

    @property
    def edge_offset(self) -> Vector2:
        return self.size / 2

    @property
    def topleft(self) -> Vector2:
        return self.pos - self.edge_offset

    @property
    def botright(self) -> Vector2:
        return self.pos + self.edge_offset

    def __set_center(self) -> None:
        from Game import GAME
        pos: Vector2 = round_vector2(vector2_mult(self.pos, GAME.screen_size()))
        self.rect = self.rect.move_to(center=pos)

    def _move_to(self, new_pos: Vector2) -> None:
        self.__pos = new_pos
        self.__set_center()

    def _move_by(self, offset: Vector2) -> None:
        self._move_to(self.pos + offset)

    def __rescale(self) -> None:
        from Game import GAME
        size: Vector2 = round_vector2(vector2_mult(self.size, GAME.screen_size()))
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.__set_center()

    def _set_size(self, new_size: Vector2) -> None:
        self.__size = new_size
        self.__rescale()

    def _set_image(self, image: pygame.Surface) -> None:
        self.image = image
        self.__rescale()

    def _load_image(self, sprite_path: str | None) -> None:
        img: pygame.Surface = None
        try:
            if (sprite_path != None):
                img = pygame.image.load(path.join("Assets", sprite_path))
            else:
                img = pygame.Surface(Vector2(0, 0), pygame.SRCALPHA)
                img.fill((0, 0, 0, 0))
        except (pygame.error, FileNotFoundError):
            img = pygame.Surface(Vector2(0, 0))
            img.fill("black")
        self._set_image(img)

    def overlap(self, other: type[BasicSprite]) -> bool:
        dist: Vector2 = abs_vector2(self.pos - other.pos)
        min_dist: Vector2 = self.edge_offset + other.edge_offset
        return dist.x < min_dist.x and dist.y < min_dist.y

    def update(self) -> None:
        pass

    def fixed_update(self) -> None:
        pass

class Command(Enum):
    WAIT = auto()
    OPEN_MENU = auto()
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
    def open_menu() -> Control:
        return Control(Command.OPEN_MENU, None)

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
class jump_params:
    dist: float = 1
    height: float = 1
    time: float = 1

@dataclass
class dash_params:
    dist: float = 1
    time: float = 1

class character_physics_controller:
    def __init__(self, speed: float, jump_force: float, gravity: float, dash_dist: float, dash_speed: float) -> None:
        self.__VELOCITY: Vector2 = Vector2(0, 0)
        self.__GRAVITY: float = gravity
        self.__JUMP: jump_struct = jump_struct(force=jump_force)
        self.__DASH: dash_struct = dash_struct(distance=dash_dist, speed=dash_speed)
        self.__SPEED: float = speed
        self.__dir: float = 1

    @property
    def on_ground(self) -> bool:
        return self.__JUMP.on_ground

    def apply_diff(self, diff: character_diff) -> None:
        self.__JUMP.air_jumps += diff.air_jumps
        self.__JUMP.def_air_jumps += diff.def_air_jumps
        self.__DASH.count += diff.dashes
        self.__DASH.def_count += diff.def_dashes

    def collide(self, obj: type[BasicSprite], ground: TilemapLayer) -> None:
        def hit_floor() -> None:
            if (self.__VELOCITY.y > 0):
                self.__JUMP.on_ground = True
                if (self.__JUMP.air_jumps < self.__JUMP.def_air_jumps):
                    self.__JUMP.air_jumps = self.__JUMP.def_air_jumps
                if (self.__DASH.count < self.__DASH.def_count):
                    self.__DASH.count = self.__DASH.def_count

        def hit_wall() -> None:
            self.__DASH.is_active = False
            self.__DASH.destination = None

        def next_state() -> BasicSprite:
            return BasicSprite(None, obj.size, obj.pos + self.__VELOCITY)

        if (self.__VELOCITY.y != 0):
            self.__JUMP.on_ground = False
        new_state = next_state()
        tiles = ground.collides(new_state, True)
        tiles.sort(key = (lambda tile: (tile.pos - obj.pos).length()))
        for tile in tiles:
            min_dist = new_state.edge_offset + tile.edge_offset
            dir = tile.pos - obj.pos
            dist = abs_vector2(tile.pos - new_state.pos)
            if (dist.x < min_dist.x and dist.y < min_dist.y):
                epsilon = 2 ** (-53)
                size = min_dist - dist + Vector2(epsilon, epsilon)
                offset = Vector2(0, 0)
                if (abs(dir.x) < min_dist.x or (size.x >= size.y and not abs(dir.y) < min_dist.y)):
                    offset.y = size.y * direction(dir.y < 0)
                    hit_floor()
                else:
                    offset.x = size.x * direction(dir.x < 0)
                    hit_wall()
                self.__VELOCITY += offset
                new_state = next_state()

    def apply_grav(self) -> None:
        if (not self.__DASH.is_active):
            self.__VELOCITY.y += self.__GRAVITY
        else:
            self.__VELOCITY.y = 0
            self.__JUMP.on_ground = False

    def run(self, dir: float) -> None:
        if (not self.__DASH.is_active):
            self.__VELOCITY.x = self.__SPEED * dir

    def dash(self) -> None:
        dash = self.__DASH
        if (not dash.is_active and dash.count > 0):
            dash.is_active = True
            dash.left = dash.distance
            dash.count -= 1
            self.__VELOCITY.x = dash.speed * self.__dir

    def jump(self) -> None:
        if (not self.__DASH.is_active):
            if (self.__JUMP.on_ground or self.__JUMP.air_jumps > 0):
                self.__VELOCITY.y = -self.__JUMP.force
                if (not self.__JUMP.on_ground):
                    self.__JUMP.air_jumps -= 1

    def move(self) -> Vector2:
        if (self.__VELOCITY.x != 0):
            self.__dir = direction(self.__VELOCITY.x > 0)
            dash = self.__DASH
            if (dash.is_active):
                if (abs(self.__VELOCITY.x) >= dash.left):
                    self.__VELOCITY.x = dash.left * self.__dir
                    dash.is_active = False
                dash.left -= abs(self.__VELOCITY.x)
        return self.__VELOCITY
