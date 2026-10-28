import pygame
from pygame import Vector2
from BasicObjects import BasicSprite
from Utils import in_interval, vector2_div, vector2_mult, round_vector2
from collections.abc import Callable

class UI_Screen:
    def __init__(self) -> None:
        self.__SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.__BUTTONS: list[Button] = []

    @property
    def SPRITES(self) -> pygame.sprite.Group:
        return self.__SPRITES

    def add_text(self, text: str, size: Vector2, pos: Vector2) -> None:
        new_text: Text = Text(text, size, pos)
        self.__SPRITES.add(new_text)

    def add_button(self, sprite_path: str, size: Vector2, pos: Vector2, callback: Callable[[], None]) -> None:
        new_button: Button = Button(sprite_path, size, pos, callback)
        self.__SPRITES.add(new_button)
        self.__BUTTONS.append(new_button)

    def press_buttons(self) -> None:
        for button in self.__BUTTONS:
            pressed: bool = button.update()
            if (pressed):
                break

class Text(BasicSprite):
    def __init__(self, text: str, max_size: Vector2, pos: Vector2) -> None:
        from Game import GAME
        super().__init__(None, max_size, pos)
        font: pygame.font.Font = pygame.font.Font(size=self.__get_max_point_size(text, max_size))
        font.align = pygame.FONT_CENTER
        img: pygame.Surface = font.render(text, True, "white", wraplength=round(max_size.x * GAME.screen_size().x))
        text_size: Vector2 = vector2_div(Vector2(img.size), GAME.screen_size())
        self._set_size(text_size)
        self._set_image(img)

    def __get_max_point_size(self, text: str, max_size: Vector2) -> int:
        from Game import GAME
        pixel_size: Vector2 = round_vector2(vector2_mult(max_size, GAME.screen_size()))
        point_size: int = 1
        fit: bool = True
        while fit:
            fit = False
            font: pygame.font.Font = pygame.font.Font(size=point_size)
            font.align = pygame.FONT_CENTER
            text_size: Vector2 = Vector2(font.render(text, True, "White", wraplength=int(pixel_size.x)).size)
            if (text_size.x <= pixel_size.x and text_size.y <= pixel_size.y):
                point_size += 1
                fit = True
            else:
                point_size -= 1
        return point_size

class Button(BasicSprite):
    def __init__(self, sprite_path: str, size: Vector2, pos: Vector2, callback: Callable[[], None]) -> None:
        super().__init__(sprite_path, size, pos)
        self.__CALLBACK: Callable[[], None] = callback

    def update(self) -> bool:
        from Game import GAME
        pressed: bool = False
        cursor_pos: Vector2 = vector2_div(Vector2(pygame.mouse.get_pos()), GAME.screen_size())
        new_keys: list[bool] = pygame.mouse.get_just_pressed()
        if(new_keys[0] and in_interval(cursor_pos.x, self.topleft.x, self.botright.x) and in_interval(cursor_pos.y, self.topleft.y, self.botright.y)):
            self.__CALLBACK()
            pressed = True
        return pressed
