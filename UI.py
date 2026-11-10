import pygame
from pygame import Vector2
from BasicObjects import BasicSprite, Transform, Control
from Utils import in_rect, vector2_div, vector2_mult, round_vector2, Interval
from collections.abc import Callable

class UI:
    def __init__(self) -> None:
        self.__start_menu: UIScreen = None
        self.__current_screen: UIScreen = None

    @property
    def SPRITES(self) -> pygame.sprite.Group | None:
        if (self.__current_screen != None):
            return self.__current_screen.SPRITES
        else:
            return None

    def set_start_menu(self, start_menu: UIScreen) -> None:
        self.__start_menu = start_menu

    def open_start_menu(self) -> None:
        self.switch_ui(self.__start_menu)

    def switch_ui(self, screen: UIScreen) -> None:
        self.clear_ui()
        self.__current_screen = screen

    def clear_ui(self) -> None:
        self.__current_screen = None

    def press_buttons(self) -> Control:
        command: Control = None
        if (self.__current_screen != None):
            command = self.__current_screen.press_buttons()
        if (command == None):
            command = Control.wait()
        return command

class UIScreen:
    def __init__(self) -> None:
        self.__SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.__BUTTONS: list[Button] = []

    @property
    def SPRITES(self) -> pygame.sprite.Group:
        return self.__SPRITES

    def add_text(self, text: str, transform: Transform) -> None:
        new_text: Text = Text(text, transform)
        self.__SPRITES.add(new_text)

    def add_button(self, sprite_path: str, transform: Transform, callback: Callable[[], Control]) -> None:
        new_button: Button = Button(sprite_path, transform, callback)
        self.__SPRITES.add(new_button)
        self.__BUTTONS.append(new_button)

    def press_buttons(self) -> Control | None:
        command: Control = None
        for button in self.__BUTTONS:
            command = button.update()
            if (command != None):
                break
        return command

class Text(BasicSprite):
    def __init__(self, text: str, transform: Transform) -> None:
        super().__init__(None, transform)
        font: pygame.font.Font = pygame.font.Font(size = self.__get_max_point_size(text, transform.size))
        font.align = pygame.FONT_CENTER
        img: pygame.Surface = font.render(text, True, "white", wraplength = round(transform.size.x * self.screen_size.x))
        text_size: Vector2 = vector2_div(Vector2(img.size), self.screen_size)
        self._set_size(text_size)
        self._set_image(img)

    def __get_max_point_size(self, text: str, max_size: Vector2) -> int:
        pixel_size: Vector2 = round_vector2(vector2_mult(max_size, self.screen_size))
        point_size: int = 1
        fit: bool = True
        while fit:
            fit = False
            font: pygame.font.Font = pygame.font.Font(size = point_size)
            font.align = pygame.FONT_CENTER
            text_size: Vector2 = Vector2(font.render(text, True, "White", wraplength = int(pixel_size.x)).size)
            if (text_size.x <= pixel_size.x and text_size.y <= pixel_size.y):
                point_size += 1
                fit = True
            else:
                point_size -= 1
        return point_size

class Button(BasicSprite):
    def __init__(self, sprite_path: str, transform: Transform, callback: Callable[[], Control]) -> None:
        super().__init__(sprite_path, transform)
        self.__CALLBACK: Callable[[], Control] = callback

    def update(self) -> Control | None:
        command: Control = None
        cursor_pos: Vector2 = vector2_div(Vector2(pygame.mouse.get_pos()), self.screen_size)
        new_keys: list[bool] = pygame.mouse.get_just_pressed()
        if (new_keys[0] and in_rect(cursor_pos, self.topleft, self.botright, Interval.CLOSED)):
            command = self.__CALLBACK()
        return command

