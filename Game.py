import pygame
from pygame import Vector2
from BasicObjects import Control, Command, Frame
from LevelObjects import Level, LevelState
from UI import UI
from os import path
from json import loads, decoder
from collections.abc import Callable
from typing import Any, TextIO

class Game:
    def __init__(self) -> None:
        self.__active: bool = False
        self.__FRAME: Frame = Frame()
        self.__UI: UI = UI()
        self.__level: Level = None
        self.__control: Control = Control.wait()

    @property
    def active(self) -> bool:
        return self.__active

    def start(self, start_menu: UIScreen) -> None:
        self.__UI.set_start_menu(start_menu)
        self.__open_main_menu()
        self.__active = True

    def set_command(self, command: Control) -> None:
        if (command.command.value > self.__control.command.value):
            self.__control = command

    def execute_command(self) -> None:
        match self.__control.command:
            case Command.WAIT:
                pass
            case Command.OPEN_MENU:
                self.__open_main_menu()
            case Command.SWITCH_UI:
                self.__FRAME.remove_sprite_group(self.__UI.SPRITES)
                self.__UI.switch_ui(self.__control.parameter)
                self.__FRAME.add_sprite_group(self.__UI.SPRITES)
            case Command.OPEN_LEVEL:
                try:
                    self.__start_level_from_file(self.__control.parameter)
                except RuntimeError:
                    pass
            case Command.CLOSE_LEVEL:
                self.__close_level()
            case Command.CLOSE_GAME:
                self.__close_game()
        self.__control = Control.wait()

    def update(self) -> None:
        button_command: Control = self.__UI.press_buttons()
        self.set_command(button_command)
        if (self.__level != None):
            self.__level.logic(int(Frame.fixed_steps()))
            if (self.__level.state == LevelState.FINISHED):
                self.set_command(Control.close_level())

    def next_frame(self) -> None:
        self.__FRAME.render()
        self.__FRAME.next()

    def __start_level_from_file(self, level_name: str) -> None:
        level_name: str = path.join("Levels", level_name)
        try:
            level_file: TextIO = open(level_name)
        except FileNotFoundError:
            raise RuntimeError("File doesn't exist")
        else:
            json_str: str = level_file.read()
            level_file.close()
            try:
                level_structure: dict[str, Any] = loads(json_str)
            except decoder.JSONDecodeError:
                raise RuntimeError("Json has wrong formating")
            else:
                try:
                    generator: Callable[[Level], None] = Level.parse_level(level_structure)
                except RuntimeError:
                    raise RuntimeError("Json has wrong structure")
                else:
                    self.__start_level(generator, Vector2(level_structure["tilemap_size"]))

    def __start_level(self, generator: Callable[[Level], None], tilemap_size: Vector2) -> None:
        self.__level = Level(generator, tilemap_size)
        self.__UI.clear_ui()
        self.__FRAME.clear_sprite_group()
        self.__FRAME.add_sprite_group(self.__level.SPRITES)

    def __close_level(self) -> None:
        self.__level = None
        self.__open_main_menu()

    def __open_main_menu(self) -> None:
        self.__FRAME.clear_sprite_group()
        self.__UI.open_start_menu()
        self.__FRAME.add_sprite_group(self.__UI.SPRITES)

    def __close_game(self) -> None:
        self.__active = False

