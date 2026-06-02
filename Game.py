import pygame
from pygame import Vector2
from collections.abc import Callable

class Game_manager:
    def __init__(self) -> None:
        self.__FRAME: Frame = Frame()
        self.__is_running: bool = True
        self.__level: Level = None

    @property
    def FRAME(self) -> Frame:
        return self.__FRAME
    
    @property
    def level(self) -> Level:
        if(self.__level == None):
            raise TypeError("Level was not initialized")
        return self.__level
    
    @property
    def is_running(self) -> bool:
        return self.__is_running

    def start_level(self, generator: Callable[[Game_manager], None], size_factor: int) -> None:
        self.__level = Level(generator, size_factor, self)
        self.level.build_level()
        self.FRAME.RENDER_GROUPS.clear()
        self.FRAME.RENDER_GROUPS.append(self.level.SPRITES)
        self.FRAME.RENDER_GROUPS.append(self.level.GROUND.SPRITES)
        self.FRAME.RENDER_GROUPS.append(self.level.HAZARD.SPRITES)

    def reset_level(self) -> None:
        level = self.level
        self.start_level(level.GENERATOR, level.SIZE)

    def close_game(self) -> None:
        self.__is_running = False

class Frame:
    def __init__(self):
        self.__SCREEN: pygame.Surface = pygame.display.set_mode()
        self.__CLOCK: pygame.Clock = pygame.time.Clock()
        self.__RENDER_GROUPS: list[pygame.sprite.Group] = []
        self.__delta_time = 0

    @property
    def SCREEN(self):
        return self.__SCREEN
    
    @property
    def CLOCK(self):
        return self.__CLOCK
    
    @property
    def RENDER_GROUPS(self):
        return self.__RENDER_GROUPS
    
    @property
    def delta_time(self):
        return self.__delta_time
    
    def next(self):
        self.__delta_time = self.CLOCK.tick(120) / 1000

    def render(self):
        self.SCREEN.fill("black")
        for i in range(len(self.RENDER_GROUPS)):
            self.RENDER_GROUPS[i].draw(self.SCREEN)
        pygame.display.flip()

class Level:
    def __init__(self, generator: Callable[[Game_manager], None], size_factor: int, game: Game_manager) -> None:
        from Objects import Tilemap, Character

        self.__GAME = game
        self.__SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.__GENERATOR: Callable[[Game_manager], None] = generator
        self.__SIZE: int = size_factor
        self.__TILE_SIZE: int = self.GAME.FRAME.SCREEN.get_width() / (16 * self.SIZE)
        self.__GROUND: Tilemap = None
        self.__HAZARD: Tilemap = None
        self.__PLAYER: Character = None

    @property
    def GAME(self):
        return self.__GAME
    
    @property
    def SPRITES(self):
        return self.__SPRITES
    
    @property
    def GENERATOR(self):
        return self.__GENERATOR
    
    @property
    def SIZE(self):
        return self.__SIZE
    
    @property
    def TILE_SIZE(self):
        return self.__TILE_SIZE
    
    @property
    def GROUND(self):
        if(self.__GROUND == None):
            raise RuntimeError("Ground is inaccessible. The level was not built.")
        return self.__GROUND
    
    @property
    def HAZARD(self):
        if(self.__GROUND == None):
            raise RuntimeError("Hazard is inaccessible. The level was not built.")
        return self.__HAZARD
    
    @property
    def PLAYER(self):
        if(self.__PLAYER == None):
            raise RuntimeError("Player is inaccessible. Character was not added.")
        return self.__PLAYER
    
    def build_level(self):
        from Objects import Tilemap
        if(self.__GROUND != None):
            raise RuntimeError("The level was already built.")
        self.__GROUND = Tilemap(self.GAME)
        self.__HAZARD = Tilemap(self.GAME)
        self.GENERATOR(self.GAME)

    def logic(self) -> None: #behaviour of a level
        self.PLAYER.behaviour()
        hazard_contacts = pygame.sprite.spritecollide(self.PLAYER, self.HAZARD.SPRITES, False)
        if(len(hazard_contacts) > 0):
            self.PLAYER.death()

    def add_ground_tile(self, sprite_path: str, tile_pos: tuple[int, int]):
        self.GROUND.addTile(sprite_path, tile_pos)
        
    def add_hazard_tile(self, sprite_path: str, tile_pos: tuple[int, int]):
        self.HAZARD.addTile(sprite_path, tile_pos)

    def add_character(self, sprite_path: str, pos: Vector2[float, float], speed: float):
        from Objects import Character
        if(self.__PLAYER != None):
            raise RuntimeError("More than one character can't be spawned")
        self.__PLAYER = Character(sprite_path, pos, speed, self.GAME)
        self.SPRITES.add(self.PLAYER)
