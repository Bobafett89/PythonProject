import os
import pygame
from pygame import Vector2
from Game import Game_manager

class Basic_object(pygame.sprite.Sprite):
    def __init__(self, sprite_path: str, pos: pygame.typing.Point, game: Game_manager) -> None:
        super().__init__()
        self._tile_pos: Vector2 = Vector2(pos) // 1
        self._local_pos = Vector2(pos) - self._tile_pos
        self._SIZE: Vector2 = Vector2(1, 1)
        self._GAME: Game_manager = game

        try:
            img = pygame.image.load(os.path.join("Assets", sprite_path))
        except:
            img = pygame.Surface(Vector2(0, 0))
            img.fill("black")
        finally:
            TILE_SIZE = self.GAME.level.TILE_SIZE
            self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            self.rect = self.image.get_rect()
            self.rect = self.rect.move_to(center=(self.tile_pos * self.GAME.level.TILE_SIZE + self.local_pos * self.GAME.level.TILE_SIZE))

    @property
    def pos(self) -> Vector2:
        return self._tile_pos + self._local_pos
    
    @property
    def tile_pos(self) -> Vector2:
        return self._tile_pos

    @property
    def local_pos(self) -> Vector2:
        return self._local_pos

    @property
    def SIZE(self) -> Vector2:
        return self._SIZE
    
    @property
    def GAME(self) -> Game_manager:
        return self._GAME
    
    @property
    def border_offset(self) -> Vector2:
        return self.SIZE / 2

    @property
    def local_border(self) -> tuple[Vector2, Vector2]:
        pos_in_tile, border_offset = self.local_pos, self.border_offset
        top_left = pos_in_tile - border_offset
        bottom_right = pos_in_tile + border_offset
        return (top_left, bottom_right)
    
    def overlap(self, tile_pos: pygame.typing.IntPoint, local_pos: Vector2, size: Vector2) -> bool:
        border_offset = size / 2
        dist = (self.tile_pos - tile_pos) + (self.local_pos - local_pos)
        return abs(dist.x) <= self.border_offset.x + border_offset.x and abs(dist.y) <= self.border_offset.y + border_offset.y
    
class Dynamic_object(Basic_object):
    def premove(self, offset: pygame.typing.Point) -> tuple[Vector2, Vector2]:
        offset_integer = Vector2(offset) // 1
        offset_float = Vector2(offset) - offset_integer
        tile_pos = self.tile_pos + offset_integer
        local_pos = self.local_pos + offset_float
        if(local_pos.x < 0 or 1 <= local_pos.x):
            dir = 2 * (local_pos.x >= 1) - 1
            local_pos.x -= dir
            tile_pos.x += dir
        if(local_pos.y < 0 or 1 <= local_pos.y):
            dir = 2 * (local_pos.y >= 1) - 1
            local_pos.y -= dir
            tile_pos.y += dir
        return (tile_pos, Vector2(round(local_pos.x, 5), round(local_pos.y, 5)))

    def move(self, offset: pygame.typing.Point) -> None: #moves object by a given offset
        self._tile_pos, self._local_pos = self.premove(offset)
        self.rect = self.rect.move_to(center=(self.tile_pos * self.GAME.level.TILE_SIZE + self.local_pos * self.GAME.level.TILE_SIZE))

    def behaviour(self) -> None: #behaviour of an object which is called every frame if it's active
        pass
