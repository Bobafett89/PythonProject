from math import ceil
import pygame
from pygame import Vector2
from BasicObjects import LevelObject
from Utils import character_diff, level_pos, in_right_interval, direction

class Character(LevelObject):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: Vector2, jump_dist: float, jump_height: float, jump_time: float, dash_dist: float, dash_time: float, game: Game_manager) -> None:
        from Physics import character_physics_controller
        jump_force = 2 * jump_height / jump_time
        gravity = jump_force / jump_time
        speed = jump_dist / (2 * jump_time)
        dash_speed = dash_dist / dash_time

        super().__init__(sprite_path, pos, Vector2(0.4, 0.8), game)
        self.PHYSICS: character_physics_controller = character_physics_controller(self, speed, jump_force, gravity, dash_dist, dash_speed)
    
    def behaviour(self) -> None:
        keys, new_keys = pygame.key.get_pressed(), pygame.key.get_just_pressed()

        if(new_keys[pygame.K_LSHIFT] or self.PHYSICS.DASH.is_active):
            self.PHYSICS.dash()

        self.PHYSICS.apply_grav()

        dir = 1 * keys[pygame.K_d] - 1 * keys[pygame.K_a]
        self.PHYSICS.run(dir)

        if(keys[pygame.K_w] and self.PHYSICS.JUMP.on_ground or new_keys[pygame.K_w]):
            self.PHYSICS.jump()

        self.__debug()
        self.PHYSICS.collide()
        self.PHYSICS.move()

    def give_air_jumps(self, count: int) -> None: #increases current air jumps by a given amount
        self.PHYSICS.JUMP.air_jumps += count

    def give_dashes(self, count: int) -> None: #increases current dashes by a given amount
        self.PHYSICS.DASH.count += count

    def increase_air_jumps(self, count: int) -> None: #increases default amount of air jumps by a given amount
        self.PHYSICS.JUMP.def_air_jumps += count

    def increase_dashes(self, count: int) -> None: #increases default amount of dashes by a given amount
        self.PHYSICS.DASH.def_count += count

    def __debug(self) -> None: #function to makes testing easier
        keys, new_keys = pygame.key.get_pressed(), pygame.key.get_just_pressed()
        if(keys[pygame.K_UP]):
            self.PHYSICS.VELOCITY.y = -self.PHYSICS.JUMP.force
        if(keys[pygame.K_DOWN]):
            self.PHYSICS.VELOCITY.y = self.PHYSICS.JUMP.force
        if(new_keys[pygame.K_1]):
           self.increase_air_jumps(1)
        if(new_keys[pygame.K_2]):
           self.increase_dashes(1)

class Tilemap:
    from Game import Game_manager
    def __init__(self, game: Game_manager) -> None:
        from Game import Game_manager
        self.GAME: Game_manager = game
        self.SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.MAP: list[list[LevelObject]] = []
        for i in range(16 * self.GAME.level.SIZE):
            self.MAP.append([])
            for j in range(9 * self.GAME.level.SIZE):
                self.MAP[i].append(None)
    
    def addTile(self, sprite_path: str, tile_pos: Vector2) -> None: #adds tile to the tilemap
        if(self.MAP[int(tile_pos.x)][int(tile_pos.y)] == None):
            tile = LevelObject(sprite_path, level_pos(tile_pos, Vector2(0.5, 0.5)), Vector2(1, 1), self.GAME)
            self.SPRITES.add(tile)
            self.MAP[int(tile_pos.x)][int(tile_pos.y)] = tile

    def getTile(self, tile_pos: Vector2, pseudo_tile: bool) -> LevelObject | None:
        if(in_right_interval(tile_pos.x, 0, len(self.MAP)) and in_right_interval(tile_pos.y, 0, len(self.MAP[0]))):
            return self.MAP[int(tile_pos.x)][int(tile_pos.y)]
        else: 
            if(pseudo_tile):
                return LevelObject(None, level_pos(tile_pos, Vector2(0.5, 0.5)), Vector2(1, 1), self.GAME)
            else:
                return None

    def collides(self, object: type[LevelObject], pseudo_tiles: bool) -> list[LevelObject]:
        tile_offset = Vector2(ceil(object.border_offset.x), ceil(object.border_offset.y))
        collisions = []
        for i in range(int(-tile_offset.x), int(tile_offset.x) + 1):
            for j in range(int(-tile_offset.y), int(tile_offset.y) + 1):
                tile = self.getTile(Vector2(object.tile_pos.x + i, object.tile_pos.y + j), pseudo_tiles)
                if(tile != None and tile.overlap(object)):
                    collisions.append(tile)
        return collisions
            
class Finish(LevelObject):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: level_pos, game: Game_manager) -> None:
        super().__init__(sprite_path, pos, Vector2(1, 1), game)

    def behaviour(self) -> None:
        character = self.GAME.level.PLAYER
        if(self.overlap(character)):
            self.GAME.close_level()

class Collectable(LevelObject):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: level_pos, diff: character_diff, game: Game_manager) -> None:
        super().__init__(sprite_path, pos, Vector2(1, 1), game)
        self.DIFF: character_diff = diff
        self.is_collected: bool = False

    def behaviour(self) -> None:
        character = self.GAME.level.PLAYER
        collide_with_character = self.overlap(character)
        if(collide_with_character and not self.is_collected):
            self.GAME.level.PLAYER.give_air_jumps(self.DIFF.air_jumps)
            self.GAME.level.PLAYER.increase_air_jumps(self.DIFF.def_air_jumps)
            self.GAME.level.PLAYER.give_dashes(self.DIFF.dashes)
            self.GAME.level.PLAYER.increase_dashes(self.DIFF.def_dashes)
            self.is_collected = True

class MovingCollectable(Collectable):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: level_pos, diff: character_diff, speed: float, destination: level_pos, game: Game_manager) -> None:
        super().__init__(sprite_path, pos, diff, game)
        self.SPEED: float = speed
        self.START: level_pos = self.level_pos.copy()
        self.DESTINATION: level_pos = destination
        self.DIR: Vector2 = (self.DESTINATION - self.START).to_vector2().normalize()
        self.to_end: bool = True

    def behaviour(self) -> None:
        target: level_pos = None
        if(self.to_end):
            target = self.DESTINATION
        else:
            target = self.START
        left = self.level_pos.vector2_to(target).length()
        step = self.SPEED * self.GAME.FRAME.delta_time
        offset = self.DIR.copy()
        if(step < left):
            offset *= step
        else:
            offset *= left
            self.to_end = not self.to_end
        offset *= direction(self.to_end)
        self.move_by(level_pos.from_vector2(offset))
        super().behaviour()