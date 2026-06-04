import pygame
from pygame import Vector2
from collections.abc import Callable
from Structs import character_diff
import json

class Game_manager:
    def __init__(self) -> None:
        self.__is_running: bool = False
        self.__FRAME: Frame = Frame()
        self.__UI = UI(self)
        self.__level: Level = None

    @property
    def FRAME(self) -> Frame:
        return self.__FRAME
    
    @property
    def UI(self) -> UI:
        return self.__UI

    @property
    def level(self) -> Level:
        return self.__level
    
    @property
    def is_running(self) -> bool:
        return self.__is_running
    
    def start(self, start_menu: UIScreen):
        self.UI.set_start_menu(start_menu)
        self.UI.open_start_menu()
        self.__is_running = True


    def start_level_from_file(self, level_path: str):
        level_file = open(level_path)
        level_structure = json.load(level_file)
        level_file.close()
        generator = Level.parse_level(level_structure)
        self.start_level(generator, level_structure["size"])
        
    def start_level(self, generator: Callable[[Game_manager], None], size_factor: int) -> None:
        self.__level = Level(generator, size_factor, self)
        self.level.build_level()
        self.UI.clear_ui()
        self.FRAME.RENDER_GROUPS.clear()
        self.FRAME.RENDER_GROUPS.append(self.level.SPRITES)
        self.FRAME.RENDER_GROUPS.append(self.level.GROUND.SPRITES)
        self.FRAME.RENDER_GROUPS.append(self.level.HAZARD.SPRITES)

    def close_level(self):
        self.__level = None
        self.FRAME.RENDER_GROUPS.clear()
        self.UI.open_start_menu()

    def reset_level(self) -> None:
        level = self.level
        self.start_level(level.GENERATOR, level.SIZE)

    def close_game(self) -> None:
        self.__is_running = False

class UI:
    from UI import UIScreen
    def __init__(self, game: Game_manager) -> None:
        from UI import UIScreen
        self.__start_menu: UIScreen = None
        self.__ui: UIScreen = None
        self.__GAME: Game_manager = game

    @property
    def start_menu(self) -> UIScreen:
        return self.__start_menu
    
    @property
    def ui(self) -> UIScreen:
        return self.__ui
    
    @property
    def GAME(self) -> Game_manager:
        return self.__GAME
    
    def set_start_menu(self, start_menu: UIScreen) -> None:
        self.__start_menu = start_menu

    def open_start_menu(self):
        self.switch_ui(self.start_menu)

    def switch_ui(self, ui: UIScreen) -> None:
        self.clear_ui()
        self.__ui = ui
        self.GAME.FRAME.RENDER_GROUPS.append(self.ui.SPRITES)

    def clear_ui(self):
        try:
            self.GAME.FRAME.RENDER_GROUPS.remove(self.ui.SPRITES)
        except:
            pass
        finally:
            self.__ui = None

class Frame:
    def __init__(self) -> None:
        self.__SCREEN: pygame.Surface = pygame.display.set_mode()
        self.__CLOCK: pygame.Clock = pygame.time.Clock()
        self.__RENDER_GROUPS: list[pygame.sprite.Group] = []
        self.__delta_time: float = 0

    @property
    def SCREEN(self) -> pygame.Surface:
        return self.__SCREEN
    
    @property
    def CLOCK(self) -> pygame.time.Clock:
        return self.__CLOCK
    
    @property
    def RENDER_GROUPS(self) -> list[pygame.sprite.Group]:
        return self.__RENDER_GROUPS
    
    @property
    def delta_time(self) -> float:
        return self.__delta_time
    
    def next(self) -> None:
        self.__delta_time = self.CLOCK.tick() / 1000

    def render(self) -> None:
        self.SCREEN.fill("#333333")
        for render_group in self.RENDER_GROUPS:
            render_group.draw(self.SCREEN)
        pygame.display.flip()

class Level:
    from Objects import Tilemap, Character, Static_collectable
    def __init__(self, generator: Callable[[Game_manager], None], size_factor: int, game: Game_manager) -> None:
        from Objects import Tilemap, Character, Static_collectable

        self.__GAME: Game_manager = game
        self.__SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.__GENERATOR: Callable[[Game_manager], None] = generator
        self.__SIZE: int = size_factor
        self.__TILE_SIZE: int = self.GAME.FRAME.SCREEN.get_width() / (16 * self.SIZE)
        self.__GROUND: Tilemap = None
        self.__HAZARD: Tilemap = None
        self.__COLLECTABLES: list[type[Static_collectable]] = []
        self.__PLAYER: Character = None

    @property
    def GAME(self) -> Game_manager:
        return self.__GAME
    
    @property
    def SPRITES(self) -> pygame.sprite.Group:
        return self.__SPRITES
    
    @property
    def GENERATOR(self) -> Callable[[Game_manager], None]:
        return self.__GENERATOR
    
    @property
    def SIZE(self) -> int:
        return self.__SIZE
    
    @property
    def TILE_SIZE(self) -> int:
        return self.__TILE_SIZE
    
    @property
    def GROUND(self) -> Tilemap:
        if(self.__GROUND == None):
            raise RuntimeError("Ground is inaccessible. The level was not built.")
        return self.__GROUND
    
    @property
    def HAZARD(self) -> Tilemap:
        if(self.__GROUND == None):
            raise RuntimeError("Hazard is inaccessible. The level was not built.")
        return self.__HAZARD
    
    @property
    def PLAYER(self) -> Character:
        if(self.__PLAYER == None):
            raise RuntimeError("Player is inaccessible. Character was not added.")
        return self.__PLAYER
    
    @property
    def COLLECTABLES(self) -> list[type[Static_collectable]]:
        return self.__COLLECTABLES
    
    @staticmethod
    def parse_level(level_structure: str) -> Callable[[Game_manager], None]:
        def generator(game: Game_manager):
            level = game.level
            character = level_structure["char"]
            ground = level_structure["grnd"]
            hazard = level_structure["hzrd"]
            static_collectables = level_structure["stc_coll"]
            dynamic_collectables = level_structure["dnm_coll"]
            level.add_character(character["spr"], Vector2(character["pos"][0], character["pos"][1]), character["speed"])
            for tile in ground:
                for pos in tile["pos"]:
                    level.add_ground_tile(tile["spr"], (pos[0], pos[1]))
            for tile in hazard:
                for pos in tile["pos"]:
                    level.add_hazard_tile(tile["spr"], (pos[0], pos[1]))
            for tile in static_collectables:
                for pos in tile["pos"]:
                    diff = character_diff(tile["diff"][0], tile["diff"][1], tile["diff"][2], tile["diff"][3])
                    level.add_static_collectable(tile["spr"], Vector2(pos[0], pos[1]), diff)
            for tile in dynamic_collectables:
                for i in range(len(tile["pos"])):
                    pos = tile["pos"][i]
                    dest = tile["dest"][i]
                    diff = character_diff(tile["diff"][0], tile["diff"][1], tile["diff"][2], tile["diff"][3])
                    level.add_dynamic_collectable(tile["spr"], Vector2(pos[0], pos[1]), diff, tile["speed"], Vector2(dest[0], dest[1]))
        
        return generator

    def build_level(self) -> None:
        from Objects import Tilemap
        if(self.__GROUND != None):
            raise RuntimeError("The level was already built.")
        self.__GROUND = Tilemap(self.GAME)
        self.__HAZARD = Tilemap(self.GAME)
        self.GENERATOR(self.GAME)

    def logic(self) -> None: #behaviour of a level
        self.PLAYER.behaviour()
        for collectable in self.COLLECTABLES:
            collectable.behaviour()
            if(collectable.is_collected):
                self.SPRITES.remove(collectable)
                self.COLLECTABLES.remove(collectable)
        hazard_contacts = pygame.sprite.spritecollide(self.PLAYER, self.HAZARD.SPRITES, False)
        if(len(hazard_contacts) > 0):
            self.GAME.reset_level()

    def add_ground_tile(self, sprite_path: str, tile_pos: tuple[int, int]) -> None:
        self.GROUND.addTile(sprite_path, tile_pos)
        
    def add_hazard_tile(self, sprite_path: str, tile_pos: tuple[int, int]) -> None:
        self.HAZARD.addTile(sprite_path, tile_pos)

    def add_character(self, sprite_path: str, pos: Vector2[float, float], speed: float) -> None:
        from Objects import Character
        if(self.__PLAYER != None):
            raise RuntimeError("More than one character can't be spawned")
        self.__PLAYER = Character(sprite_path, pos, speed, self.GAME)
        self.SPRITES.add(self.PLAYER)

    def add_static_collectable(self, sprite_path: str, pos: Vector2[float, float], diff: character_diff) -> None:
        from Objects import Static_collectable
        collectable = Static_collectable(sprite_path, pos, diff, self.GAME)
        self.COLLECTABLES.append(collectable)
        self.SPRITES.add(collectable)

    def add_dynamic_collectable(self, sprite_path: str, pos: Vector2[float, float], diff: character_diff, speed: float, destination: Vector2[float, float]) -> None:
        from Objects import Dynamic_collectable
        collectable = Dynamic_collectable(sprite_path, pos, diff, speed, destination, self.GAME)
        self.COLLECTABLES.append(collectable)
        self.SPRITES.add(collectable)