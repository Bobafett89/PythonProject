import pygame
import os

class GAME:
    SCREEN = pygame.display.set_mode()
    CLOCK = pygame.time.Clock()
    SPRITES = pygame.sprite.Group()
    is_running = True

    class level:
        GROUND = None
        PLAYER = None
        SIZE = None
        TILE_SIZE = None

        @staticmethod
        def logic() -> None:
            GAME.level.PLAYER.behaviour()

    class frame:
        delta_time = 0
        @staticmethod
        def next() -> None:
            GAME.frame.delta_time = GAME.CLOCK.tick(120) / 1000

        @staticmethod
        def render() -> None:
            GAME.SCREEN.fill("black")
            GAME.level.GROUND.render(GAME.SCREEN)
            GAME.SPRITES.draw(GAME.SCREEN)
            pygame.display.flip()

    class init:
        @staticmethod
        def level(size_factor: int) -> None:
            GAME.level.SIZE = size_factor
            GAME.level.TILE_SIZE = GAME.SCREEN.get_width() / (16 * size_factor)
            GAME.level.GROUND = Tilemap()

        @staticmethod
        def player(sprite_path: str, tile_pos: tuple[int, int], speed: float) -> None:
            pos = (pygame.Vector2(tile_pos) + (0.5, 0.5)) * GAME.level.TILE_SIZE
            GAME.level.PLAYER = Character(sprite_path, pos, speed)
            GAME.add.sprite(GAME.level.PLAYER)

    class add:
        @staticmethod
        def ground_tile(sprite_path: str, tile_pos: tuple[int, int]) -> None:
            GAME.level.GROUND.addTile(sprite_path, tile_pos)

        @staticmethod
        def sprite(sprite):
            GAME.SPRITES.add(sprite)

class Basic_object(pygame.sprite.Sprite):
    def __init__(self, sprite_path: str, pos: pygame.Vector2) -> None:
        super().__init__()
        img = pygame.image.load(os.path.join(sprite_path))
        self.image = pygame.transform.scale(img, (GAME.level.TILE_SIZE, GAME.level.TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move_to(center=pos)
    
class Dynamic_object(Basic_object):
    def __init__(self, sprite_path: str, pos: pygame.Vector2) -> None:
        super().__init__(sprite_path, pos)
        self.pos = pygame.Vector2(pos)

    def move(self, offset: pygame.Vector2) -> None:
        self.pos.update(self.pos + offset)
        self.rect = self.rect.move_to(center=self.pos)

    def behaviour(self) -> None:
        pass

class Character(Dynamic_object):
    SIZE_Y = 1
    SIZE_X = 0.5
    SIZE_FACTOR = 0.8
    GROUND_MARGIN = 0.05

    def __init__(self, sprite_path: str, pos: pygame.Vector2, speed: float) -> None:
        super().__init__(sprite_path, pos)
        self.speed = speed * GAME.level.TILE_SIZE
        char_unit = GAME.level.TILE_SIZE * Character.SIZE_FACTOR
        self.image = pygame.transform.scale(self.image, (char_unit * Character.SIZE_X, char_unit * Character.SIZE_Y))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move_to(center=pos)
    
    def behaviour(self) -> None:
        keys = pygame.key.get_pressed()
        speed = self.speed * GAME.frame.delta_time
        dirs = self.can_go()

        if(keys[pygame.K_d] and dirs[1]):
            self.move(pygame.Vector2(speed, 0))
        if(keys[pygame.K_a] and dirs[0]):
            self.move(pygame.Vector2(-speed, 0))
        if(keys[pygame.K_w] and dirs[2]):
            self.move(pygame.Vector2(0, -speed))
        if(keys[pygame.K_s] and dirs[3]):
            self.move(pygame.Vector2(0, speed))

    def can_go(self) -> list[bool, bool, bool, bool]:
        def get_grid() -> list[list[bool, bool, bool], list[bool, bool, bool], list[bool, bool, bool]]:
            tile_pos = pygame.Vector2(self.pos.x, self.pos.y) // GAME.level.TILE_SIZE
            grid = [[True, True, True], [True, True, True], [True, True, True]]
            for i in range(3):
                if((tile_pos.x != 0 or i != 0) and (tile_pos.x != len(GAME.level.GROUND.MAP) - 1 or i != 2)):
                    for j in range(3):
                        if((tile_pos.y != 0 or j != 0) and (tile_pos.y != len(GAME.level.GROUND.MAP[0]) - 1 or j != 2)):
                            grid[i][j] = GAME.level.GROUND.MAP[int(tile_pos.x) - 1 + i][int(tile_pos.y) - 1 + j]
            return grid
        
        def get_border() -> tuple[pygame.Vector2, pygame.Vector2]:
            pos_in_tile = pygame.Vector2(self.pos.x, self.pos.y) / GAME.level.TILE_SIZE
            pos_in_tile -= pos_in_tile // 1
            border_offset = pygame.Vector2(Character.SIZE_X, Character.SIZE_Y) * Character.SIZE_FACTOR / 2
            top_left = pos_in_tile - pygame.Vector2(border_offset.x, border_offset.y)
            bottom_right = pos_in_tile + pygame.Vector2(border_offset.x, border_offset.y)
            return (top_left, bottom_right)

        dirs = [False, False, False, False]
        top_left, bottom_right = get_border()
        map = get_grid()
        for i in range(2):
            isNotTouching = top_left.x > Character.GROUND_MARGIN if i==0 else bottom_right.x < 1 - Character.GROUND_MARGIN
            if(isNotTouching):
                dirs[i] = True
            else:
                top = top_left.y > 0 or not map[2 * i][0]
                middle = not map[2 * i][1]
                bot = bottom_right.y < 1 or not map[2 * i][2]
                dirs[i] = top and middle and bot

        for i in range(2):
            isNotTouching = top_left.y > Character.GROUND_MARGIN if i==0 else bottom_right.y < 1 - Character.GROUND_MARGIN
            if(isNotTouching):
                dirs[2+i] = True
            else:
                top = top_left.x > 0 or not map[0][2 * i]
                middle = not map[1][2 * i]
                bot = bottom_right.x < 1 or not map[2][2 * i]
                dirs[2+i] = top and middle and bot

        return dirs

class Tilemap:
    def __init__(self) -> None:
        self.SPRITES = pygame.sprite.Group()
        self.MAP = []
        for i in range(16 * GAME.level.SIZE):
            self.MAP.append([])
            for j in range(9 * GAME.level.SIZE):
                self.MAP[i].append(False)
    
    def addTile(self, spritePath: str, tile_pos: tuple[int, int]) -> None:
        pos = (pygame.Vector2(tile_pos) + (0.5, 0.5)) * GAME.level.TILE_SIZE
        tile = Basic_object(spritePath, pos)
        self.SPRITES.add(tile)
        self.MAP[tile_pos[0]][tile_pos[1]] = True

    def render(self, surface: pygame.Surface) -> None:
        self.SPRITES.draw(surface)
