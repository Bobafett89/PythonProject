import pygame
from pygame import Vector2
from BasicObjects import BasicSprite, Player_diff, Control, Jump_params, Dash_params, Transform
from BasicObjects import PhysicsSystem as physics
from Utils import in_rect, direction, trunc_vector2, vector2_div, vector2_mult, Interval
from math import ceil

class Player(BasicSprite):
    def __init__(self, sprite_path: str, transform: Transform, jump: Jump_params, dash: Dash_params, tilemap: Tilemap) -> None:
        super().__init__(sprite_path, transform)
        from Game import GAME
        jump_force: float = 2 * jump.height / jump.time * GAME.FIXED_DT()
        gravity: float = jump_force / jump.time * GAME.FIXED_DT()
        speed: float = jump.dist / (2 * jump.time) * GAME.FIXED_DT()
        dash_speed: float = dash.dist / dash.time * GAME.FIXED_DT()

        self.__PHYSICS: physics = physics(speed, jump_force, gravity, dash.dist, dash_speed)
        self.__TILEMAP: Tilemap = tilemap

    def update(self) -> None:
        keys: list[bool] = pygame.key.get_pressed()
        new_keys: list[bool] = pygame.key.get_just_pressed()

        if (new_keys[pygame.K_LSHIFT]):
            self.__PHYSICS.dash()

        dir: int = 1 * keys[pygame.K_d] - 1 * keys[pygame.K_a]
        self.__PHYSICS.run(dir)

        if (keys[pygame.K_w] and self.__PHYSICS.on_ground or new_keys[pygame.K_w]):
            self.__PHYSICS.jump()

        self.__debug()

    def fixed_update(self) -> None:
        self.__PHYSICS.apply_grav()

        keys: list[bool] = pygame.key.get_pressed()
        dir: int = 1 * keys[pygame.K_d] - 1 * keys[pygame.K_a]
        self.__PHYSICS.run(dir)

        if (keys[pygame.K_w] and self.__PHYSICS.on_ground):
            self.__PHYSICS.jump()

        self.__PHYSICS.collide(self, self.__TILEMAP.get_layer("ground"))
        self._move_by(self.__PHYSICS.move())
        self.death_check()

    def death_check(self) -> None:
        from Game import GAME
        hazard_contacts: list[BasicSprite] = self.__TILEMAP.collides("hazard", self, False)
        if (len(hazard_contacts) > 0):
            GAME.set_command(Control.restart_level())

    def apply_diff(self, diff: chacracter_diff):
        self.__PHYSICS.apply_diff(diff)

    def __debug(self) -> None:
        keys: list[bool] = pygame.key.get_pressed()
        new_keys: list[bool] = pygame.key.get_just_pressed()
        if (keys[pygame.K_UP]):
            self.__PHYSICS._PhysicsSystem__VELOCITY.y = -self.__PHYSICS._PhysicsSystem__JUMP.force
        if (keys[pygame.K_DOWN]):
            self.__PHYSICS._PhysicsSystem__VELOCITY.y = self.__PHYSICS._PhysicsSystem__JUMP.force
        if (new_keys[pygame.K_1]):
            self.__PHYSICS._PhysicsSystem__JUMP.def_air_jumps += 1
        if (new_keys[pygame.K_2]):
            self.__PHYSICS._PhysicsSystem__DASH.def_count += 1

class Tilemap:
    def __init__(self, size: Vector2) -> None:
        self.__SIZE: Vector2 = size
        self.__SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.__LAYERS: dict[str, TilemapLayer] = dict()

    @property
    def SIZE(self) -> Vector2:
        return self.__SIZE

    @property
    def SPRITES(self) -> pygame.sprite.Group:
        return self.__SPRITES

    def add_layer(self, name: str) -> None:
        self.__LAYERS[name] = TilemapLayer(self.__SIZE, self.__SPRITES)

    def get_layer(self, name: str) -> TilemapLayer:
        return self.__LAYERS[name]

    def add_tile(self, sprite_path: str, layer_name: str, tile_pos: Vector2) -> None:
        self.__LAYERS[layer_name].add_tile(sprite_path, tile_pos)

    def get_tile(self, layer_name: str, tile_pos: Vector2, pseudo_tile: bool) -> BasicSprite | None:
        return self.__LAYERS[layer_name].get_tile(tile_pos, pseudo_tile)

    def collides(self, layer_name: str, object: type[BasicSprite], pseudo_tiles: bool) -> list[BasicSprite]:
        return self.__LAYERS[layer_name].collides(object, pseudo_tiles)

class TilemapLayer:
    def __init__(self, size: Vector2, sprite_group: pygame.sprite.Group) -> None:
        self.__SIZE: Vector2 = size
        self.__TILESIZE: Vector2 = vector2_div(Vector2(1, 1), self.__SIZE)
        self.__SPRITES: pygame.sprite.Group = sprite_group
        self.__MAP: list[list[BasicSprite]] = []
        for i in range(int(self.__SIZE.x)):
            self.__MAP.append([])
            for j in range(int(self.__SIZE.y)):
                self.__MAP[i].append(None)

    def __convert_to_screen(self, pos: Vector2) -> Vector2:
        return vector2_div(pos, self.__SIZE)

    def __convert_to_tilemap(self, pos: Vector2) -> Vector2:
        return vector2_mult(pos, self.__SIZE)

    def add_tile(self, sprite_path: str, tile_pos: Vector2) -> None:
        if (self.__MAP[int(tile_pos.x)][int(tile_pos.y)] == None):
            pos: Vector2 = self.__convert_to_screen(tile_pos + Vector2(0.5, 0.5))
            tile: BasicSprite = BasicSprite(sprite_path, Transform(self.__TILESIZE, pos))
            self.__SPRITES.add(tile)
            self.__MAP[int(tile_pos.x)][int(tile_pos.y)] = tile

    def get_tile(self, tile_pos: Vector2, pseudo_tile: bool) -> BasicSprite | None:
        if (in_rect(tile_pos, Vector2(0, 0), self.__SIZE, Interval.RIGHTOPEN)):
            return self.__MAP[int(tile_pos.x)][int(tile_pos.y)]
        else:
            if (pseudo_tile):
                pos: Vector2 = self.__convert_to_screen(tile_pos + Vector2(0.5, 0.5))
                return BasicSprite(None, Transform(self.__TILESIZE, pos))
            else:
                return None

    def collides(self, object: type[BasicSprite], pseudo_tiles: bool) -> list[BasicSprite]:
        tilemap_pos: Vector2 = trunc_vector2(self.__convert_to_tilemap(object.pos))
        border_offset: Vector2 = self.__convert_to_tilemap(object.edge_offset)
        tile_offset: Vector2 = Vector2(ceil(border_offset.x), ceil(border_offset.y))
        collisions: list[BasicSprite] = []
        for i in range(int(-tile_offset.x), int(tile_offset.x) + 1):
            for j in range(int(-tile_offset.y), int(tile_offset.y) + 1):
                offset = Vector2(i, j)
                tile = self.get_tile(tilemap_pos + offset, pseudo_tiles)
                if (tile != None and tile.overlap(object)):
                    collisions.append(tile)
        return collisions

class Finish(BasicSprite):
    def __init__(self, sprite_path: str | None, transform: Transform, player: type[BasicSprite]) -> None:
        super().__init__(sprite_path, transform)
        self.__PLAYER: type[BasicSprite] = player

    def fixed_update(self) -> None:
        from Game import GAME
        if (self.overlap(self.__PLAYER)):
            GAME.set_command(Control.close_level())

class Collectable(BasicSprite):
    def __init__(self, sprite_path: str | None, transform: Transform, diff: Player_diff, player: type[Player]) -> None:
        super().__init__(sprite_path, transform)
        self.__DIFF: Player_diff = diff
        self.__is_collected: bool = False
        self.__PLAYER: type[Player] = player

    @property
    def is_collected(self) -> bool:
        return self.__is_collected

    def fixed_update(self) -> None:
        collide_with_player: bool = self.overlap(self.__PLAYER)
        if (collide_with_player and not self.is_collected):
            self.__PLAYER.apply_diff(self.__DIFF)
            self.__is_collected = True

class MovingCollectable(Collectable):
    def __init__(self, sprite_path: str | None, transform: Transform, diff: Player_diff, speed: float, destination: Vector2, player: type[Player]) -> None:
        from Game import GAME
        super().__init__(sprite_path, transform, diff, player)
        self.__SPEED: float = speed * GAME.FIXED_DT()
        self.__START: Vector2 = self.pos.copy()
        self.__DESTINATION: Vector2 = destination
        self.__DIR: Vector2 = (self.__DESTINATION - self.__START).normalize()
        self.__to_end: bool = True

    def fixed_update(self) -> None:
        target: Vector2 = None
        if (self.__to_end):
            target = self.__DESTINATION
        else:
            target = self.__START
        left: float = (target - self.pos).length()
        offset: Vector2 = self.__DIR.copy() * direction(self.__to_end)
        if (self.__SPEED < left):
            offset *= self.__SPEED
        else:
            offset *= left
            self.__to_end = not self.__to_end
        self._move_by(offset)
        super().fixed_update()
