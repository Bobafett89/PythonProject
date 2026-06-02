import pygame
from pygame import Vector2
from Game import Game_manager
from BasicObjects import Basic_object, Dynamic_object
from Physics import character_physics_controller


class Character(Dynamic_object):
    def __init__(self, sprite_path: str, pos: Vector2, speed: float, game: Game_manager) -> None:
        super().__init__(sprite_path, pos, game)
        self.__PHYSICS = character_physics_controller(self, speed)
        self._SIZE = Vector2(0.5, 1) * 0.8

        TILE_SIZE = self.GAME.level.TILE_SIZE
        self.image = pygame.transform.scale(self.image, self.SIZE * TILE_SIZE)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move_to(center=(pos * TILE_SIZE))
    
    def behaviour(self) -> None:
        keys, new_keys = pygame.key.get_pressed(), pygame.key.get_just_pressed()

        if(new_keys[pygame.K_LSHIFT] or self.__PHYSICS.DASH.is_active):
            self.__PHYSICS.dash()

        self.__PHYSICS.apply_grav()

        dir = 1 * keys[pygame.K_d] - 1 * keys[pygame.K_a]
        self.__PHYSICS.run(dir)

        if(keys[pygame.K_w] and self.__PHYSICS.JUMP.on_ground or new_keys[pygame.K_w]):
            self.__PHYSICS.jump()

        self.__debug()
        self.__PHYSICS.collide()
        self.__PHYSICS.move()

    def death(self) -> None: #events which are fired when character dies
        self.GAME.reset_level()

    def give_air_jumps(self, count: int) -> None: #increases current air jumps by a given amount
        self.__PHYSICS.JUMP.air_jumps += count

    def give_dashes(self, count: int) -> None: #increases current dashes by a given amount
        self.__PHYSICS.DASH.count += count

    def increase_air_jumps(self, count: int) -> None: #increases default amount of air jumps by a given amount
        self.__PHYSICS.JUMP.def_air_jumps += count

    def increase_dashes(self, count: int) -> None: #increases default amount of dashes by a given amount
        self.__PHYSICS.DASH.def_count += count

    def __debug(self) -> None: #function to makes testing easier
        keys, new_keys = pygame.key.get_pressed(), pygame.key.get_just_pressed()
        if(keys[pygame.K_UP]):
            self.__PHYSICS.VELOCITY.y = -self.__PHYSICS.JUMP.force
        if(new_keys[pygame.K_1]):
           self.increase_air_jumps(1)
        if(new_keys[pygame.K_2]):
           self.increase_dashes(1)

class Tilemap:
    def __init__(self, game: Game_manager) -> None:
        self.__SPRITES = pygame.sprite.Group()
        self.__MAP = []
        self.__GAME = game
        for i in range(16 * self.__GAME.level.SIZE):
            self.MAP.append([])
            for j in range(9 * self.__GAME.level.SIZE):
                self.MAP[i].append(False)

    @property
    def SPRITES(self):
        return self.__SPRITES
    
    @property
    def MAP(self):
        return self.__MAP
    
    def addTile(self, spritePath: str, tile_pos: tuple[int, int]) -> None: #adds tile to the tilemap
        pos = Vector2(tile_pos) + Vector2(0.5, 0.5)
        tile = Basic_object(spritePath, pos, self.__GAME)
        self.SPRITES.add(tile)
        self.MAP[tile_pos[0]][tile_pos[1]] = True
