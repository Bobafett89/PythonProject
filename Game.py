import pygame
from pygame import Vector2
from Utils import character_diff, Control, Command, tilemap_info, vector2_div, vector2_mult
from os import path
from json import loads, decoder
from collections.abc import Callable

class Game_manager:
    def __init__(self) -> None:
        self.is_running: bool = False
        self.FRAME: Frame = Frame()
        self.UI = UI(self)
        self.level: Level = None
        self.control: Control = Control.wait()

    def start(self, start_menu: UIScreen) -> None:
        self.UI.set_start_menu(start_menu)
        self.UI.open_start_menu()
        self.is_running = True

    def set_command(self, command: Control) -> None:
        if(command.command.value > self.control.command.value):
            self.control = command

    def execute_command(self):
        match self.control.command:
            case Command.WAIT:
                pass
            case Command.SWITCH_UI:
                self.UI.switch_ui(self.control.parameter)
            case Command.OPEN_LEVEL:
                try:
                    self._start_level_from_file(self.control.parameter)
                except RuntimeError:
                    pass
            case Command.RESTART_LEVEL:
                self._reset_level()
            case Command.CLOSE_LEVEL:
                self._close_level()
            case Command.CLOSE_GAME:
                self._close_game()
        self.control = Control.wait()

    def _start_level_from_file(self, level_name: str) -> None:
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
                    self._start_level(generator, level_structure["size_factor"], Vector2(level_structure["tiles"]))
            
    def _start_level(self, generator: Callable[[Game_manager], None], size_factor: int, tilemap_size: Vector2) -> None:
        self.level = Level(generator, size_factor, tilemap_size, self)
        self.level.build_level()
        self.UI.clear_ui()
        self.FRAME.RENDER_GROUPS.clear()
        self.FRAME.RENDER_GROUPS.append(self.level.SPRITES)
        self.FRAME.RENDER_GROUPS.append(self.level.GROUND.SPRITES)
        self.FRAME.RENDER_GROUPS.append(self.level.HAZARD.SPRITES)

    def _close_level(self) -> None:
        self.level = None
        self.FRAME.RENDER_GROUPS.clear()
        self.UI.open_start_menu()

    def _reset_level(self) -> None:
        level = self.level
        self._start_level(level.GENERATOR, level.SIZE_FACTOR, level.TILEMAP.size)

    def _close_game(self) -> None:
        self.is_running = False

class UI:
    from UI import UI_Screen
    def __init__(self, game: Game_manager) -> None:
        from UI import UI_Screen
        self.start_menu: UI_Screen = None
        self.current_screen: UI_Screen = None
        self.GAME: Game_manager = game

    def set_start_menu(self, start_menu: UI_Screen) -> None:
        self.start_menu = start_menu

    def open_start_menu(self) -> None:
        self.switch_ui(self.start_menu)

    def switch_ui(self, screen: UI_Screen) -> None:
        self.clear_ui()
        self.current_screen = screen
        self.GAME.FRAME.RENDER_GROUPS.append(self.current_screen.SPRITES)

    def clear_ui(self) -> None:
        if(self.current_screen != None and self.current_screen.SPRITES in self.GAME.FRAME.RENDER_GROUPS):
            self.GAME.FRAME.RENDER_GROUPS.remove(self.current_screen.SPRITES)
        self.current_screen = None

    def press_buttons(self) -> None:
        self.current_screen.press_buttons()

class Frame:
    def __init__(self) -> None:
        screen_flags = pygame.FULLSCREEN | pygame.SCALED
        self.SCREEN: pygame.Surface = pygame.display.set_mode((1536, 864), screen_flags)
        self.CLOCK: pygame.Clock = pygame.time.Clock()
        self.RENDER_GROUPS: list[pygame.sprite.Group] = []
        self.delta_time: float = 0
        self.FIXED_DELTA_TIME: float = 0.02

    def next(self) -> None:
        self.delta_time = self.CLOCK.tick(1000) / 1000

    def render(self) -> None:
        self.SCREEN.fill("#333333")
        for render_group in self.RENDER_GROUPS:
            render_group.draw(self.SCREEN)
        pygame.display.flip()

class Level:
    from Objects import TilemapLayer, Character, Collectable, Finish
    from BasicObjects import BasicSprite
    def __init__(self, generator: Callable[[Game_manager], None], size_factor: float, tilemap_size: Vector2, game: Game_manager) -> None:
        from Objects import TilemapLayer, Character
        from BasicObjects import BasicSprite
        self.GAME: Game_manager = game
        self.SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.GENERATOR: Callable[[Game_manager], None] = generator
        self.SIZE_FACTOR: float = size_factor
        self.UNITS: Vector2 = Vector2(16, 9) * self.SIZE_FACTOR
        self.UNIT_PIXEL_SIZE: float = self.GAME.FRAME.SCREEN.width / self.UNITS.x
        self.TILEMAP: tilemap_info = tilemap_info(tilemap_size, vector2_div(Vector2(1, 1), tilemap_size))
        self.GROUND: TilemapLayer = None
        self.HAZARD: TilemapLayer = None
        self.OBJECTS: list[type[BasicSprite]] = []
        self.COLLECTED: list[type[BasicSprite]] = []
        self.PLAYER: Character = None
        self.acc_delta_time: float = 0

    @staticmethod
    def parse_level(level_struct: dict) -> Callable[[Game_manager], None]:
        def has_keys(keys: list[str] | str, where: dict, type: type | tuple[type, ...]) -> bool:
            has: bool = None
            if(isinstance(keys, str)):
                has = keys in where and isinstance(where[keys], type)
            else:
                has = True
                for key in keys:
                    if(not (key in where and isinstance(where[key], type))):
                        has = False
                        break
            return has
            
        def has_sprite(where: dict):
            return has_keys("spr", where, str)

        def validate_list(arr: list, size: int, type: type) -> bool:
            valid = False
            if(len(arr) == size or size == 0):
                valid = True
                for element in arr:
                    if(not isinstance(element, type)):
                        valid = False
                        break
            return valid

        def validate_point(pos: list, is_int: bool = False) -> bool:
            pos_type: type | tuple[type, ...] = None
            if(is_int):
                pos_type = int
            else:
                pos_type = (int, float)
            return validate_list(pos, 2, pos_type)

        def validate_poses(poses: list, is_int: bool = False, include_lines: bool = False) -> bool:
            valid = validate_list(poses, 0, list)
            if(valid):
                for pos in poses:
                    valid_point = validate_point(pos, is_int)
                    valid_line = include_lines and validate_list(pos, 2, list) and validate_point(pos[0], is_int) and validate_point(pos[1], is_int)
                    if(not (valid_point or valid_line)):
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
                if(not valid_tilemap):
                    break
            return valid_tilemap

        def generator(game: Game_manager) -> None:
            def point_to_vector(point: list[float | int]):
                return Vector2(point[0], point[1])
            
            def build_tilemap(tilemap: list[dict], add_tile: Callable[[str, Vector2], None]):
                for tile in tilemap:
                    for pos in tile["pos"]:
                        if(isinstance(pos[0], list)):
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

            level = game.level
            char = level_struct["char"]
            jump = char["jump"]
            dash = char["dash"]
            ground = level_struct["grnd"]
            hazard = level_struct["hzrd"]
            finishes = level_struct["finishes"]
            static_items = level_struct["coll"]
            moving_items = level_struct["mov_coll"]

            char_pos = point_to_vector(char["pos"])
            char_size = point_to_vector(char["size"])
            level.add_character(char["spr"], char_size, char_pos, jump["dist"], jump["height"], jump["time"], dash["dist"], dash["time"])

            for finish in finishes:
                for pos in finish["pos"]:
                    finish_pos = point_to_vector(pos)
                    finish_size = point_to_vector(finish["size"])
                    level.add_finish(finish["spr"], finish_size, finish_pos)

            build_tilemap(ground, level.add_ground_tile)

            build_tilemap(hazard, level.add_hazard_tile)

            for item in static_items:
                for pos in item["pos"]:
                    item_size = point_to_vector(item["size"])
                    item_pos = point_to_vector(pos)
                    item_diff = character_diff(item["diff"][0], item["diff"][1], item["diff"][2], item["diff"][3])
                    level.add_static_item(item["spr"], item_size, item_pos, item_diff)

            for item in moving_items:
                for i in range(len(item["pos"])):
                    item_size = point_to_vector(item["size"])
                    item_pos = point_to_vector(item["pos"][i])
                    item_dest = point_to_vector(item["dest"][i])
                    item_diff = character_diff(item["diff"][0], item["diff"][1], item["diff"][2], item["diff"][3])
                    level.add_moving_item(item["spr"], item_size, item_pos, item_diff, item["speed"], item_dest)
        
        valid_size_factor = has_keys("size_factor", level_struct, int)

        valid_tiles = has_keys("tiles", level_struct, list) and validate_point(level_struct["tiles"], True)

        valid_char = has_keys(["char"], level_struct, dict)
        if(valid_char):
            char = level_struct["char"]
            valid_sprite = has_sprite(char)
            valid_size = has_valid_size(char)
            valid_pos = has_valid_pos(char)
            valid_jump = has_keys("jump", char, dict) and has_keys(["height", "dist", "time", "temp", "def"], char["jump"], (int, float))
            valid_dash = has_keys("dash", char, dict) and has_keys(["dist", "time", "temp", "def"], char["dash"], (int, float))
            valid_char = valid_sprite and valid_size and valid_pos and valid_jump and valid_dash

        valid_ground = has_keys(["grnd"], level_struct, list) and validate_list(level_struct["grnd"], 0, dict) and validate_tilemap(level_struct["grnd"])

        valid_hazard = has_keys(["hzrd"], level_struct, list) and validate_list(level_struct["hzrd"], 0, dict) and validate_tilemap(level_struct["hzrd"])

        valid_finishes = has_keys("finishes", level_struct, list) and validate_list(level_struct["finishes"], 0, dict)
        valid_finishes = valid_finishes and len(level_struct["finishes"]) > 0
        if(valid_finishes):
            for finish in level_struct["finishes"]:
                valid_spr = has_sprite(finish)
                valid_size = has_valid_size(finish)
                valid_pos = has_valid_poses(finish)
                valid_finishes = valid_spr and valid_size and valid_pos
                if(not valid_finishes):
                    break

        valid_static_items = has_keys("coll", level_struct, list) and validate_list(level_struct["coll"], 0, dict)
        if(valid_static_items):
            for item in level_struct["coll"]:
                valid_sprite = has_sprite(item)
                valid_size = has_valid_size(item)
                valid_diff = has_keys("diff", item, list) and validate_list(item["diff"], 4, int)
                valid_pos = has_valid_poses(item)
                valid_static_items = valid_sprite and valid_size and valid_diff and valid_pos
                if(not valid_static_items):
                    break

        valid_moving_items = has_keys("mov_coll", level_struct, list) and validate_list(level_struct["mov_coll"], 0, dict)
        if(valid_moving_items):
            for item in level_struct["mov_coll"]:
                valid_sprite = has_sprite(item)
                valid_size = has_valid_size(item)
                valid_diff = has_keys("diff", item, list) and validate_list(item["diff"], 4, int)
                valid_speed = has_keys("speed", item, (int, float))
                valid_pos = has_valid_poses(item)
                valid_dest = valid_pos and has_keys("dest", item, list) and len(item["dest"]) == len(item["pos"]) and validate_poses(item["dest"])
                valid_moving_items = valid_sprite and valid_diff and valid_pos and valid_speed and valid_dest
                if(not valid_moving_items):
                    break
        
        valid_tilemaps = valid_tiles and valid_ground and valid_hazard
        valid_items = valid_static_items and valid_moving_items
        if(not (valid_size_factor and valid_char and valid_tilemaps and valid_finishes and valid_items)):
            raise RuntimeError("Not valid structure of a level")

        return generator

    def convert_tilemap_vector(self, vector: Vector2, to_tilemap: bool = False) -> Vector2:
        new_vector = Vector2(0, 0)
        if(to_tilemap):
            new_vector = vector2_mult(vector, self.TILEMAP.size)
        else:
            new_vector = vector2_div(vector, self.TILEMAP.size)
        return new_vector

    def convert_unit_vector(self, vector: Vector2, to_unit: bool = False) -> Vector2:
        new_vector = Vector2(0, 0)
        if(to_unit):
            new_vector = vector2_mult(vector, self.UNITS)
        else:
            new_vector = vector2_div(vector, self.UNITS)
        return new_vector

    def build_level(self) -> None:
        from Objects import TilemapLayer
        if(self.GROUND != None):
            raise RuntimeError("The level was already built.")
        self.GROUND = TilemapLayer(self.GAME)
        self.HAZARD = TilemapLayer(self.GAME)
        self.GENERATOR(self.GAME)

    def logic(self) -> None:
        for object in self.OBJECTS:
            object.behaviour()
        self.acc_delta_time += self.GAME.FRAME.delta_time
        fixed_delta = self.GAME.FRAME.FIXED_DELTA_TIME
        while self.acc_delta_time > fixed_delta:
            self.acc_delta_time -= fixed_delta
            for object in self.OBJECTS:
                object.fixed_step_behaviour()
        self.remove_collected_objects()
        pass

    def add_ground_tile(self, sprite_path: str, tile_pos: Vector2) -> None:
        self.GROUND.addTile(sprite_path, tile_pos)
        
    def add_hazard_tile(self, sprite_path: str, tile_pos: Vector2) -> None:
        self.HAZARD.addTile(sprite_path, tile_pos)

    def add_character(self, sprite_path: str, size: Vector2, pos: Vector2, jump_dist: float, jump_height: float, jump_time: float, dash_dist: float, dash_time: float) -> None:
        from Objects import Character
        if(self.PLAYER != None):
            raise RuntimeError("More than one character can't be spawned")
        self.PLAYER = Character(sprite_path, size, pos, jump_dist, jump_height, jump_time, dash_dist, dash_time, self.GAME)
        self.OBJECTS.append(self.PLAYER)
        self.SPRITES.add(self.PLAYER)

    def add_finish(self, sprite_path: str, size: Vector2, pos: Vector2) -> None:
        from Objects import Finish
        finish = Finish(sprite_path, size, pos, self.GAME)
        self.OBJECTS.append(finish)
        self.SPRITES.add(finish)

    def add_static_item(self, sprite_path: str, size: Vector2, pos: Vector2, diff: character_diff) -> None:
        from Objects import Collectable
        collectable = Collectable(sprite_path, size, pos, diff, self.GAME)
        self.OBJECTS.append(collectable)
        self.SPRITES.add(collectable)

    def add_moving_item(self, sprite_path: str, size: Vector2, pos: Vector2, diff: character_diff, speed: float, destination: Vector2) -> None:
        from Objects import MovingCollectable
        collectable = MovingCollectable(sprite_path, size, pos, diff, speed, destination, self.GAME)
        self.OBJECTS.append(collectable)
        self.SPRITES.add(collectable)

    def collect_object(self, object: type[BasicSprite]) -> None:
        if(not object in self.COLLECTED):
            self.COLLECTED.append(object)

    def remove_collected_objects(self) -> None:
        for object in self.COLLECTED:
            self.OBJECTS.remove(object)
            self.SPRITES.remove(object)
        self.COLLECTED.clear()