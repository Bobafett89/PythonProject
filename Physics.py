import pygame
from pygame import Vector2
from Utils import jump_struct, dash_struct, level_pos, direction

class character_physics_controller:
        from Game import Game_manager
        from Objects import Character
        def __init__(self, char: Character, speed: float, jump_force: float, gravity: float, dash_dist: float, dash_speed: float) -> None:
            from Objects import Character
            self.VELOCITY: Vector2 = Vector2(0, 0)
            self.GRAVITY: float = gravity
            self.JUMP: jump_struct = jump_struct(force=jump_force)
            self.DASH: dash_struct = dash_struct(distance=dash_dist, speed=dash_speed)
            self.SPEED: float = speed
            self.CHAR: Character = char
            self.dir: float = 1

        @property
        def GAME(self) -> Game_manager:
            return self.CHAR.GAME

        @property
        def delta_time(self) -> float:
            return self.GAME.FRAME.delta_time

        @property
        def step(self) -> Vector2:
            return self.VELOCITY *  self.delta_time

        def collide(self):
            from BasicObjects import LevelObject
            def hit_floor() -> None:
                if(self.VELOCITY.y > 0):
                    self.JUMP.on_ground = True
                    if(self.JUMP.air_jumps < self.JUMP.def_air_jumps):
                        self.JUMP.air_jumps = self.JUMP.def_air_jumps
                    if(self.DASH.count < self.DASH.def_count):
                        self.DASH.count = self.DASH.def_count

            def hit_wall() -> None:
                self.DASH.is_active = False
                self.DASH.destination = None

            def next_state() -> LevelObject:
                return LevelObject(None, self.CHAR.level_pos + level_pos.from_vector2(self.step), self.CHAR.level_size, self.GAME)

            if(self.VELOCITY.y != 0):
                self.JUMP.on_ground = False
            new_state = next_state()
            tiles = self.GAME.level.GROUND.collides(new_state)
            tiles.sort(key=(lambda tile: self.CHAR.level_pos.vector2_to(tile.level_pos).length()))
            for tile in tiles:
                rel_topleft = (new_state.topleft_border - tile.topleft_border).to_vector2()
                rel_botright = (new_state.botright_border - tile.topleft_border).to_vector2()
                topleft = Vector2(max(0, rel_topleft.x), max(0, rel_topleft.y))
                botright = Vector2(min(1, rel_botright.x), min(1, rel_botright.y))
                size = botright - topleft
                offset = Vector2(0, 0)
                if(self.CHAR.tile_pos.x == tile.tile_pos.x or (size.x >= size.y and not self.CHAR.tile_pos.y == tile.tile_pos.y)):
                    dir = direction(self.CHAR.tile_pos.y > tile.tile_pos.y)
                    offset.y = size.y * dir
                    hit_floor()
                else:
                    dir = direction(self.CHAR.tile_pos.x > tile.tile_pos.x)
                    offset.x = size.x * dir
                    hit_wall()
                self.VELOCITY += offset / self.delta_time
                new_state = next_state()
                
        def apply_grav(self) -> None:
            if(not self.DASH.is_active):
                self.VELOCITY.y += self.GRAVITY * self.delta_time
            else:
                self.VELOCITY.y = 0
                self.JUMP.on_ground = False

        def run(self, dir: float) -> None:
            if(not self.DASH.is_active):
                self.VELOCITY.x = self.SPEED * dir

        def dash(self) -> None:
            dash = self.DASH
            pos = self.CHAR.level_pos
            if(not dash.is_active and dash.count > 0):
                dash.is_active = True
                dash.left = dash.distance
                dash.count -= 1
                self.VELOCITY.x = dash.speed * self.dir
            if(dash.is_active):
                if(dash.left > 0):
                    if(abs(self.step.x) <= dash.left):
                        self.VELOCITY.x = dash.speed * self.dir
                    else:
                        self.VELOCITY.x = dash.left * self.dir / self.delta_time
                else:
                    dash.is_active = False
                    dash.destination = None

        def jump(self) -> None:
            if(not self.DASH.is_active):
                if(self.JUMP.on_ground or self.JUMP.air_jumps > 0):
                    self.VELOCITY.y = -self.JUMP.force
                    if(not self.JUMP.on_ground):
                        self.JUMP.air_jumps -= 1

        def move(self) -> None:
            if(self.VELOCITY.x > 0):
                self.dir = 1
            elif(self.VELOCITY.x < 0):
                self.dir = -1
            self.CHAR.move_by(level_pos.from_vector2(self.step))
            if(self.DASH.is_active):
                self.DASH.left -= self.step.x
