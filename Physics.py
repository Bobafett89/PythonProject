import pygame
from pygame import Vector2
from Structs import jump_struct, dash_struct
from BasicObjects import Dynamic_object

class character_physics_controller:
        def __init__(self, entity: type[Dynamic_object], speed: float) -> None:
            self.__COLLIDER_MARGIN: float = 0.015
            self.__VELOCITY: Vector2 = Vector2(0, 0)
            self.__GRAVITY: float = 10
            self.__JUMP: jump_struct = jump_struct()
            self.__DASH: dash_struct = dash_struct()
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
            def grounded() -> None: #events which are fired when object touches ground
                self.JUMP.on_ground = True
                if(self.JUMP.air_jumps < self.JUMP.def_air_jumps):
                    self.JUMP.air_jumps = self.JUMP.def_air_jumps
                if(self.DASH.count < self.DASH.def_count):
                    self.DASH.count = self.DASH.def_count

            def hit_wall() -> None: #events which are fired when object hits wall
                self.DASH.is_active = False
                self.DASH.destination = None

            pos_in_tile, border_offset = self.ENTITY.get_local_pos(), self.ENTITY.get_border_offset()
            top_left, bottom_right = self.ENTITY.get_border()
            map = self.ENTITY.get_local_map()

            if(self.VELOCITY.y != 0):
                self.JUMP.on_ground = False
                moving_down = self.VELOCITY.y > 0
                left = top_left.x > 0 or not map[0][2 * moving_down]
                middle = not map[1][2 * moving_down]
                right = bottom_right.x < 1 or not map[2][2 * moving_down]
                can_move = left and middle and right
                if(not can_move):
                    dir = 2 * moving_down - 1
                    collider_edge = pos_in_tile.y + (border_offset.y + self.COLLIDER_MARGIN) * dir
                    border = 1 * moving_down
                    is_touching = (border - collider_edge) * dir <= 0
                    if(is_touching):
                        self.ENTITY.move(Vector2(0, border - collider_edge))
                        self.VELOCITY.y = 0
                        if(moving_down):
                            grounded()
                    else:
                        distance = border - collider_edge
                        step = self.VELOCITY.y * self.ENTITY.GAME.FRAME.delta_time
                        if(abs(step) > abs(distance)):
                            self.VELOCITY.y = distance / self.ENTITY.GAME.FRAME.delta_time
                            if(moving_down):
                                grounded()

            if(self.VELOCITY.x != 0):
                moving_right = self.VELOCITY.x > 0
                top = top_left.y > 0 or not map[2 * moving_right][0]
                middle = not map[2 * moving_right][1]
                bot = bottom_right.y < 1 or not map[2 * moving_right][2]
                can_move = top and middle and bot
                if(not can_move):
                    dir = 2 * moving_right - 1
                    collider_edge = pos_in_tile.x + (border_offset.x + self.COLLIDER_MARGIN) * dir
                    border = 1 * moving_right
                    is_touching = (border - collider_edge) * dir <= 0
                    if(is_touching):
                        self.ENTITY.move(Vector2(border - collider_edge, 0))
                        self.VELOCITY.x = 0
                        hit_wall()
                    else:
                        distance = border - collider_edge
                        step = self.VELOCITY.x * self.ENTITY.GAME.FRAME.delta_time
                        if(abs(step) > abs(distance)):
                            self.VELOCITY.x = distance / self.ENTITY.GAME.FRAME.delta_time
                            hit_wall()

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
