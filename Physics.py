import pygame
from pygame import Vector2
from Structs import jump_struct, dash_struct
from BasicObjects import Basic_object, Dynamic_object

class character_physics_controller:
        from Game import Game_manager
        def __init__(self, entity: type[Dynamic_object], speed: float, jump_force: float, gravity: float, dash_dist: float, dash_speed: float) -> None:
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
        def SPEED(self) -> float:
            return self.__SPEED
        
        @property
        def ENTITY(self) -> type[Dynamic_object]:
            return self.__ENTITY
        
        @property
        def GAME(self) -> Game_manager:
            return self.ENTITY.GAME
        
        @property
        def delta_time(self):
            return self.GAME.FRAME.delta_time
        
        @property
        def dir(self) -> float:
            return self.__dir
        
        @property
        def step(self) -> Vector2:
            return self.VELOCITY * self.delta_time
        
        @property
        def collider(self) -> pygame.Rect:
            return self.ENTITY.rect

        def collide(self):
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

            if(self.VELOCITY.y != 0):
                self.JUMP.on_ground = False
            next_pos = self.ENTITY.premove(self.step)
            border_offset = self.ENTITY.border_offset
            tiles = self.GAME.level.GROUND.collides(next_pos[0], next_pos[1], self.ENTITY.SIZE)
            tiles.sort(key=(lambda tile: tile.pos.distance_to(self.ENTITY.pos)))
            for tile in tiles:
                next_rel_pos = next_pos[1] - (tile.tile_pos - next_pos[0])
                top_left = Vector2(max(next_rel_pos.x - border_offset.x, tile.local_border[0].x), max(next_rel_pos.y - border_offset.y, tile.local_border[0].y))
                bottom_right = Vector2(min(next_rel_pos.x + border_offset.x, tile.local_border[1].x), min(next_rel_pos.y + border_offset.y, tile.local_border[1].y))
                size = bottom_right - top_left
                target = Vector2(0, 0)
                if(self.ENTITY.tile_pos.x == tile.tile_pos.x or (size.x >= size.y and not self.ENTITY.tile_pos.y == tile.tile_pos.y)):
                    if(self.ENTITY.pos.y <= tile.pos.y):
                        dir = -1
                    else:
                        dir = 1
                    target = Vector2(next_rel_pos.x, tile.local_pos.y + (tile.border_offset.y + border_offset.y) * dir)
                    hit_floor()
                else:
                    if(self.ENTITY.pos.x <= tile.pos.x):
                        dir = -1    
                    else:
                        dir = 1
                    target = Vector2(tile.local_pos.x + (tile.border_offset.x + border_offset.x) * dir, next_rel_pos.y)
                    hit_wall()
                self.__VELOCITY += (target - next_rel_pos) / self.delta_time
                next_pos = self.ENTITY.premove(self.step)
                
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
                self.VELOCITY.x = dash.speed * self.dir
            if(dash.is_active):
                left = (dash.destination - pos.x) * self.dir
                if(left > 0):
                    if(abs(self.step.x) <= left):
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
            self.ENTITY.move(self.step)
