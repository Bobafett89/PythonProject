import pygame
from pygame import Vector2

class GAME: #Game manager
    SCREEN = pygame.display.set_mode()
    CLOCK = pygame.time.Clock()
    RENDER_GROUPS = []
    is_running = True

    class level: #functions and variables associated with the level
        SPRITES = None
        GENERATOR = None
        GROUND = None
        HAZARD = None
        PLAYER = None
        SIZE = None
        TILE_SIZE = None

        @staticmethod
        def logic() -> None: #behaviour of a level
            GAME.level.PLAYER.behaviour()
            hazard_contacts = pygame.sprite.spritecollide(GAME.level.PLAYER, GAME.level.HAZARD.SPRITES, False)
            if(len(hazard_contacts) > 0):
                GAME.level.PLAYER.death()

        @staticmethod
        def close(): #deinitializes level
            GAME.RENDER_GROUPS = []
            GAME.level.SPRITES = None
            GAME.level.GENERATOR = None
            GAME.level.GROUND = None
            GAME.level.HAZARD = None
            GAME.level.PLAYER = None
            GAME.level.SIZE = None
            GAME.level.TILE_SIZE = None

        @staticmethod
        def reset() -> None: #reinitializes the level
            size = GAME.level.SIZE
            generator = GAME.level.GENERATOR
            GAME.level.close()
            GAME.init.level(size, generator)

    class frame: #functions and variables associated with frame data
        delta_time = 0
        @staticmethod
        def next() -> None:
            GAME.frame.delta_time = GAME.CLOCK.tick(120) / 1000

        @staticmethod
        def render() -> None:
            GAME.SCREEN.fill("black")
            for i in range(len(GAME.RENDER_GROUPS)):
                GAME.RENDER_GROUPS[i].draw(GAME.SCREEN)
            pygame.display.flip()

    class init: #functions to initialize things
        @staticmethod
        def level(size_factor: int, generator: function) -> None: #initializes level
            from Objects import Tilemap
            GAME.level.SPRITES = pygame.sprite.Group()
            GAME.level.SIZE = size_factor
            GAME.level.TILE_SIZE = GAME.SCREEN.get_width() / (16 * size_factor)
            GAME.level.GROUND = Tilemap()
            GAME.level.HAZARD = Tilemap()
            GAME.level.GENERATOR = generator
            generator()
            GAME.RENDER_GROUPS.append(GAME.level.SPRITES)
            GAME.RENDER_GROUPS.append(GAME.level.GROUND.SPRITES)
            GAME.RENDER_GROUPS.append(GAME.level.HAZARD.SPRITES)

        @staticmethod
        def player(sprite_path: str, pos: Vector2[float, float], speed: float) -> None: #initialize player in the active level
            from Objects import Character
            GAME.level.PLAYER = Character(sprite_path, pos, speed)
            GAME.add.level_sprite(GAME.level.PLAYER)

    class add: #functions to dynamically add something to the game
        @staticmethod
        def ground_tile(sprite_path: str, tile_pos: tuple[int, int]) -> None: #adds a tile to the ground tilemap of the active level
            GAME.level.GROUND.addTile(sprite_path, tile_pos)

        def hazard_tile(sprite_path: str, tile_pos: tuple[int, int]) -> None: #adds a tile to the hazard tilemap of the active level
            GAME.level.HAZARD.addTile(sprite_path, tile_pos)

        @staticmethod
        def level_sprite(sprite): #adds a renderable object to the active level
            GAME.level.SPRITES.add(sprite)
