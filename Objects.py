import pygame
from pygame import Vector2
from BasicObjects import LevelObject
from Utils import character_diff, level_pos, Control, in_right_interval, direction, vector2_div
from math import ceil

class Character(LevelObject):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: Vector2, jump_dist: float, jump_height: float, jump_time: float, dash_dist: float, dash_time: float, game: Game_manager) -> None:
        from Physics import character_physics_controller as physics
        jump_force = 2 * jump_height / jump_time
        gravity = jump_force / jump_time
        speed = jump_dist / (2 * jump_time)
        dash_speed = dash_dist / dash_time

        super().__init__(sprite_path, pos, Vector2(0.4, 0.8), game)
        self.PHYSICS: physics = physics(self, speed, jump_force, gravity, dash_dist, dash_speed)
    
    def behaviour(self) -> None:
        keys, new_keys = pygame.key.get_pressed(), pygame.key.get_just_pressed()

        if(new_keys[pygame.K_LSHIFT]):
            self.PHYSICS.dash()

        dir = 1 * keys[pygame.K_d] - 1 * keys[pygame.K_a]
        self.PHYSICS.run(dir)

        if(keys[pygame.K_w] and self.PHYSICS.JUMP.on_ground or new_keys[pygame.K_w]):
            self.PHYSICS.jump()

        self.__debug()
    
    def fixed_step_behaviour(self, delta_time: float):
        self.PHYSICS.set_delta_time(delta_time)
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
        self.MAP: list[list[LevelObject]] = []
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
    
    def convert_to_unit(self, pos: level_pos) -> level_pos:
        return self.GAME.level.convert_pos(pos, False)
    
    def convert_to_tilemap(self, pos: level_pos) -> level_pos:
        return self.GAME.level.convert_pos(pos, True)
    
    def addTile(self, sprite_path: str, tile_pos: Vector2) -> None:
        if(self.MAP[int(tile_pos.x)][int(tile_pos.y)] == None):
            pos = self.convert_to_unit(level_pos(tile_pos, Vector2(0.5, 0.5)))
            tile = LevelObject(sprite_path, pos, self.TILE_SIZE, self.GAME)
            self.SPRITES.add(tile)
            self.MAP[int(tile_pos.x)][int(tile_pos.y)] = tile

    def getTile(self, tile_pos: Vector2, pseudo_tile: bool) -> LevelObject | None:
        if(in_right_interval(tile_pos.x, 0, len(self.MAP)) and in_right_interval(tile_pos.y, 0, len(self.MAP[0]))):
            return self.MAP[int(tile_pos.x)][int(tile_pos.y)]
        else: 
            if(pseudo_tile):
                pos = self.convert_to_unit(level_pos(tile_pos, Vector2(0.5, 0.5)))
                return LevelObject(None, pos, self.TILE_SIZE, self.GAME)
            else:
                return None

    def collides(self, object: type[LevelObject], pseudo_tiles: bool) -> list[LevelObject]:
        tilemap_pos = self.convert_to_tilemap(object.level_pos)
        border_offset = self.convert_to_tilemap(level_pos.from_vector2(object.border_offset)).to_vector2()
        tile_offset = Vector2(ceil(border_offset.x), ceil(border_offset.y))
        collisions = []
        for i in range(int(-tile_offset.x), int(tile_offset.x) + 1):
            for j in range(int(-tile_offset.y), int(tile_offset.y) + 1):
                tile = self.getTile(Vector2(tilemap_pos.unit_pos.x + i, tilemap_pos.unit_pos.y + j), pseudo_tiles)
                if(tile != None and tile.overlap(object)):
                    collisions.append(tile)
        return collisions
            
class Finish(LevelObject):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: level_pos, game: Game_manager) -> None:
        super().__init__(sprite_path, pos, Vector2(1, 1), game)

    def fixed_step_behaviour(self, delta_time) -> None:
        character = self.GAME.level.PLAYER
        if(self.overlap(character)):
            self.GAME.set_command(Control.close_level())

class Collectable(LevelObject):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: level_pos, diff: character_diff, game: Game_manager) -> None:
        super().__init__(sprite_path, pos, Vector2(1, 1), game)
        self.DIFF: character_diff = diff
        self.is_collected: bool = False

    def fixed_step_behaviour(self, delta_time: float) -> None:
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
    def __init__(self, sprite_path: str, pos: level_pos, diff: character_diff, speed: float, destination: level_pos, game: Game_manager) -> None:
        super().__init__(sprite_path, pos, diff, game)
        self.SPEED: float = speed
        self.START: level_pos = self.level_pos.copy()
        self.DESTINATION: level_pos = destination
        self.DIR: Vector2 = (self.DESTINATION - self.START).to_vector2().normalize()
        self.to_end: bool = True

    def fixed_step_behaviour(self, delta_time: float) -> None:
        target: level_pos = None
        if(self.to_end):
            target = self.DESTINATION
        else:
            target = self.START
        left = self.level_pos.vector2_to(target).length()
        step = self.SPEED * delta_time
        offset = self.DIR.copy()
        offset *= direction(self.to_end)
        if(step < left):
            offset *= step
        else:
            offset *= left
            self.to_end = not self.to_end
        self.move_by(level_pos.from_vector2(offset))
        super().fixed_step_behaviour(delta_time)