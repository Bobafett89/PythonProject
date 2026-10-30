import pygame
from pygame import Vector2
from Utils import character_diff, Control, Command, clamp, vector2_div, vector2_mult
from math import floor
from os import path
from json import loads, decoder
from collections.abc import Callable

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
    def screen_size(cls) -> Vector2:
        return cls.__FRAME.screen_size

    @classmethod
    def dt(cls) -> float:
        return cls.__FRAME.dt

    @classmethod
    def fixed_dt(cls) -> float:
        return cls.__FRAME.fixed_dt

    @classmethod
    def fixed_steps(cls) -> int:
        return cls.__FRAME.fixed_steps

    @classmethod
    def init(cls) -> None:
        cls.__active: bool = False
        cls.__FRAME: Frame = Frame()
        cls.__UI = UI()
        cls.__control: Control = Control.wait()

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
                    cls.__start_levev_from_file(cls.__control.parameter)
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
        cls.__UI.press_buttons()
        if (cls.__level != None):
            cls.__level.logic()

    @classmethod
    def next_frame(cls) -> None:
        cls.__FRAME.render()
        cls.__FRAME.next()

    @classmethod
    def __start_levev_from_file(cls, level_name: str) -> None:
        level_name = path.join("Levels", level_name)
        try:
            level_file = open(level_name)
        except FileNotFoundError:
            raise RuntimeError("File doesn't exist")
        else:
            json_str = level_file.read()
            level_file.close()
            try:
                level_structure = loads(json_str)
            except decoder.JSONDecodeError:
                raise RuntimeError("Json has wrong formating")
            else:
                try:
                    generator = Level.parse_level(level_structure)
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

class UI:
    def __init__(self) -> None:
        from UI import UI_Screen
        self.__start_menu: UI_Screen = None
        self.__current_screen: UI_Screen = None

    @property
    def SPRITES(self) -> pygame.sprite.Group | None:
        if (self.__current_screen != None):
            return self.__current_screen.SPRITES
        else:
            return None

    def set_start_menu(self, start_menu: UI_Screen) -> None:
        self.__start_menu = start_menu

    def open_start_menu(self) -> None:
        self.switch_ui(self.__start_menu)

    def switch_ui(self, screen: UI_Screen) -> None:
        self.clear_ui()
        self.__current_screen = screen

    def clear_ui(self) -> None:
        self.__current_screen = None

    def press_buttons(self) -> None:
        if (self.__current_screen != None):
            self.__current_screen.press_buttons()

class Frame:
    _FIXED_DT: float = 1 / 50
    _MAX_DT: float = 1 / 30

    @property
    def dt(self) -> float:
        return self.__dt

    @property
    def fixed_dt(self) -> float:
        return self._FIXED_DT

    @property
    def fixed_steps(self) -> int:
        return self.__fixed_steps

    @property
    def screen_size(self) -> Vector2:
        return Vector2(self.__SCREEN.get_size())

    def __init__(self) -> None:
        screen_flags = pygame.FULLSCREEN | pygame.SCALED
        self.__SCREEN: pygame.Surface = pygame.display.set_mode((1920, 1080), screen_flags)
        self.__CLOCK: pygame.Clock = pygame.time.Clock()
        self.__RENDER_GROUPS: list[pygame.sprite.Group] = []
        self.__dt: float = 0
        self.__acc_dt: float = 0
        self.__fixed_steps: int = 0

    def next(self) -> None:
        self.__dt = clamp(self.__CLOCK.tick(1000) / 1000, 0, Frame._MAX_DT)
        self.__acc_dt += self.__dt
        self.__fixed_steps = floor(self.__acc_dt / self._FIXED_DT)
        self.__acc_dt -= Frame._FIXED_DT * self.__fixed_steps

    def render(self) -> None:
        self.__SCREEN.fill("#333333")
        for render_group in self.__RENDER_GROUPS:
            render_group.draw(self.__SCREEN)
        pygame.display.flip()

    def add_sprite_group(self, group: pygame.sprite.Group) -> None:
        if (group not in self.__RENDER_GROUPS):
            self.__RENDER_GROUPS.append(group)

    def remove_sprite_group(self, group: pygame.sprite.Group) -> None:
        if (group in self.__RENDER_GROUPS):
            self.__RENDER_GROUPS.remove(group)

    def clear_sprite_group(self) -> None:
        self.__RENDER_GROUPS.clear()

class Level:
    _DEF_LEVEL_SIZE: Vector2 = Vector2(16, 9)
    _DEF_TILEMAP_LAYERS: list[str] = ["ground", "hazard"]

    def __init__(self, generator: Callable[[Level], None], tilemap_size: Vector2) -> None:
        from Objects import Tilemap, Character
        self.__SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.__GENERATOR: Callable[[Level], None] = generator
        self.__TILEMAP: Tilemap = Tilemap(tilemap_size)
        self.__OBJECTS: list[type[BasicSprite]] = []
        self.__COLLECTABLES: list[type[Collectable]] = []
        self.__PLAYER: Character = None
        self.__build_level()

    @property
    def SPRITES(self) -> pygame.sprite.Group:
        return self.__SPRITES

    @property
    def TILEMAP_SPRITES(self) -> pygame.sprite.Group:
        return self.__TILEMAP.SPRITES

    @property
    def TILEMAP_SIZE(self) -> Vector2:
        return self.__TILEMAP.SIZE

    @property
    def GENERATOR(self) -> Callable[[Level], None]:
        return self.__GENERATOR

    @classmethod
    def parse_level(cls, level_struct: dict) -> Callable[[Level], None]:
        def has_keys(keys: list[str] | str, where: dict, type: type | tuple[type, ...]) -> bool:
            has: bool = None
            if (isinstance(keys, str)):
                has = keys in where and isinstance(where[keys], type)
            else:
                has = True
                for key in keys:
                    if (not (key in where and isinstance(where[key], type))):
                        has = False
                        break
            return has

        def has_sprite(where: dict):
            return has_keys("spr", where, str)

        def validate_list(arr: list, size: int, type: type) -> bool:
            valid = False
            if (len(arr) == size or size == 0):
                valid = True
                for element in arr:
                    if (not isinstance(element, type)):
                        valid = False
                        break
            return valid

        def validate_point(pos: list, is_int: bool = False) -> bool:
            pos_type: type | tuple[type, ...] = None
            if (is_int):
                pos_type = int
            else:
                pos_type = (int, float)
            return validate_list(pos, 2, pos_type)

        def validate_poses(poses: list, is_int: bool = False, include_lines: bool = False) -> bool:
            valid = validate_list(poses, 0, list)
            if (valid):
                for pos in poses:
                    valid_point = validate_point(pos, is_int)
                    valid_line = include_lines and validate_list(pos, 2, list) and validate_point(pos[0], is_int) and validate_point(pos[1], is_int)
                    if (not (valid_point or valid_line)):
                        valid = False
                        break
            return valid

        def has_valid_pos(where: dict) -> bool:
            return has_keys("pos", where, list) and validate_point(where["pos"])

        def has_valid_poses(where: dict) -> bool:
            return has_keys("pos", where, list) and validate_poses(where["pos"])

        def has_valid_size(where: dict) -> bool:
            return has_keys("size", where, list) and validate_point(where["size"])

        def validate_tilemap(tilemap: list) -> bool:
            valid_tilemap = True
            for tile in tilemap:
                valid_sprite = has_sprite(tile)
                valid_pos = has_keys("pos", tile, list) and validate_poses(tile["pos"], True, True)
                valid_tilemap = valid_sprite and valid_pos
                if (not valid_tilemap):
                    break
            return valid_tilemap

        def generator(level: Level) -> None:
            level_size: Vector2 = cls._DEF_LEVEL_SIZE * level_struct["size_factor"]

            def point_to_vector(point: list[float | int]):
                return Vector2(point[0], point[1])

            def build_tilemap(tilemap: list[dict], add_tile: Callable[[str, Vector2], None]):
                for tile in tilemap:
                    for pos in tile["pos"]:
                        if (isinstance(pos[0], list)):
                            first_pos = point_to_vector(pos[0])
                            second_pos = point_to_vector(pos[1])
                            leftop = Vector2(min(first_pos.x, second_pos.x), min(first_pos.y, second_pos.y))
                            botright = Vector2(max(first_pos.x, second_pos.x), max(first_pos.y, second_pos.y))
                            size = botright - leftop + Vector2(1, 1)
                            for i in range(int(size.x)):
                                for j in range(int(size.y)):
                                    offset = Vector2(i, j)
                                    add_tile(tile["spr"], leftop + offset)
                        else:
                            tile_pos = point_to_vector(pos)
                            add_tile(tile["spr"], tile_pos)

            def to_screen_vector(level_vector: Vector2) -> Vector2:
                return vector2_div(level_vector, level_size)

            char = level_struct["char"]
            jump = char["jump"]
            dash = char["dash"]
            ground = level_struct["tiles"]["grnd"]
            hazard = level_struct["tiles"]["hzrd"]
            finishes = level_struct["finishes"]
            static_items = level_struct["items"]["stc"]
            moving_items = level_struct["items"]["mov"]

            char_pos = to_screen_vector(point_to_vector(char["pos"]))
            char_size = to_screen_vector(point_to_vector(char["size"]))
            level.add_character(char["spr"], char_size, char_pos, jump["dist"] / level_size.x, jump["height"] / level_size.y, jump["time"], dash["dist"] / level_size.x, dash["time"])

            for finish in finishes:
                for pos in finish["pos"]:
                    finish_pos = to_screen_vector(point_to_vector(pos))
                    finish_size = to_screen_vector(point_to_vector(finish["size"]))
                    level.add_finish(finish["spr"], finish_size, finish_pos)

            build_tilemap(ground, level.add_ground_tile)

            build_tilemap(hazard, level.add_hazard_tile)

            for item in static_items:
                for pos in item["pos"]:
                    item_size = to_screen_vector(point_to_vector(item["size"]))
                    item_pos = to_screen_vector(point_to_vector(pos))
                    item_diff = character_diff(item["diff"][0], item["diff"][1], item["diff"][2], item["diff"][3])
                    level.add_static_item(item["spr"], item_size, item_pos, item_diff)

            for item in moving_items:
                for i in range(len(item["pos"])):
                    item_size = to_screen_vector(point_to_vector(item["size"]))
                    item_pos = to_screen_vector(point_to_vector(item["pos"][i]))
                    item_dest = to_screen_vector(point_to_vector(item["dest"][i]))
                    item_speed = (item_dest - item_pos).length() / item["time"]
                    item_diff = character_diff(item["diff"][0], item["diff"][1], item["diff"][2], item["diff"][3])
                    level.add_moving_item(item["spr"], item_size, item_pos, item_diff, item_speed, item_dest)

        valid_size_factor = has_keys("size_factor", level_struct, int)

        valid_tiles = has_keys("tilemap_size", level_struct, list) and validate_point(level_struct["tilemap_size"], True)

        valid_char = has_keys("char", level_struct, dict)
        if (valid_char):
            char = level_struct["char"]
            valid_sprite = has_sprite(char)
            valid_size = has_valid_size(char)
            valid_pos = has_valid_pos(char)
            valid_jump = has_keys("jump", char, dict) and has_keys(["height", "dist", "time", "temp", "def"], char["jump"], (int, float))
            valid_dash = has_keys("dash", char, dict) and has_keys(["dist", "time", "temp", "def"], char["dash"], (int, float))
            valid_char = valid_sprite and valid_size and valid_pos and valid_jump and valid_dash

        tiles = dict()
        if (has_keys("tiles", level_struct, dict)):
            tiles = level_struct["tiles"]
        valid_ground = has_keys("grnd", tiles, list) and validate_list(tiles["grnd"], 0, dict) and validate_tilemap(tiles["grnd"])
        valid_hazard = has_keys("hzrd", tiles, list) and validate_list(tiles["hzrd"], 0, dict) and validate_tilemap(tiles["hzrd"])

        valid_finishes = has_keys("finishes", level_struct, list) and validate_list(level_struct["finishes"], 0, dict)
        valid_finishes = valid_finishes and len(level_struct["finishes"]) > 0
        if (valid_finishes):
            for finish in level_struct["finishes"]:
                valid_spr = has_sprite(finish)
                valid_size = has_valid_size(finish)
                valid_pos = has_valid_poses(finish)
                valid_finishes = valid_spr and valid_size and valid_pos
                if (not valid_finishes):
                    break

        items = dict()
        if (has_keys("items", level_struct, dict)):
            items = level_struct["items"]

        valid_static_items = has_keys("stc", items, list) and validate_list(items["stc"], 0, dict)
        if (valid_static_items):
            for item in items["stc"]:
                valid_sprite = has_sprite(item)
                valid_size = has_valid_size(item)
                valid_diff = has_keys("diff", item, list) and validate_list(item["diff"], 4, int)
                valid_pos = has_valid_poses(item)
                valid_static_items = valid_sprite and valid_size and valid_diff and valid_pos
                if (not valid_static_items):
                    break

        valid_moving_items = has_keys("mov", items, list) and validate_list(items["mov"], 0, dict)
        if (valid_moving_items):
            for item in items["mov"]:
                valid_sprite = has_sprite(item)
                valid_size = has_valid_size(item)
                valid_diff = has_keys("diff", item, list) and validate_list(item["diff"], 4, int)
                valid_time = has_keys("time", item, (int, float))
                valid_pos = has_valid_poses(item)
                valid_dest = valid_pos and has_keys("dest", item, list) and len(item["dest"]) == len(item["pos"]) and validate_poses(item["dest"])
                valid_moving_items = valid_sprite and valid_diff and valid_pos and valid_time and valid_dest
                if (not valid_moving_items):
                    break

        valid_tilemaps = valid_tiles and valid_ground and valid_hazard
        valid_items = valid_static_items and valid_moving_items
        if (not (valid_size_factor and valid_char and valid_tilemaps and valid_finishes and valid_items)):
            raise RuntimeError("Not valid structure of a level")

        return generator

    def __build_level(self) -> None:
        for name in Level._DEF_TILEMAP_LAYERS:
            self.__TILEMAP.add_layer(name)
        self.__GENERATOR(self)

    def logic(self) -> None:
        for object in self.__OBJECTS:
            object.update()
        for i in range(GAME.fixed_steps()):
            for object in self.__OBJECTS:
                object.fixed_update()
        self.__collect_items()
        pass

    def add_ground_tile(self, sprite_path: str, tile_pos: Vector2) -> None:
        self.__TILEMAP.add_tile(sprite_path, "ground", tile_pos)

    def add_hazard_tile(self, sprite_path: str, tile_pos: Vector2) -> None:
        self.__TILEMAP.add_tile(sprite_path, "hazard", tile_pos)

    def add_character(self, sprite_path: str, size: Vector2, pos: Vector2, jump_dist: float, jump_height: float, jump_time: float, dash_dist: float, dash_time: float) -> None:
        from Objects import Character
        if (self.__PLAYER != None):
            raise RuntimeError("More than one character can't be spawned")
        self.__PLAYER = Character(sprite_path, size, pos, jump_dist, jump_height, jump_time, dash_dist, dash_time, self.__TILEMAP)
        self.__OBJECTS.append(self.__PLAYER)
        self.__SPRITES.add(self.__PLAYER)

    def add_finish(self, sprite_path: str, size: Vector2, pos: Vector2) -> None:
        from Objects import Finish
        finish = Finish(sprite_path, size, pos, self.__PLAYER)
        self.__OBJECTS.append(finish)
        self.__SPRITES.add(finish)

    def add_static_item(self, sprite_path: str, size: Vector2, pos: Vector2, diff: character_diff) -> None:
        from Objects import Collectable
        collectable = Collectable(sprite_path, size, pos, diff, self.__PLAYER)
        self.__OBJECTS.append(collectable)
        self.__COLLECTABLES.append(collectable)
        self.__SPRITES.add(collectable)

    def add_moving_item(self, sprite_path: str, size: Vector2, pos: Vector2, diff: character_diff, speed: float, destination: Vector2) -> None:
        from Objects import MovingCollectable
        collectable = MovingCollectable(sprite_path, size, pos, diff, speed, destination, self.__PLAYER)
        self.__OBJECTS.append(collectable)
        self.__COLLECTABLES.append(collectable)
        self.__SPRITES.add(collectable)

    def __collect_items(self) -> None:
        for object in self.__COLLECTABLES:
            if (object.is_collected):
                self.__OBJECTS.remove(object)
                self.__COLLECTABLES.remove(object)
                self.__SPRITES.remove(object)
