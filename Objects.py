import pygame
from pygame import Vector2
from BasicObjects import BasicSprite, LevelSprite
from Utils import character_diff, Control, in_right_interval, direction, trunc_vector2
from math import ceil

class Character(LevelSprite):
    from Game import Game_manager
    def __init__(self, sprite_path: str, size: Vector2, pos: Vector2, jump_dist: float, jump_height: float, jump_time: float, dash_dist: float, dash_time: float, game: Game_manager) -> None:
        from Physics import character_physics_controller as physics
        def convert_x(num: float) -> float:
            return game.level.convert_unit_vector(Vector2(num, 0)).x
        def convert_y(num: float) -> float:
            return game.level.convert_unit_vector(Vector2(0, num)).y
        fixed_delta = game.FRAME.FIXED_DELTA_TIME
        jump_force = convert_y(2 * jump_height / jump_time) * fixed_delta
        gravity = convert_y((2 * jump_height / jump_time) / jump_time) * (fixed_delta ** 2)
        speed = convert_x(jump_dist / (2 * jump_time)) * fixed_delta
        dash_speed = convert_x(dash_dist / dash_time) * fixed_delta
        screen_dash_dist = convert_x(dash_dist)

        super().__init__(sprite_path, size, pos, game)
        self.PHYSICS: physics = physics(self, speed, jump_force, gravity, screen_dash_dist, dash_speed)

    def behaviour(self) -> None:
        keys, new_keys = pygame.key.get_pressed(), pygame.key.get_just_pressed()

        if(new_keys[pygame.K_LSHIFT]):
            self.PHYSICS.dash()

        dir = 1 * keys[pygame.K_d] - 1 * keys[pygame.K_a]
        self.PHYSICS.run(dir)

        if(keys[pygame.K_w] and self.PHYSICS.JUMP.on_ground or new_keys[pygame.K_w]):
            self.PHYSICS.jump()

        self.__debug()
    
    def fixed_step_behaviour(self):
        self.PHYSICS.apply_grav()

        keys = pygame.key.get_pressed()
        dir = 1 * keys[pygame.K_d] - 1 * keys[pygame.K_a]
        self.PHYSICS.run(dir)

        if(keys[pygame.K_w] and self.PHYSICS.JUMP.on_ground):
            self.PHYSICS.jump()

        self.PHYSICS.collide()
        self.PHYSICS.move()
        self.death_check()

    def death_check(self) -> None:
        hazard_contacts = self.GAME.level.HAZARD.collides(self, False)
        if(len(hazard_contacts) > 0):
            self.GAME.set_command(Control.restart_level())

    def give_air_jumps(self, count: int) -> None:
        self.PHYSICS.JUMP.air_jumps += count

    def give_dashes(self, count: int) -> None:
        self.PHYSICS.DASH.count += count

    def increase_air_jumps(self, count: int) -> None:
        self.PHYSICS.JUMP.def_air_jumps += count

    def increase_dashes(self, count: int) -> None:
        self.PHYSICS.DASH.def_count += count

    def __debug(self) -> None:
        keys, new_keys = pygame.key.get_pressed(), pygame.key.get_just_pressed()
        if(keys[pygame.K_UP]):
            self.PHYSICS.VELOCITY.y = -self.PHYSICS.JUMP.force
        if(keys[pygame.K_DOWN]):
            self.PHYSICS.VELOCITY.y = self.PHYSICS.JUMP.force
        if(new_keys[pygame.K_1]):
           self.increase_air_jumps(1)
        if(new_keys[pygame.K_2]):
           self.increase_dashes(1)

class TilemapLayer:
    from Game import Game_manager
    def __init__(self, game: Game_manager) -> None:
        from Game import Game_manager
        self.GAME: Game_manager = game
        self.SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.MAP: list[list[BasicSprite]] = []
        for i in range(int(self.SIZE.x)):
            self.MAP.append([])
            for j in range(int(self.SIZE.y)):
                self.MAP[i].append(None)

    @property
    def SIZE(self) -> Vector2:
        return self.GAME.level.TILEMAP.size
    
    @property
    def TILE_SIZE(self) -> Vector2:
        return self.GAME.level.TILEMAP.tile_size
    
    def convert_to_screen(self, pos: Vector2) -> Vector2:
        return self.GAME.level.convert_tilemap_vector(pos)
    
    def convert_to_tilemap(self, pos: Vector2) -> Vector2:
        return self.GAME.level.convert_tilemap_vector(pos, True)
    
    def addTile(self, sprite_path: str, tile_pos: Vector2) -> None:
        if(self.MAP[int(tile_pos.x)][int(tile_pos.y)] == None):
            pos = self.convert_to_screen(tile_pos + Vector2(0.5, 0.5))
            tile = BasicSprite(sprite_path, pos, self.TILE_SIZE, self.GAME)
            self.SPRITES.add(tile)
            self.MAP[int(tile_pos.x)][int(tile_pos.y)] = tile

    def getTile(self, tile_pos: Vector2, pseudo_tile: bool) -> BasicSprite | None:
        if(in_right_interval(tile_pos.x, 0, len(self.MAP)) and in_right_interval(tile_pos.y, 0, len(self.MAP[0]))):
            return self.MAP[int(tile_pos.x)][int(tile_pos.y)]
        else: 
            if(pseudo_tile):
                pos = self.convert_to_screen(tile_pos + Vector2(0.5, 0.5))
                return BasicSprite(None, pos, self.TILE_SIZE, self.GAME)
            else:
                return None

    def collides(self, object: type[BasicSprite], pseudo_tiles: bool) -> list[BasicSprite]:
        tilemap_pos = trunc_vector2(self.convert_to_tilemap(object.pos))
        border_offset = self.convert_to_tilemap(object.edge_offset)
        tile_offset = Vector2(ceil(border_offset.x), ceil(border_offset.y))
        collisions = []
        for i in range(int(-tile_offset.x), int(tile_offset.x) + 1):
            for j in range(int(-tile_offset.y), int(tile_offset.y) + 1):
                offset = Vector2(i, j)
                tile = self.getTile(tilemap_pos + offset, pseudo_tiles)
                if(tile != None and tile.overlap(object)):
                    collisions.append(tile)
        return collisions
            
class Finish(LevelSprite):
    from Game import Game_manager
    def __init__(self, sprite_path: str | None, size: Vector2, pos: Vector2, game: Game_manager) -> None:
        super().__init__(sprite_path, size, pos, game)

    def fixed_step_behaviour(self) -> None:
        character = self.GAME.level.PLAYER
        if(self.overlap(character)):
            self.GAME.set_command(Control.close_level())

class Collectable(LevelSprite):
    from Game import Game_manager
    def __init__(self, sprite_path: str | None, size: Vector2, pos: Vector2, diff: character_diff, game: Game_manager) -> None:
        super().__init__(sprite_path, size, pos, game)
        self.DIFF: character_diff = diff
        self.is_collected: bool = False

    def fixed_step_behaviour(self) -> None:
        character = self.GAME.level.PLAYER
        collide_with_character = self.overlap(character)
        if(collide_with_character and not self.is_collected):
            character.give_air_jumps(self.DIFF.air_jumps)
            character.increase_air_jumps(self.DIFF.def_air_jumps)
            character.give_dashes(self.DIFF.dashes)
            character.increase_dashes(self.DIFF.def_dashes)
            self.is_collected = True
            self.GAME.level.collect_object(self)

class MovingCollectable(Collectable):
    from Game import Game_manager
    def __init__(self, sprite_path: str | None, size: Vector2, pos: Vector2, diff: character_diff, speed: float, destination: Vector2, game: Game_manager) -> None:
        super().__init__(sprite_path, size, pos, diff, game)
        screen_speed = self.GAME.level.convert_unit_vector(Vector2(speed, 0)).x
        self.SPEED: float = screen_speed * self.GAME.FRAME.FIXED_DELTA_TIME
        self.START: Vector2 = self.pos.copy()
        self.DESTINATION: Vector2 = game.level.convert_unit_vector(destination)
        self.DIR: Vector2 = (self.DESTINATION - self.START).normalize()
        self.to_end: bool = True

    def fixed_step_behaviour(self) -> None:
        target: Vector2 = None
        if(self.to_end):
            target = self.DESTINATION
        else:
            target = self.START
        left = (target - self.pos).length()
        offset = self.DIR.copy() * direction(self.to_end)
        if(self.SPEED < left):
            offset *= self.SPEED
        else:
            offset *= left
            self.to_end = not self.to_end
        self.move_by(offset)
        super().fixed_step_behaviour()