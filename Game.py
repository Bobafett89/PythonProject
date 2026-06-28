import pygame
from pygame import Vector2
from Utils import character_diff, level_pos, Control, Command
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
                    self._start_level(generator, level_structure["size"])
            
    def _start_level(self, generator: Callable[[Game_manager], None], size_factor: int) -> None:
        self.level = Level(generator, size_factor, self)
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
        self._start_level(level.GENERATOR, level.SIZE)

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
        self.SCREEN: pygame.Surface = pygame.display.set_mode()
        self.CLOCK: pygame.Clock = pygame.time.Clock()
        self.RENDER_GROUPS: list[pygame.sprite.Group] = []
        self.delta_time: float = 0
        self.FIXED_DELTA_TIME: float = 0.03

    def next(self) -> None:
        self.delta_time = self.CLOCK.tick(1000) / 1000

    def render(self) -> None:
        self.SCREEN.fill("#333333")
        for render_group in self.RENDER_GROUPS:
            render_group.draw(self.SCREEN)
        pygame.display.flip()

class Level:
    from Objects import Tilemap, Character, Collectable, Finish
    from BasicObjects import LevelObject
    def __init__(self, generator: Callable[[Game_manager], None], size_factor: int, game: Game_manager) -> None:
        from Objects import Tilemap, Character
        from BasicObjects import LevelObject
        self.GAME: Game_manager = game
        self.SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.GENERATOR: Callable[[Game_manager], None] = generator
        self.SIZE: int = size_factor
        self.TILE_SIZE: int = self.GAME.FRAME.SCREEN.width / (16 * self.SIZE)
        self.GROUND: Tilemap = None
        self.HAZARD: Tilemap = None
        self.OBJECTS: list[type[LevelObject]] = []
        self.COLLECTED: list[type[LevelObject]] = []
        self.PLAYER: Character = None

    @staticmethod
    def parse_level(level_struct: dict) -> Callable[[Game_manager], None]:
        def has_keys(keys: list[str], where: dict, type: type) -> bool:
            has = True
            for key in keys:
                if(key not in where or not isinstance(where[key], type)):
                    has = False
                    break
            return has
        
        def validate_poses(poses: list, is_int: bool, include_lines: bool) -> bool:
            valid = validate_list(poses, 0, list)
            pos_type = None
            if(is_int):
                pos_type = int
            else:
                pos_type = (int, float)
            if(valid):
                for pos in poses:
                    valid_point = validate_list(pos, 2, pos_type)
                    valid_line = include_lines and validate_list(pos, 2, list) and validate_list(pos[0], 2, pos_type) and validate_list(pos[1], 2, pos_type)
                    if(not (valid_point or valid_line)):
                        valid = False
                        break
            return valid
            
        def validate_list(arr: list, size: int, type: type) -> bool:
            valid = False
            if(len(arr) == size or size == 0):
                valid = True
                for element in arr:
                    if(not isinstance(element, type)):
                        valid = False
                        break
            return valid
        
        def validate_tilemap(tilemap: list) -> bool:
            valid_tilemap = True
            for tile in tilemap:
                valid_sprite = has_keys(["spr"], tile, str)
                valid_pos = has_keys(["pos"], tile, list) and validate_poses(tile["pos"], True, True)
                if(not (valid_sprite and valid_pos)):
                    valid_tilemap = False
                    break
            return valid_tilemap

        def generator(game: Game_manager) -> None:
            level = game.level
            character = level_struct["char"]
            jump = character["jump"]
            dash = character["dash"]
            ground = level_struct["grnd"]
            hazard = level_struct["hzrd"]
            finish = level_struct["finish"]
            static_collectables = level_struct["stc_coll"]
            dynamic_collectables = level_struct["dnm_coll"]

            level.add_character(character["spr"], Vector2(character["pos"][0], character["pos"][1]), jump["dist"], jump["height"], jump["time"], dash["dist"], dash["time"])

            level.add_finish(finish["spr"], Vector2(finish["pos"][0], finish["pos"][1]))

            for tile in ground:
                for pos in tile["pos"]:
                    if(isinstance(pos[0], list)):
                        start = pos[0]
                        end = pos[1]
                        if(pos[0][0] == pos[1][0]):
                            dir = start[1] <= end[1] * 2 - 1
                            for i in range(start[1], end[1] + dir, dir):
                                level.add_ground_tile(tile["spr"], Vector2(start[0], i))
                        else:
                            dir = start[0] <= end[0] * 2 - 1
                            for i in range(start[0], end[0] + dir, dir):
                                level.add_ground_tile(tile["spr"], Vector2(i, start[1]))
                    else:
                        level.add_ground_tile(tile["spr"], Vector2(pos[0], pos[1]))

            for tile in hazard:
                for pos in tile["pos"]:
                    if(isinstance(pos[0], list)):
                        start = pos[0]
                        end = pos[1]
                        if(pos[0][0] == pos[1][0]):
                            dir = start[1] <= end[1] * 2 - 1
                            for i in range(start[1], end[1] + dir, dir):
                                level.add_hazard_tile(tile["spr"], Vector2(start[0], i))
                        else:
                            dir = start[0] <= end[0] * 2 - 1
                            for i in range(start[0], end[0] + dir, dir):
                                level.add_hazard_tile(tile["spr"], Vector2(i, start[1]))
                    else:
                        level.add_hazard_tile(tile["spr"], Vector2(pos[0], pos[1]))

            for item in static_collectables:
                for pos in item["pos"]:
                    diff = character_diff(item["diff"][0], item["diff"][1], item["diff"][2], item["diff"][3])
                    level.add_static_collectable(item["spr"], Vector2(pos[0], pos[1]), diff)

            for item in dynamic_collectables:
                for i in range(len(item["pos"])):
                    pos = item["pos"][i]
                    dest = item["dest"][i]
                    diff = character_diff(item["diff"][0], item["diff"][1], item["diff"][2], item["diff"][3])
                    level.add_dynamic_collectable(item["spr"], Vector2(pos[0], pos[1]), diff, item["speed"], Vector2(dest[0], dest[1]))
        
        valid_size = has_keys(["size"], level_struct, int)

        valid_char = has_keys(["char"], level_struct, dict)
        if(valid_char):
            char = level_struct["char"]
            valid_sprite = has_keys(["spr"], char, str)
            valid_pos = has_keys(["pos"], char, list) and validate_list(char["pos"], 2, (int, float))
            valid_jump = has_keys(["jump"], char, dict) and has_keys(["height", "dist", "time"], char["jump"], (int, float))
            valid_dash = has_keys(["dash"], char, dict) and has_keys(["dist", "time"], char["dash"], (int, float))
            valid_char = valid_sprite and valid_pos and valid_jump and valid_dash

        valid_ground = has_keys(["grnd"], level_struct, list) and validate_tilemap(level_struct["grnd"])

        valid_hazard = has_keys(["hzrd"], level_struct, list) and validate_tilemap(level_struct["hzrd"])

        valid_finish = has_keys(["finish"], level_struct, dict)
        if(valid_finish):
            valid_spr = has_keys(["spr"], level_struct["finish"], str)
            valid_pos = has_keys(["pos"], level_struct["finish"], list) and validate_list(level_struct["finish"]["pos"], 2, (int, float))
            valid_finish = valid_spr and valid_pos

        valid_items = has_keys(["stc_coll"], level_struct, list) and has_keys(["dnm_coll"], level_struct, list)
        if(valid_items):
            for item in level_struct["stc_coll"]:
                valid_sprite = has_keys(["spr"], item, str)
                valid_diff = has_keys(["diff"], item, list) and validate_list(item["diff"], 4, int)
                valid_pos = has_keys(["pos"], item, list) and validate_poses(item["pos"], False, False)
                if(not (valid_sprite and valid_diff and valid_pos)):
                    valid_items = False
                    break
            for item in level_struct["dnm_coll"]:
                valid_sprite = has_keys(["spr"], item, str)
                valid_diff = has_keys(["diff"], item, list) and validate_list(item["diff"], 4, int)
                valid_speed = has_keys(["speed"], item, (int, float))
                valid_pos = has_keys(["pos"], item, list) and validate_poses(item["pos"], False, False)
                valid_dest = valid_pos and has_keys(["dest"], item, list) and len(item["dest"]) == len(item["pos"]) and validate_poses(item["dest"], False, False)
                if(not (valid_sprite and valid_diff and valid_pos and valid_speed and valid_dest)):
                    valid_items = False
                    break

        if(not (valid_size and valid_char and valid_ground and valid_hazard and valid_finish and valid_items)):
            raise RuntimeError("Not valid structure of a level")

        return generator

    def build_level(self) -> None:
        from Objects import Tilemap
        if(self.GROUND != None):
            raise RuntimeError("The level was already built.")
        self.GROUND = Tilemap(self.GAME)
        self.HAZARD = Tilemap(self.GAME)
        self.GENERATOR(self.GAME)

    def logic(self) -> None:
        for object in self.OBJECTS:
            object.behaviour()
        delta_time = self.GAME.FRAME.delta_time
        fixed_delta_time = self.GAME.FRAME.FIXED_DELTA_TIME
        while delta_time > 0:
            current_delta = 0
            if(delta_time > fixed_delta_time):
                current_delta = fixed_delta_time
            else:
                current_delta = delta_time
            delta_time -= current_delta
            for object in self.OBJECTS:
                object.fixed_step_behaviour(current_delta)
        self.remove_collected_objects()

    def add_ground_tile(self, sprite_path: str, tile_pos: Vector2) -> None:
        self.GROUND.addTile(sprite_path, tile_pos)
        
    def add_hazard_tile(self, sprite_path: str, tile_pos: Vector2) -> None:
        self.HAZARD.addTile(sprite_path, tile_pos)

    def add_character(self, sprite_path: str, pos: Vector2, jump_dist: float, jump_height: float, jump_time: float, dash_dist: float, dash_time: float) -> None:
        from Objects import Character
        if(self.PLAYER != None):
            raise RuntimeError("More than one character can't be spawned")
        self.PLAYER = Character(sprite_path, level_pos.from_vector2(pos), jump_dist, jump_height, jump_time, dash_dist, dash_time, self.GAME)
        self.OBJECTS.append(self.PLAYER)
        self.SPRITES.add(self.PLAYER)

    def add_finish(self, sprite_path: str, pos: Vector2) -> None:
        from Objects import Finish
        finish = Finish(sprite_path, level_pos.from_vector2(pos), self.GAME)
        self.OBJECTS.append(finish)
        self.SPRITES.add(finish)

    def add_static_collectable(self, sprite_path: str, pos: Vector2, diff: character_diff) -> None:
        from Objects import Collectable
        collectable = Collectable(sprite_path, level_pos.from_vector2(pos), diff, self.GAME)
        self.OBJECTS.append(collectable)
        self.SPRITES.add(collectable)

    def add_dynamic_collectable(self, sprite_path: str, pos: Vector2, diff: character_diff, speed: float, destination: Vector2) -> None:
        from Objects import MovingCollectable
        collectable = MovingCollectable(sprite_path, level_pos.from_vector2(pos), diff, speed, level_pos.from_vector2(destination), self.GAME)
        self.OBJECTS.append(collectable)
        self.SPRITES.add(collectable)

    def collect_object(self, object: type[LevelObject]) -> None:
        if(not object in self.COLLECTED):
            self.COLLECTED.append(object)

    def remove_collected_objects(self) -> None:
        for object in self.COLLECTED:
            self.OBJECTS.remove(object)
            self.SPRITES.remove(object)
        self.COLLECTED.clear()