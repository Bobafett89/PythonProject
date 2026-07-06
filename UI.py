import pygame
from pygame import Vector2
from BasicObjects import BasicSprite
from Utils import in_interval, vector2_div, vector2_mult
from collections.abc import Callable

class UI_Screen:
    from Game import Game_manager
    def __init__(self, game: Game_manager) -> None:
        from Game import Game_manager
        self.SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.BUTTONS: list[Button] = []
        self.GAME: Game_manager = game
    
    def add_text(self, text: str, pos: Vector2, size: Vector2) -> None:
        new_text = Text(text, pos, size, self.GAME)
        self.SPRITES.add(new_text)
    
    def add_button(self, sprite_path: str, pos: Vector2, size: Vector2, callback: Callable[[Game_manager], None]) -> None:
        new_button = Button(sprite_path, pos, size, callback, self.GAME)
        self.SPRITES.add(new_button)
        self.BUTTONS.append(new_button)

    def press_buttons(self) -> None:
        for button in self.BUTTONS:
            pressed = button.behaviour()
            if(pressed):
                break   

class Text(BasicSprite):
    from Game import Game_manager
    def __init__(self, text: str, pos: Vector2, max_size: Vector2, game: Game_manager) -> None:
        super().__init__(None, pos, max_size, game)
        font = pygame.font.Font(size=self.get_max_point_size(text, max_size))
        font.align = pygame.FONT_CENTER
        img = font.render(text, True, "white", wraplength=int(max_size.x * self.percent.x))
        text_size = vector2_div(Vector2(img.size), self.percent)
        self.set_size(text_size)
        self.set_image(img)
    
    def get_max_point_size(self, text: str, max_size: Vector2) -> int:
        pixel_size = vector2_mult(max_size, self.percent)
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
    from Game import Game_manager
    def __init__(self, sprite_path: str, pos: Vector2, size: Vector2, callback: Callable[[Game_manager], None], game: Game_manager) -> None:
        from Game import Game_manager
        super().__init__(sprite_path, pos, size, game)
        self.CALLBACK: Callable[[Game_manager], None] = callback

    def behaviour(self) -> bool:
        pressed = False
        cursor_pos = vector2_div(Vector2(pygame.mouse.get_pos()), self.percent)
        new_keys = pygame.mouse.get_just_pressed()
        if(new_keys[0] and in_interval(cursor_pos.x, self.topleft.x, self.botright.x) and in_interval(cursor_pos.y, self.topleft.y, self.botright.y)):
            self.CALLBACK(self.GAME)
            pressed = True
        return pressed
