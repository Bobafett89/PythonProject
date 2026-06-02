import os
import pygame
from pygame import Vector2
from Game import Game_manager


class Basic_object(pygame.sprite.Sprite):
    def __init__(self, sprite_path: str, pos: Vector2[float, float], game: Game_manager) -> None:
        super().__init__()
        self._pos = pos
        self._SIZE = Vector2(1, 1)
        self._GAME = game

        TILE_SIZE = self.GAME.level.TILE_SIZE
        img = pygame.image.load(os.path.join(sprite_path))
        self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move_to(center=(pos * TILE_SIZE))

    @property
    def pos(self):
        return self._pos
    
    @property
    def SIZE(self):
        return self._SIZE
    
    @property
    def GAME(self):
        return self._GAME

    def get_local_map(self) -> list[list[bool, bool, bool], list[bool, bool, bool], list[bool, bool, bool]]: #returns 3x3 tilemap around the object
        ground_map = self.GAME.level.GROUND.MAP
        tile_pos = self.pos // 1
        grid = [[True, True, True], [True, True, True], [True, True, True]]
        for i in range(3):
            if((tile_pos.x != 0 or i != 0) and (tile_pos.x != len(ground_map) - 1 or i != 2)):
                for j in range(3):
                    if((tile_pos.y != 0 or j != 0) and (tile_pos.y != len(ground_map[0]) - 1 or j != 2)):
                        grid[i][j] = ground_map[int(tile_pos.x) - 1 + i][int(tile_pos.y) - 1 + j]
        return grid
    
    def get_local_pos(self) -> Vector2[float, float]: #returns position inside a tile
        pos_in_tile = self.pos.copy()
        pos_in_tile -= pos_in_tile // 1
        return pos_in_tile

    def get_border_offset(self) -> Vector2[float, float]:#returns offset from the center to border
        border_offset = self.SIZE / 2
        return border_offset

    def get_border(self) -> tuple[Vector2, Vector2]:#returns positions of the top-left and bottom-right corners of the border 
        pos_in_tile, border_offset = self.get_local_pos(), self.get_border_offset()
        top_left = pos_in_tile - border_offset
        bottom_right = pos_in_tile + border_offset
        return (top_left, bottom_right)
    
class Dynamic_object(Basic_object):
    def move(self, offset: Vector2[float, float]) -> None: #moves object by a given offset
        self._pos += offset
        self.rect = self.rect.move_to(center=(self.pos * self.GAME.level.TILE_SIZE))

    def behaviour(self) -> None: #behaviour of an object which is called every frame if it's active
        pass
