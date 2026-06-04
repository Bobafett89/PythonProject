import os
import pygame
from pygame import Vector2
from collections.abc import Callable

class UIScreen:
    from Game import Game_manager
    def __init__(self, game: Game_manager):
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

    def check_buttons(self) -> None:
        for button in self.BUTTONS:
            pressed = button.behaviour()
            if(pressed):
                break

    

class Button(pygame.sprite.Sprite):
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: Vector2, size: Vector2, callback: Callable[[Game_manager], None], game: Game_manager):
        from Game import Game_manager
        super().__init__()
        self.__SIZE: Vector2 = size
        self.__POS: Vector2 = pos
        self.__GAME: Vector2 = game
        self.__CALLBACK: Callable[[Game_manager], None] = callback

        unit = game.FRAME.SCREEN.get_size()
        unit = ((unit[0] - 1) / 100, (unit[1] - 1) / 100)
        img = pygame.image.load(os.path.join(sprite_path))
        self.image = pygame.transform.scale(img, (size.x * unit[0], size.y * unit[1]))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move_to(center=((pos.x + size.x / 2) * unit[0], ((pos.y + size.y / 2) * unit[1])))


    @property
    def SIZE(self) -> Vector2:
        return self.__SIZE

    @property
    def POS(self) -> Vector2:
        return self.__POS

    @property
    def GAME(self) -> Game_manager:
        return self.__GAME

    @property
    def CALLBACK(self) -> Callable[[Game_manager], None]:
        return self.__CALLBACK

    def behaviour(self) -> bool:
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
