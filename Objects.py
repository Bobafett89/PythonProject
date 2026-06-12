import pygame
from pygame import Vector2
from Game import Game_manager
from BasicObjects import Basic_object, Dynamic_object
from Physics import character_physics_controller
from Structs import character_diff

class Character(Dynamic_object):
    def __init__(self, sprite_path: str, pos: pygame.typing.Point, jump_dist: float, jump_height: float, jump_time: float, dash_dist: float, dash_time: float, game: Game_manager) -> None:
        jump_force = 2 * jump_height / jump_time
        gravity = jump_force / jump_time
        speed = jump_dist / (2 * jump_time)
        dash_speed = dash_dist / dash_time

        super().__init__(sprite_path, pos, game)
        self.__PHYSICS: character_physics_controller = character_physics_controller(self, speed, jump_force, gravity, dash_dist, dash_speed)
        self._SIZE = Vector2(0.5, 1) * 0.8

        TILE_SIZE = self.GAME.level.TILE_SIZE
        self.image = pygame.transform.scale(self.image, self.SIZE * TILE_SIZE)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move_to(center=(pos * TILE_SIZE))

    @property
    def PHYSICS(self) -> character_physics_controller:
        return self.__PHYSICS
    
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
        if(new_keys[pygame.K_1]):
           self.increase_air_jumps(1)
        if(new_keys[pygame.K_2]):
           self.increase_dashes(1)

class Tilemap:
    def __init__(self, game: Game_manager) -> None:
        self.__GAME: Game_manager = game
        self.__SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.__MAP: list[list[bool]] = []
        for i in range(16 * self.__GAME.level.SIZE):
            self.MAP.append([])
            for j in range(9 * self.__GAME.level.SIZE):
                self.MAP[i].append(False)

    @property
    def SPRITES(self) -> pygame.sprite.Group:
        return self.__SPRITES
    
    @property
    def MAP(self) -> list[list[bool]]:
        return self.__MAP
    
    def addTile(self, spritePath: str, tile_pos: pygame.typing.IntPoint) -> None: #adds tile to the tilemap
        if(not self.MAP[tile_pos[0]][tile_pos[1]]):
            pos = Vector2(tile_pos) + Vector2(0.5, 0.5)
            tile = Basic_object(spritePath, pos, self.__GAME)
            self.SPRITES.add(tile)
            self.MAP[tile_pos[0]][tile_pos[1]] = True

class Static_collectable(Dynamic_object):
    def __init__(self, sprite_path: str, pos: pygame.typing.Point, diff: character_diff, game: Game_manager) -> None:
        super().__init__(sprite_path, pos, game)
        self.__DIFF: character_diff = diff
        self.__is_collected: bool = False

    @property
    def DIFF(self) -> character_diff:
        return self.__DIFF
    
    @property
    def is_collected(self) -> bool:
        return self.__is_collected

    def behaviour(self) -> None:
        character = self.GAME.level.PLAYER
        collide_with_character = self.rect.colliderect(character)
        if(collide_with_character and not self.__is_collected):
            self.GAME.level.PLAYER.give_air_jumps(self.DIFF.air_jumps)
            self.GAME.level.PLAYER.increase_air_jumps(self.DIFF.def_air_jumps)
            self.GAME.level.PLAYER.give_dashes(self.DIFF.dashes)
            self.GAME.level.PLAYER.increase_dashes(self.DIFF.def_dashes)
            self.__is_collected = True

class Dynamic_collectable(Static_collectable):
    def __init__(self, sprite_path: str, pos: pygame.typing.Point, diff: character_diff, speed: float, destination: pygame.typing.Point, game: Game_manager) -> None:
        super().__init__(sprite_path, pos, diff, game)
        self.__SPEED: float = speed
        self.__START: Vector2 = self.pos.copy()
        self.__DESTINATION: Vector2 = Vector2(destination)
        self.__DIR: Vector2 = (self.DESTINATION - self.START).normalize()
        self.__to_end: bool = True

    @property
    def SPEED(self) -> float:
        return self.__SPEED
    
    @property
    def START(self) -> Vector2:
        return self.__START

    @property
    def DESTINATION(self) -> Vector2:
        return self.__DESTINATION

    @property
    def DIR(self) -> Vector2:
        return self.__DIR

    @property
    def to_end(self) -> bool:
        return self.__to_end

    def behaviour(self) -> None:
        target: Vector2 = None
        if(self.to_end):
            target = self.DESTINATION
        else:
            target = self.START
        left = self.pos.distance_to(target)
        step = self.SPEED * self.GAME.FRAME.delta_time
        offset = self.DIR.copy()
        if(step < left):
            offset *= step
        else:
            offset *= left
            self.__to_end = not self.__to_end
        offset *= 2 * self.to_end - 1
        self.move(offset)
        super().behaviour()