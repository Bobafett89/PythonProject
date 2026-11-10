import pygame
from pygame import Vector2
from enum import Enum, auto
from Utils import vector2_mult, round_vector2, abs_vector2, direction, clamp
from typing import Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from os import path
from math import floor

class Frame:
    __FIXED_DT: float = 1 / 50
    __MAX_DT: float = 1 / 20
    __MAX_FPS: int = 1000
    __screen_size: tuple[int, int] = (1920, 1080)
    __dt: float  = 0
    __fixed_steps: float = 0

    def __init__(self) -> None:
        screen_flags = pygame.FULLSCREEN | pygame.SCALED
        self.__SCREEN: pygame.Surface = pygame.display.set_mode(Frame.__screen_size, screen_flags)
        self.__CLOCK: pygame.Clock = pygame.time.Clock()
        self.__RENDER_GROUPS: list[pygame.sprite.Group] = []

    @classmethod
    def dt(cls) -> float:
        return cls.__dt

    @classmethod
    def FIXED_DT(cls) -> float:
        return cls.__FIXED_DT

    @classmethod
    def fixed_steps(cls) -> int:
        return cls.__fixed_steps

    @classmethod
    def screen_size(cls) -> Vector2:
        return Vector2(cls.__screen_size)

    def next(self) -> None:
        Frame.__fixed_steps -= int(Frame.__fixed_steps)
        Frame.__dt = clamp(self.__CLOCK.tick(Frame.__MAX_FPS) / 1000, 0, Frame.__MAX_DT)
        Frame.__fixed_steps += Frame.__dt / Frame.__FIXED_DT

    def render(self) -> None:
        self.__SCREEN.fill("#333333")
        for render_group in self.__RENDER_GROUPS:
            render_group.draw(self.__SCREEN)
        pygame.display.flip()

    def add_sprite_group(self, group: pygame.sprite.Group) -> None:
        if (group not in self.__RENDER_GROUPS):
            self.__RENDER_GROUPS.append(group)

    def remove_sprite_group(self, group: pygame.sprite.Group) -> None:
        if (group in self.__RENDER_GROUPS):
            self.__RENDER_GROUPS.remove(group)

    def clear_sprite_group(self) -> None:
        self.__RENDER_GROUPS.clear()

class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, sprite_path: str | None, transform: Transform) -> None:
        super().__init__()
        self.__transform: Transform = transform
        self._load_image(sprite_path)

    @property
    def size(self) -> Vector2:
        return self.__transform.size

    @property
    def pos(self) -> Vector2:
        return self.__transform.pos

    @property
    def edge_offset(self) -> Vector2:
        return self.size / 2

    @property
    def topleft(self) -> Vector2:
        return self.pos - self.edge_offset

    @property
    def botright(self) -> Vector2:
        return self.pos + self.edge_offset

    @property
    def screen_size(self) -> Vector2:
        return Frame.screen_size()

    @property
    def FIXED_DT(sefl) -> float:
        return Frame.FIXED_DT()

    def _set_center(self, pos: Vector2) -> None:
        pos: Vector2 = round_vector2(vector2_mult(pos, Frame.screen_size()))
        self.rect = self.rect.move_to(center=pos)

    def _move_to(self, new_pos: Vector2) -> None:
        self.__transform.pos = new_pos
        self._set_center(self.pos)

    def _move_by(self, offset: Vector2) -> None:
        self._move_to(self.pos + offset)

    def __rescale(self) -> None:
        size: Vector2 = round_vector2(vector2_mult(self.size, Frame.screen_size()))
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self._set_center(self.pos)

    def _set_size(self, new_size: Vector2) -> None:
        self.__transform.size = new_size
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
    def switch_ui(screen: UIScreen) -> Control:
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
class Transform:
    size: Vector2
    pos: Vector2

@dataclass
class Jump_info:
    on_ground: bool = False
    force: int = 0
    air_jumps: int = 0
    def_air_jumps: int = 0

@dataclass
class Dash_info:
    is_active: bool = False
    speed: float = 0
    distance: float = 0
    left: float = 0
    count: int = 0
    def_count: int = 0

@dataclass
class Player_diff:
    air_jumps: int
    def_air_jumps: int
    dashes: int
    def_dashes: int

@dataclass
class Jump_params:
    dist: float
    height: float
    time: float

@dataclass
class Dash_params:
    dist: float
    time: float

class PhysicsSystem:
    def __init__(self, speed: float, jump_force: float, gravity: float, dash_dist: float, dash_speed: float) -> None:
        self.__VELOCITY: Vector2 = Vector2(0, 0)
        self.__GRAVITY: float = gravity
        self.__JUMP: Jump_info = Jump_info(force=jump_force)
        self.__DASH: Dash_info = Dash_info(distance=dash_dist, speed=dash_speed)
        self.__SPEED: float = speed
        self.__dir: float = 1

    @property
    def on_ground(self) -> bool:
        return self.__JUMP.on_ground

    def apply_diff(self, diff: Player_diff) -> None:
        self.__JUMP.air_jumps += diff.air_jumps
        self.__JUMP.def_air_jumps += diff.def_air_jumps
        self.__DASH.count += diff.dashes
        self.__DASH.def_count += diff.def_dashes

    def collide(self, obj: type[BasicSprite], ground: list[BasicSprite]) -> None:
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
            return BasicSprite(None, Transform(obj.size, obj.pos + self.__VELOCITY))

        if (self.__VELOCITY.y != 0):
            self.__JUMP.on_ground = False
        new_state: BasicSprite = next_state()
        tiles: list[BasicSprite] = list(filter(lambda object: object.overlap(new_state), ground))
        tiles.sort(key = (lambda tile: (tile.pos - obj.pos).length()))
        for tile in tiles:
            min_dist: Vector2 = new_state.edge_offset + tile.edge_offset
            current_disp: Vector2 = tile.pos - obj.pos
            new_dist: Vector2 = abs_vector2(tile.pos - new_state.pos)
            if (new_dist.x < min_dist.x and new_dist.y < min_dist.y):
                epsilon: float = 2 ** (-53)
                overlap: Vector2 = min_dist - new_dist + Vector2(epsilon, epsilon)
                offset: Vector2 = Vector2(0, 0)
                if (abs(current_disp.x) < min_dist.x or (overlap.x >= overlap.y and not abs(current_disp.y) < min_dist.y)):
                    offset.y = overlap.y * direction(current_disp.y < 0)
                    hit_floor()
                else:
                    offset.x = overlap.x * direction(current_disp.x < 0)
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
            dash: Dash_info = self.__DASH
            if (dash.is_active):
                if (abs(self.__VELOCITY.x) >= dash.left):
                    self.__VELOCITY.x = dash.left * self.__dir
                    dash.is_active = False
                dash.left -= abs(self.__VELOCITY.x)
        return self.__VELOCITY

class InterpolationSystem:
    def __init__(self, pos: Vector2) -> None:
        self.__last_pos: Vector2 = pos

    def update_last_pos(self, pos: Vector2) -> None:
        self.__last_pos: Vector2 = pos

    def interpolate_pos(self, pos: Vector2) -> Vector2:
        step: Vector2 = pos - self.__last_pos
        progress: float = Frame.fixed_steps() - int(Frame.fixed_steps())
        return self.__last_pos + step * progress

class Interpolatable(ABC):
    @abstractmethod
    def interpolate_sprite_pos(self) -> None:
        pass
