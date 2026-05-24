import pygame
from pygame import Vector2
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
        def player(sprite_path: str, tile_pos: tuple[float, float], speed: float) -> None:
            pos = (Vector2(tile_pos) + Vector2(0.5, 0.5)) * GAME.level.TILE_SIZE
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
    def __init__(self, sprite_path: str, pos: Vector2) -> None:
        super().__init__()
        img = pygame.image.load(os.path.join(sprite_path))
        self.image = pygame.transform.scale(img, (GAME.level.TILE_SIZE, GAME.level.TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move_to(center=pos)
    
class Dynamic_object(Basic_object):
    def __init__(self, sprite_path: str, pos: Vector2) -> None:
        super().__init__(sprite_path, pos)
        self.pos = Vector2(pos)

    def move(self, offset: Vector2) -> None:
        self.pos += offset
        self.rect = self.rect.move_to(center=self.pos)

    def behaviour(self) -> None:
        pass

class Character(Dynamic_object):
    SIZE = Vector2(0.5, 1) * 0.8

    class physics:
        def __init__(self, character: Character) -> None:
            self.COLLIDER_MARGIN = 0.05
            self.VELOCITY = Vector2(0, 0)
            self.GRAVITY = 10
            self.JUMP = 5
            self.on_ground = False
            self.character = character

        def collide(self) -> None:
            def get_map() -> list[list[bool, bool, bool], list[bool, bool, bool], list[bool, bool, bool]]:
                tile_pos = Vector2(self.character.pos.x, self.character.pos.y) // GAME.level.TILE_SIZE
                grid = [[True, True, True], [True, True, True], [True, True, True]]
                for i in range(3):
                    if((tile_pos.x != 0 or i != 0) and (tile_pos.x != len(GAME.level.GROUND.MAP) - 1 or i != 2)):
                        for j in range(3):
                            if((tile_pos.y != 0 or j != 0) and (tile_pos.y != len(GAME.level.GROUND.MAP[0]) - 1 or j != 2)):
                                grid[i][j] = GAME.level.GROUND.MAP[int(tile_pos.x) - 1 + i][int(tile_pos.y) - 1 + j]
                return grid
            
            def get_local_pos() -> Vector2:
                pos_in_tile = Vector2(self.character.pos.x, self.character.pos.y) / GAME.level.TILE_SIZE
                pos_in_tile -= pos_in_tile // 1
                return pos_in_tile

            def get_border_offset() -> tuple[Vector2, Vector2]:
                border_offset = Character.SIZE / 2
                return border_offset

            def get_border() -> tuple[Vector2, Vector2]:
                pos_in_tile, border_offset = get_local_pos(), get_border_offset()
                top_left = pos_in_tile - border_offset
                bottom_right = pos_in_tile + border_offset
                return (top_left, bottom_right)

            pos_in_tile, border_offset = get_local_pos(), get_border_offset()
            top_left, bottom_right = get_border()
            map = get_map()

            if(self.VELOCITY.y != 0):
                self.on_ground = False
                moving_down = self.VELOCITY.y > 0
                dir = 2 * moving_down - 1
                collider_edge = pos_in_tile.y + (border_offset.y + self.COLLIDER_MARGIN) * dir
                border = 1 * moving_down
                is_not_touching = (collider_edge * dir) < border
                if(not is_not_touching):
                    left = top_left.x > 0 or not map[0][2 * moving_down]
                    middle = not map[1][2 * moving_down]
                    right = bottom_right.x < 1 or not map[2][2 * moving_down]
                    can_move = left and middle and right
                    if(not can_move):
                        if(moving_down):
                            self.on_ground = True
                        self.VELOCITY.y = 0

            if(self.VELOCITY.x != 0):
                moving_right = self.VELOCITY.x > 0
                dir = (2 * moving_right - 1)
                collider_edge = pos_in_tile.x + (border_offset.x + self.COLLIDER_MARGIN) * dir
                border = 1 * moving_right
                is_not_touching = (collider_edge * dir) < border
                if(not is_not_touching):
                    top = top_left.y > 0 or not map[2 * moving_right][0]
                    middle = not map[2 * moving_right][1]
                    bot = bottom_right.y < 1 or not map[2 * moving_right][2]
                    can_move = top and middle and bot
                    if(not can_move):
                        self.VELOCITY.x = 0

    def __init__(self, sprite_path: str, pos: Vector2, speed: float) -> None:
        super().__init__(sprite_path, pos)
        self.image = pygame.transform.scale(self.image, Character.SIZE * GAME.level.TILE_SIZE)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move_to(center=pos)

        self.PHYSICS = Character.physics(self)
        self.speed = speed * GAME.level.TILE_SIZE
    
    def behaviour(self) -> None:
        keys = pygame.key.get_pressed()
        speed = self.speed * GAME.frame.delta_time
        gravity = self.PHYSICS.GRAVITY * GAME.frame.delta_time

        self.PHYSICS.VELOCITY.x = speed * keys[pygame.K_d] - speed * keys[pygame.K_a]
        if(keys[pygame.K_w] and self.PHYSICS.on_ground):
            self.PHYSICS.VELOCITY.y = -self.PHYSICS.JUMP
            self.PHYSICS.on_ground = False
        elif(keys[pygame.K_UP]):
            self.PHYSICS.VELOCITY.y = -self.PHYSICS.JUMP
        else:
            self.PHYSICS.VELOCITY.y += gravity

        self.PHYSICS.collide()
        self.move(self.PHYSICS.VELOCITY)

class Tilemap:
    def __init__(self) -> None:
        self.SPRITES = pygame.sprite.Group()
        self.MAP = []
        for i in range(16 * GAME.level.SIZE):
            self.MAP.append([])
            for j in range(9 * GAME.level.SIZE):
                self.MAP[i].append(False)
    
    def addTile(self, spritePath: str, tile_pos: tuple[int, int]) -> None:
        pos = (Vector2(tile_pos) + Vector2(0.5, 0.5)) * GAME.level.TILE_SIZE
        tile = Basic_object(spritePath, pos)
        self.SPRITES.add(tile)
        self.MAP[tile_pos[0]][tile_pos[1]] = True

    def render(self, surface: pygame.Surface) -> None:
        self.SPRITES.draw(surface)
