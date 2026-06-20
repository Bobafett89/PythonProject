import os
import pygame
from pygame import Vector2
from collections.abc import Callable

class UI_Screen:
    from Game import Game_manager
    def __init__(self, game: Game_manager) -> None:
        from Game import Game_manager
        self.__SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.__BUTTONS: list[Button] = []
        self.__GAME: Game_manager = game

    @property
    def SPRITES(self) -> pygame.sprite.Group:
        return self.__SPRITES

    @property
    def BUTTONS(self) -> list[Button]:
        return self.__BUTTONS
    
    @property
    def GAME(self) -> Game_manager:
        return self.__GAME
    
    def add_text(self, text: str, pos: Vector2, size: Vector2):
        new_text = Text(text, pos, size, self.GAME)
        self.SPRITES.add(new_text)
    
    def add_button(self, sprite_path: str, pos: Vector2, size: Vector2, callback: Callable[[Game_manager], None]) -> None:
        new_button = Button(sprite_path, pos, size, callback, self.GAME)
        self.SPRITES.add(new_button)
        self.BUTTONS.append(new_button)

    def press_buttons(self) -> None:
        for button in self.BUTTONS:
            pressed = button.press()
            if(pressed):
                break   

class Basic_UI(pygame.sprite.Sprite):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: Vector2, size: Vector2, game: Game_manager) -> None:
        from Game import Game_manager
        super().__init__()
        self._SIZE: Vector2 = size
        self._POS: Vector2 = pos
        self._GAME: Game_manager = game
        self.unit: Vector2 = Vector2(self.GAME.FRAME.SCREEN.get_size())
        self.unit: Vector2 = Vector2((self.unit.x - 1) / 100, (self.unit.y - 1) / 100)

        try:
            img = pygame.image.load(os.path.join("Assets", sprite_path))
        except:
            img = pygame.Surface(Vector2(0, 0))
            img.fill("black")
        finally:
            self.image = pygame.transform.scale(img, (self.SIZE.x * self.unit.x, self.SIZE.y * self.unit.y))
            self.rect = self.image.get_rect()
            self.rect = self.rect.move_to(center=((self.POS.x + self.SIZE.x / 2) * self.unit.x, ((self.POS.y + self.SIZE.y / 2) * self.unit.y)))

    @property
    def SIZE(self) -> Vector2:
        return self._SIZE

    @property
    def POS(self) -> Vector2:
        return self._POS

    @property
    def GAME(self) -> Game_manager:
        return self._GAME

class Text(Basic_UI):
    from Game import Game_manager
    def __init__(self, text: str, pos: Vector2, size: Vector2, game: Game_manager):
        super().__init__("", pos, size, game)
        font = pygame.font.Font(size=self.get_max_point_size(text, size))
        font.align = pygame.FONT_CENTER
        img = font.render(text, True, "white", wraplength=int(size.x * self.unit.x))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect = self.rect.move_to(center=((pos.x + size.x / 2) * self.unit.x, ((pos.y + size.y / 2) * self.unit.y)))
    
    def get_max_point_size(self, text: str, size: Vector2):
        pixel_size = Vector2(size.x * self.unit.x, size.y * self.unit.y)
        point_size = 1
        fit = True
        while fit:
            fit = False
            font = pygame.font.Font(size=point_size)
            font.align = pygame.FONT_CENTER
            text_size = Vector2(font.render(text, True, "White", wraplength=int(pixel_size.x)).size)
            if(text_size.x < pixel_size.x and text_size.y < pixel_size.y):
                point_size += 1
                fit = True
        return point_size - 1

class Button(Basic_UI):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: Vector2, size: Vector2, callback: Callable[[Game_manager], None], game: Game_manager) -> None:
        from Game import Game_manager
        super().__init__(sprite_path, pos, size, game)
        self.__CALLBACK: Callable[[Game_manager], None] = callback

    @property
    def CALLBACK(self) -> Callable[[Game_manager], None]:
        return self.__CALLBACK

    def press(self) -> bool:
        pressed = False
        cursor_pos = pygame.mouse.get_pos()
        cursor_pos = (cursor_pos[0] / self.unit.x, cursor_pos[1] / self.unit.y)
        new_keys = pygame.mouse.get_just_pressed()
        if(new_keys[0] and cursor_pos[0] >= self.POS[0] and cursor_pos[0] <= self.POS[0] + self.SIZE[0] and cursor_pos[1] >= self.POS[1] and cursor_pos[1] <= self.POS[1] + self.SIZE[1]):
            self.CALLBACK(self.GAME)
            pressed = True
        return pressed
