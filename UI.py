import pygame
from pygame import Vector2
from BasicObjects import BasicSprite
from Utils import in_interval, vector2_div, vector2_mult, round_vector2
from collections.abc import Callable

class UI_Screen:
    def __init__(self) -> None:
        self.SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.BUTTONS: list[Button] = []

    def add_text(self, text: str, size: Vector2, pos: Vector2) -> None:
        new_text = Text(text, size, pos)
        self.SPRITES.add(new_text)

    def add_button(self, sprite_path: str, size: Vector2, pos: Vector2, callback: Callable[[], None]) -> None:
        new_button = Button(sprite_path, size, pos, callback)
        self.SPRITES.add(new_button)
        self.BUTTONS.append(new_button)

    def press_buttons(self) -> None:
        for button in self.BUTTONS:
            pressed = button.behaviour()
            if(pressed):
                break

class Text(BasicSprite):
    def __init__(self, text: str, max_size: Vector2, pos: Vector2) -> None:
        from Game import GAME
        super().__init__(None, max_size, pos)
        font = pygame.font.Font(size=self.get_max_point_size(text, max_size))
        font.align = pygame.FONT_CENTER
        img = font.render(text, True, "white", wraplength=round(max_size.x * GAME.screen_size().x))
        text_size = vector2_div(Vector2(img.size), GAME.screen_size())
        self.set_size(text_size)
        self.set_image(img)

    def get_max_point_size(self, text: str, max_size: Vector2) -> int:
        from Game import GAME
        pixel_size = round_vector2(vector2_mult(max_size, GAME.screen_size()))
        point_size = 1
        fit = True
        while fit:
            fit = False
            font = pygame.font.Font(size=point_size)
            font.align = pygame.FONT_CENTER
            text_size = Vector2(font.render(text, True, "White", wraplength=int(pixel_size.x)).size)
            if(text_size.x <= pixel_size.x and text_size.y <= pixel_size.y):
                point_size += 1
                fit = True
            else:
                point_size -= 1
        return point_size

class Button(BasicSprite):
    def __init__(self, sprite_path: str, size: Vector2, pos: Vector2, callback: Callable[[], None]) -> None:
        super().__init__(sprite_path, size, pos)
        self.CALLBACK: Callable[[], None] = callback

    def behaviour(self) -> bool:
        from Game import GAME
        pressed = False
        cursor_pos = vector2_div(Vector2(pygame.mouse.get_pos()), GAME.screen_size())
        new_keys = pygame.mouse.get_just_pressed()
        if(new_keys[0] and in_interval(cursor_pos.x, self.topleft.x, self.botright.x) and in_interval(cursor_pos.y, self.topleft.y, self.botright.y)):
            self.CALLBACK()
            pressed = True
        return pressed
