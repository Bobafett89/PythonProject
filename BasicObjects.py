import pygame
from pygame import Vector2
from Utils import vector2_mult, vector2_div, round_vector2, abs_vector2
from os import path

class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, sprite_path: str | None, size: Vector2, pos: Vector2) -> None:
        super().__init__()
        self.__size: Vector2 = size
        self.__pos: Vector2 = pos
        self._load_image(sprite_path)

    @property
    def size(self) -> Vector2:
        return self.__size

    @property
    def pos(self) -> Vector2:
        return self.__pos

    @property
    def edge_offset(self) -> Vector2:
        return self.size / 2

    @property
    def topleft(self) -> Vector2:
        return self.pos - self.edge_offset

    @property
    def botright(self) -> Vector2:
        return self.pos + self.edge_offset

    def __set_center(self) -> None:
        from Game import GAME
        pos: Vector2 = round_vector2(vector2_mult(self.pos, GAME.screen_size()))
        self.rect = self.rect.move_to(center=pos)

    def _move_to(self, new_pos: Vector2) -> None:
        self.__pos = new_pos
        self.__set_center()

    def _move_by(self, offset: Vector2) -> None:
        self._move_to(self.pos + offset)

    def __rescale(self) -> None:
        from Game import GAME
        size: Vector2 = round_vector2(vector2_mult(self.size, GAME.screen_size()))
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.__set_center()

    def _set_size(self, new_size: Vector2) -> None:
        self.__size = new_size
        self.__rescale()

    def _set_image(self, image: pygame.Surface) -> None:
        self.image = image
        self.__rescale()

    def _load_image(self, sprite_path: str | None) -> None:
        img: pygame.Surface = None
        try:
            if(sprite_path != None):
                img = pygame.image.load(path.join("Assets", sprite_path))
            else:
                img = pygame.Surface(Vector2(0, 0), pygame.SRCALPHA)
                img.fill((0, 0, 0, 0))
        except (pygame.error, FileNotFoundError):
            img = pygame.Surface(Vector2(0, 0))
            img.fill("black")
        self._set_image(img)

    def overlap(self, other: type[BasicSprite]) -> bool:
        dist: Vector2 = abs_vector2(self.pos - other.pos)
        min_dist: Vector2 = self.edge_offset + other.edge_offset
        return dist.x < min_dist.x and dist.y < min_dist.y

    def update(self) -> None:
        pass

    def fixed_update(self) -> None:
        pass
