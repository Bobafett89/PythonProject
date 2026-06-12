import pygame
from pygame import Vector2
from Structs import jump_struct, dash_struct
from BasicObjects import Dynamic_object
from collections.abc import Callable

class character_physics_controller:
        def __init__(self, entity: type[Dynamic_object], speed: float, jump_force: float, gravity: float, dash_dist: float, dash_speed: float) -> None:
            self.__COLLIDER_MARGIN: float = 0.001
            self.__VELOCITY: Vector2 = Vector2(0, 0)
            self.__GRAVITY: float = gravity
            self.__JUMP: jump_struct = jump_struct(force=jump_force)
            self.__DASH: dash_struct = dash_struct(distance=dash_dist, speed=dash_speed)
            self.__SPEED: float = speed
            self.__ENTITY: type[Dynamic_object] = entity
            self.__dir: float = 1

        @property
        def VELOCITY(self) -> Vector2:
            return self.__VELOCITY
        
        @property
        def JUMP(self) -> jump_struct:
            return self.__JUMP
        
        @property
        def DASH(self) -> dash_struct:
            return self.__DASH
        
        @property
        def GRAVITY(self) -> float:
            return self.__GRAVITY
        
        @property
        def COLLIDER_MARGIN(self) -> float:
            return self.__COLLIDER_MARGIN
        
        @property
        def SPEED(self) -> float:
            return self.__SPEED
        
        @property
        def ENTITY(self) -> type[Dynamic_object]:
            return self.__ENTITY
        
        @property
        def dir(self) -> float:
            return self.__dir

        def collide(self) -> None: #stops object from moving if touches ground
            def hit_floor() -> None: #events which are fired when object touches ground
                if(self.VELOCITY.y > 0):
                    self.JUMP.on_ground = True
                    if(self.JUMP.air_jumps < self.JUMP.def_air_jumps):
                        self.JUMP.air_jumps = self.JUMP.def_air_jumps
                    if(self.DASH.count < self.DASH.def_count):
                        self.DASH.count = self.DASH.def_count

            def hit_wall() -> None: #events which are fired when object hits wall
                self.DASH.is_active = False
                self.DASH.destination = None

            def can_move(start: float, end: float, map: tuple[bool, bool, bool]) -> bool:
                left = start >= 0 or not map[0]
                middle = not map[1]
                right = end <= 1 or not map[2]
                return left and middle and right

            def change_velocity(moving_pos: bool, velocity: float, pos_in_tile: float, border_offset: float, hit_ground: Callable[[], None]) -> float:
                dir = 2 * moving_pos - 1
                collider_edge = pos_in_tile + (border_offset + self.COLLIDER_MARGIN) * dir
                distance = 1 * moving_pos - collider_edge
                is_touching = distance * dir <= 0
                step = velocity * self.ENTITY.GAME.FRAME.delta_time
                if(is_touching or abs(step) > abs(distance)):
                    hit_ground()
                    velocity = distance / self.ENTITY.GAME.FRAME.delta_time
                return velocity

            pos_in_tile, border_offset = self.ENTITY.get_local_pos(), self.ENTITY.get_border_offset()
            top_left, bottom_right = self.ENTITY.get_border()
            map = self.ENTITY.get_local_map()

            if(self.VELOCITY.y != 0):
                self.JUMP.on_ground = False
                moving_down = self.VELOCITY.y > 0
                local_map = (map[0][2 * moving_down], map[1][2 * moving_down], map[2][2 * moving_down])
                if(not can_move(top_left.x, bottom_right.x, local_map)):
                    self.VELOCITY.y = change_velocity(moving_down, self.VELOCITY.y, pos_in_tile.y, border_offset.y, hit_floor)

            if(self.VELOCITY.x != 0):
                moving_right = self.VELOCITY.x > 0
                local_map = (map[2 * moving_right][0], map[2 * moving_right][1], map[2 * moving_right][2])
                if(not can_move(top_left.y, bottom_right.y, local_map)):
                    self.VELOCITY.x = change_velocity(moving_right, self.VELOCITY.x, pos_in_tile.x, border_offset.x, hit_wall)

        def apply_grav(self) -> None: #applies gravity to velocity
            if(not self.DASH.is_active):
                self.VELOCITY.y += self.GRAVITY * self.ENTITY.GAME.FRAME.delta_time
            else:
                self.VELOCITY.y = 0
                self.JUMP.on_ground = False

        def run(self, dir: float) -> None: #applies force to the x axis on a given direction
            if(not self.DASH.is_active):
                self.VELOCITY.x = self.SPEED * dir

        def dash(self) -> None: #applies special force to the velocity if has enough dashes
            dash = self.DASH
            pos = self.ENTITY.pos
            if(not dash.is_active and dash.count > 0):
                dash.is_active = True
                dash.destination = pos.x + dash.distance * self.dir
                dash.count -= 1
            if(dash.is_active):
                left = (dash.destination - pos.x) * self.dir
                step = dash.speed * self.ENTITY.GAME.FRAME.delta_time
                if(left > 0):
                    if(step <= left):
                        self.VELOCITY.x = dash.speed * self.dir
                    else:
                        self.VELOCITY.x = left * self.dir / self.ENTITY.GAME.FRAME.delta_time
                else:
                    dash.is_active = False
                    dash.destination = None

        def jump(self) -> None: #applies force to the y axis if has enough jumps
            if(not self.DASH.is_active):
                if(self.JUMP.on_ground or self.JUMP.air_jumps > 0):
                    self.VELOCITY.y = -self.JUMP.force
                    if(not self.JUMP.on_ground):
                        self.JUMP.air_jumps -= 1

        def move(self) -> None: #moves object according to its velocity
            if(self.VELOCITY.x > 0):
                self.__dir = 1
            elif(self.VELOCITY.x < 0):
                self.__dir = -1
            offset = self.VELOCITY * self.ENTITY.GAME.FRAME.delta_time
            self.ENTITY.move(offset)
