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

        unit = self.GAME.FRAME.SCREEN.get_size()
        unit = ((unit[0] - 1) / 100, (unit[1] - 1) / 100)
        try:
            img = pygame.image.load(os.path.join("Assets", sprite_path))
        except:
            img = pygame.Surface(Vector2(0, 0))
            img.fill("black")
        finally:
            self.image = pygame.transform.scale(img, (self.SIZE.x * unit[0], self.SIZE.y * unit[1]))
            self.rect = self.image.get_rect()
            self.rect = self.rect.move_to(center=((self.POS.x + self.SIZE.x / 2) * unit[0], ((self.POS.y + self.SIZE.y / 2) * unit[1])))

    @property
    def SIZE(self) -> Vector2:
        return self._SIZE

    @property
    def POS(self) -> Vector2:
        return self._POS

    @property
    def GAME(self) -> Game_manager:
        return self._GAME
    
    def press(self) -> None:
        pass

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
        unit = self.GAME.FRAME.SCREEN.get_size()
        unit = ((unit[0] - 1) / 100, (unit[1] - 1) / 100)
        cursor_pos = pygame.mouse.get_pos()
        cursor_pos = (cursor_pos[0] / unit[0], cursor_pos[1] / unit[1])
        new_keys = pygame.mouse.get_just_pressed()
        if(new_keys[0] and cursor_pos[0] >= self.POS[0] and cursor_pos[0] <= self.POS[0] + self.SIZE[0] and cursor_pos[1] >= self.POS[1] and cursor_pos[1] <= self.POS[1] + self.SIZE[1]):
            self.CALLBACK(self.GAME)
            pressed = True
        return pressed
