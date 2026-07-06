import pygame
from pygame import Vector2
from Utils import vector2_mult, vector2_div, level_pos
from os import path

class BasicSprite(pygame.sprite.Sprite):
    from Game import Game_manager
    def __init__(self, sprite_path: str | None, screen_pos: Vector2, screen_size: Vector2, game: Game_manager) -> None:
        from Game import Game_manager
        super().__init__()
        self.GAME: Game_manager = game
        self.percent: Vector2 = self.calc_percent()
        self.screen_pos: Vector2 = screen_pos
        self.screen_size: Vector2 = screen_size

        self.load_image(sprite_path)

    @property
    def edge_offset(self) -> Vector2:
        return self.screen_size / 2

    @property
    def topleft(self) -> Vector2:
        return self.screen_pos - self.edge_offset
    
    @property
    def botright(self) -> Vector2:
        return self.screen_pos + self.edge_offset
    
    def calc_percent(self) -> Vector2:
        return Vector2(self.GAME.FRAME.SCREEN.size) / 100

    def set_center(self) -> None:
        self.rect = self.rect.move_to(center=vector2_mult(self.screen_pos, self.percent))

    def move_to(self, new_pos: Vector2) -> None:
        self.screen_pos = new_pos
        self.set_center()

    def move_by(self, offset: Vector2) -> None:
        self.move_to(self.screen_pos + offset)

    def rescale(self) -> None:
        self.percent = self.calc_percent()
        self.image = pygame.transform.scale(self.image, vector2_mult(self.screen_size, self.percent))
        self.rect = self.image.get_rect()
        self.set_center()

    def set_size(self, new_size: Vector2) -> None:
        self.screen_size = new_size
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

    def behaviour(self) -> None:
        pass

    def fixed_step_behaviour(self, delta_time: float):
        pass
    

class LevelObject(BasicSprite):
    from Game import Game_manager
    def __init__(self, sprite_path: str | None, pos_in_level: level_pos, level_size: Vector2, game: Game_manager) -> None:
        self.GAME = game
        self.percent = self.calc_percent()
        self.level_pos: level_pos = pos_in_level
        self.level_size: Vector2 = level_size
        super().__init__(sprite_path, self.calc_screen_pos(), self.calc_screen_size(), game)

    @property
    def border_offset(self) -> Vector2:
        return self.level_size / 2
    
    @property
    def topleft_border(self) -> level_pos:
        return self.level_pos - level_pos.from_vector2(self.border_offset)
    
    @property
    def botright_border(self) -> level_pos:
        return self.level_pos + level_pos.from_vector2(self.border_offset)
    
    @property
    def UNIT_SIZE(self) -> int:
        return self.GAME.level.UNIT_SIZE
    
    @property
    def unit_pos(self) -> Vector2:
        return self.level_pos.unit_pos
    
    @property
    def local_pos(self) -> Vector2:
        return self.level_pos.local_pos

    def calc_screen_pos(self) -> Vector2:
        return vector2_div(self.unit_pos * self.UNIT_SIZE + self.local_pos * self.UNIT_SIZE, self.percent)
    
    def calc_screen_size(self) -> Vector2:
        return vector2_div(self.level_size * self.UNIT_SIZE, self.percent)

    def move_to(self, new_pos: level_pos) -> None:
        precision = 3
        new_pos.local_pos = Vector2(round(new_pos.local_pos.x, precision), round(new_pos.local_pos.y, precision))
        self.level_pos = new_pos
        super().move_to(self.calc_screen_pos())
    
    def move_by(self, offset: level_pos) -> None:
        self.move_to(self.level_pos + offset)

    def set_size(self, new_size: Vector2) -> None:
        self.level_size = new_size
        super().set_size(self.calc_screen_size())

    def overlap(self, other: type[LevelObject]) -> bool:
        dist = self.level_pos.vector2_to(other.level_pos)
        return abs(dist.x) < self.border_offset.x + other.border_offset.x and abs(dist.y) < self.border_offset.y + other.border_offset.y