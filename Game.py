import pygame
from pygame import Vector2
from BasicObjects import Control, Command, Frame
from LevelObjects import Level
from UI import UI
from os import path
from json import loads, decoder
from collections.abc import Callable
from typing import Any, TextIO

class GAME:
    __active: bool = None
    __FRAME: Frame = None
    __UI: UI = None
    __level: Level = None
    __control: Control = None

    @classmethod
    def active(cls) -> bool:
        return cls.__active

    @classmethod
    def init(cls) -> None:
        cls.__active = False
        cls.__FRAME = Frame()
        cls.__UI = UI()
        cls.__control = Control.wait()

    @classmethod
    def start(cls, start_menu: UIScreen) -> None:
        cls.__UI.set_start_menu(start_menu)
        cls.__open_main_menu()
        cls.__active = True

    @classmethod
    def set_command(cls, command: Control) -> None:
        if (command.command.value > cls.__control.command.value):
            cls.__control = command

    @classmethod
    def execute_command(cls) -> None:
        match cls.__control.command:
            case Command.WAIT:
                pass
            case Command.OPEN_MENU:
                cls.__open_main_menu()
            case Command.SWITCH_UI:
                cls.__FRAME.remove_sprite_group(cls.__UI.SPRITES)
                cls.__UI.switch_ui(cls.__control.parameter)
                cls.__FRAME.add_sprite_group(cls.__UI.SPRITES)
            case Command.OPEN_LEVEL:
                try:
                    cls.__start_level_from_file(cls.__control.parameter)
                except RuntimeError:
                    pass
            case Command.RESTART_LEVEL:
                cls.__reset_level()
            case Command.CLOSE_LEVEL:
                cls.__close_level()
            case Command.CLOSE_GAME:
                cls.__close_game()
        cls.__control = Control.wait()

    @classmethod
    def update(cls) -> None:
        button_command: Control = cls.__UI.press_buttons()
        cls.set_command(button_command)
        if (cls.__level != None):
            cls.__level.logic(int(Frame.fixed_steps()))
            cls.set_command(cls.__level.command)

    @classmethod
    def next_frame(cls) -> None:
        cls.__FRAME.render()
        cls.__FRAME.next()

    @classmethod
    def __start_level_from_file(cls, level_name: str) -> None:
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
                    cls.__start_level(generator, Vector2(level_structure["tilemap_size"]))

    @classmethod
    def __start_level(cls, generator: Callable[[Level], None], tilemap_size: Vector2) -> None:
        cls.__level = Level(generator, tilemap_size)
        cls.__UI.clear_ui()
        cls.__FRAME.clear_sprite_group()
        cls.__FRAME.add_sprite_group(cls.__level.SPRITES)
        cls.__FRAME.add_sprite_group(cls.__level.TILEMAP_SPRITES)

    @classmethod
    def __close_level(cls) -> None:
        cls.__level = None
        cls.__open_main_menu()

    @classmethod
    def __reset_level(cls) -> None:
        level = cls.__level
        cls.__start_level(level.GENERATOR, level.TILEMAP_SIZE)

    @classmethod
    def __open_main_menu(cls) -> None:
        cls.__FRAME.clear_sprite_group()
        cls.__UI.open_start_menu()
        cls.__FRAME.add_sprite_group(cls.__UI.SPRITES)

    @classmethod
    def __close_game(cls) -> None:
        cls.__active = False

