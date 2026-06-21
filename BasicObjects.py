import os
import pygame
from pygame import Vector2
from Game import Game_manager
from Utils import vector2_add_num, vector2_mult

class BasicSprite(pygame.sprite.Sprite):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: Vector2, size: Vector2, game: Game_manager):
        from Game import Game_manager
        super().__init__()
        self.GAME: Game_manager = game
        self.screen_size: Vector2 = size
        self.screen_pos: Vector2 = pos
        self.unit: Vector2 = vector2_add_num(Vector2(self.GAME.FRAME.SCREEN.size), -1) / 100

        self.load_image(sprite_path)

    def move_to(self, new_pos: Vector2) -> None:
        self.screen_pos = new_pos
        self.rect = self.rect.move_to(center=vector2_mult(self.screen_pos, self.unit))

    def move_by(self, offset: Vector2) -> None:
        self.move_to(self.screen_pos + offset)

    def rescale(self, new_size: Vector2) -> None:
        self.screen_size = new_size
        self.unit = vector2_add_num(Vector2(self.GAME.FRAME.SCREEN.size), -1) / 100
        self.image = pygame.transform.scale(self.image, (self.screen_size.x * self.unit.x, self.screen_size.y * self.unit.y))
        self.rect = self.image.get_rect()
        self.move_to(self.screen_pos)

    def set_image(self, image: pygame.Surface) -> None:
        self.image = image
        self.rescale(self.screen_size)

    def load_image(self, sprite_path: str) -> None:
        img: pygame.Surface = None
        try:
            if(sprite_path != None):
                img = pygame.image.load(os.path.join("Assets", sprite_path))
            else:
                img = pygame.Surface(Vector2(0, 0), pygame.SRCALPHA)
                img.fill((0, 0, 0, 0))
        except (pygame.error, FileNotFoundError):
            img = pygame.Surface(Vector2(0, 0))
            img.fill("black")
        self.set_image(img)

    def behaviour(self) -> None:
        pass
    
    @property
    def edge_offset(self) -> Vector2:
        return self.screen_size / 2

    @property
    def topleft(self) -> Vector2:
        return self.screen_pos - self.edge_offset
    
    @property
    def botright(self) -> Vector2:
        return self.screen_pos + self.edge_offset
    
    @property
    def edges(self) -> tuple[Vector2, Vector2]:
        return (self.screen_topleft, self.screen_bottomright)

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
