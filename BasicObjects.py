import pygame
from pygame import Vector2
from Utils import vector2_mult, round_vector2, abs_vector2
from os import path

class BasicSprite(pygame.sprite.Sprite):
    from Game import Game_manager
    def __init__(self, sprite_path: str | None, screen_pos: Vector2, screen_size: Vector2, game: Game_manager) -> None:
        from Game import Game_manager
        super().__init__()
        self.GAME: Game_manager = game
        self.pos: Vector2 = screen_pos
        self.size: Vector2 = screen_size

        self.load_image(sprite_path)

    @property
    def SCREEN_SIZE(self) -> Vector2:
        return Vector2(self.GAME.FRAME.SCREEN.size)

    @property
    def edge_offset(self) -> Vector2:
        return self.size / 2

    @property
    def topleft(self) -> Vector2:
        return self.pos - self.edge_offset
    
    @property
    def botright(self) -> Vector2:
        return self.pos + self.edge_offset

    def set_center(self) -> None:
        pos = round_vector2(vector2_mult(self.pos, self.SCREEN_SIZE))
        self.rect = self.rect.move_to(center=pos)

    def move_to(self, new_pos: Vector2) -> None:
        self.pos = new_pos
        self.set_center()

    def move_by(self, offset: Vector2) -> None:
        self.move_to(self.pos + offset)

    def rescale(self) -> None:
        size = round_vector2(vector2_mult(self.size, self.SCREEN_SIZE))
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.set_center()

    def set_size(self, new_size: Vector2) -> None:
        self.size = new_size
        self.rescale()

    def set_image(self, image: pygame.Surface) -> None:
        self.image = image
        self.rescale()

    def load_image(self, sprite_path: str | None) -> None:
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
        self.set_image(img)
    
    def overlap(self, other: type[BasicSprite]) -> bool:
        dist = abs_vector2(self.pos - other.pos)
        min_dist = self.edge_offset + other.edge_offset
        return dist.x < min_dist.x and dist.y < min_dist.y

    def behaviour(self) -> None:
        pass

    def fixed_step_behaviour(self):
        pass

class LevelSprite(BasicSprite):
    def __init__(self, sprite_path, level_pos, level_size, game):
        screen_pos = game.level.convert_unit_vector(level_pos, False)
        screen_size = game.level.convert_unit_vector(level_size, False)
        super().__init__(sprite_path, screen_pos, screen_size, game)