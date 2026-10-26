import pygame
from pygame import Vector2
from BasicObjects import BasicSprite
from Utils import character_diff, Control, in_right_interval, direction, trunc_vector2, vector2_div, vector2_mult
from math import ceil

class Character(BasicSprite):
    def __init__(self, sprite_path: str, size: Vector2, pos: Vector2, jump_dist: float, jump_height: float, jump_time: float, dash_dist: float, dash_time: float) -> None:
        super().__init__(sprite_path, size, pos)
        from Game import GAME
        from Physics import character_physics_controller as physics
        jump_force = 2 * jump_height / jump_time * GAME.fixed_dt()
        gravity = (2 * jump_height / jump_time) / jump_time * (GAME.fixed_dt() ** 2)
        speed = jump_dist / (2 * jump_time) * GAME.fixed_dt()
        dash_speed = dash_dist / dash_time * GAME.fixed_dt()

        self.PHYSICS: physics = physics(self, speed, jump_force, gravity, dash_dist, dash_speed)

    def behaviour(self) -> None:
        keys, new_keys = pygame.key.get_pressed(), pygame.key.get_just_pressed()

        if(new_keys[pygame.K_LSHIFT]):
            self.PHYSICS.dash()

        dir = 1 * keys[pygame.K_d] - 1 * keys[pygame.K_a]
        self.PHYSICS.run(dir)

        if(keys[pygame.K_w] and self.PHYSICS.JUMP.on_ground or new_keys[pygame.K_w]):
            self.PHYSICS.jump()

        self.__debug()

    def fixed_step_behaviour(self):
        self.PHYSICS.apply_grav()

        keys = pygame.key.get_pressed()
        dir = 1 * keys[pygame.K_d] - 1 * keys[pygame.K_a]
        self.PHYSICS.run(dir)

        if(keys[pygame.K_w] and self.PHYSICS.JUMP.on_ground):
            self.PHYSICS.jump()

        self.PHYSICS.collide()
        self.PHYSICS.move()
        self.death_check()

    def death_check(self) -> None:
        from Game import GAME
        hazard_contacts = GAME._level.TILEMAP.collides("hazard", self, False)
        if(len(hazard_contacts) > 0):
            GAME.set_command(Control.restart_level())

    def give_air_jumps(self, count: int) -> None:
        self.PHYSICS.JUMP.air_jumps += count

    def give_dashes(self, count: int) -> None:
        self.PHYSICS.DASH.count += count

    def increase_air_jumps(self, count: int) -> None:
        self.PHYSICS.JUMP.def_air_jumps += count

    def increase_dashes(self, count: int) -> None:
        self.PHYSICS.DASH.def_count += count

    def __debug(self) -> None:
        keys, new_keys = pygame.key.get_pressed(), pygame.key.get_just_pressed()
        if(keys[pygame.K_UP]):
            self.PHYSICS.VELOCITY.y = -self.PHYSICS.JUMP.force
        if(keys[pygame.K_DOWN]):
            self.PHYSICS.VELOCITY.y = self.PHYSICS.JUMP.force
        if(new_keys[pygame.K_1]):
           self.increase_air_jumps(1)
        if(new_keys[pygame.K_2]):
           self.increase_dashes(1)

class Tilemap:
    def __init__(self, size: Vector2) -> None:
        self._SIZE: Vector2 = size
        self._TILESIZE: Vector2 = vector2_div(Vector2(1, 1), self._SIZE)
        self._SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self._MAP: dict[list[list[BasicSprite]]] = dict()

    @property
    def size(self) -> Vector2:
        return self._SIZE

    @property
    def SPRITES(self) -> pygame.sprite.Group:
        return self._SPRITES

    def _convert_to_screen(self, pos: Vector2) -> Vector2:
        return vector2_div(pos, self._SIZE)

    def _convert_to_tilemap(self, pos: Vector2) -> Vector2:
        return vector2_mult(pos, self._SIZE)

    def add_layer(self, name: str) -> None:
        self._MAP[name] = []
        layer = self._MAP[name]
        for i in range(int(self._SIZE.x)):
            layer.append([])
            for j in range(int(self._SIZE.y)):
                layer[i].append(None)

    def add_tile(self, sprite_path: str, layer_name: str, tile_pos: Vector2) -> None:
        from Game import GAME
        layer = self._MAP[layer_name]
        if(layer[int(tile_pos.x)][int(tile_pos.y)] == None):
            pos = self._convert_to_screen(tile_pos + Vector2(0.5, 0.5))
            tile = BasicSprite(sprite_path, self._TILESIZE, pos)
            self._SPRITES.add(tile)
            layer[int(tile_pos.x)][int(tile_pos.y)] = tile

    def get_tile(self, layer_name: str, tile_pos: Vector2, pseudo_tile: bool) -> BasicSprite | None:
        layer = self._MAP[layer_name]
        if(in_right_interval(tile_pos.x, 0, self._SIZE.x) and in_right_interval(tile_pos.y, 0, self._SIZE.y)):
            return layer[int(tile_pos.x)][int(tile_pos.y)]
        else:
            if(pseudo_tile):
                pos = self._convert_to_screen(tile_pos + Vector2(0.5, 0.5))
                return BasicSprite(None, self._TILESIZE, pos)
            else:
                return None

    def collides(self, layer_name: str, object: type[BasicSprite], pseudo_tiles: bool) -> list[BasicSprite]:
        tilemap_pos = trunc_vector2(self._convert_to_tilemap(object.pos))
        border_offset = self._convert_to_tilemap(object.edge_offset)
        tile_offset = Vector2(ceil(border_offset.x), ceil(border_offset.y))
        collisions = []
        for i in range(int(-tile_offset.x), int(tile_offset.x) + 1):
            for j in range(int(-tile_offset.y), int(tile_offset.y) + 1):
                offset = Vector2(i, j)
                tile = self.get_tile(layer_name, tilemap_pos + offset, pseudo_tiles)
                if(tile != None and tile.overlap(object)):
                    collisions.append(tile)
        return collisions

class Finish(BasicSprite):
    def __init__(self, sprite_path: str | None, size: Vector2, pos: Vector2) -> None:
        super().__init__(sprite_path, size, pos)

    def fixed_step_behaviour(self) -> None:
        from Game import GAME
        character = GAME._level.PLAYER
        if(self.overlap(character)):
            GAME.set_command(Control.close_level())

class Collectable(BasicSprite):
    def __init__(self, sprite_path: str | None, size: Vector2, pos: Vector2, diff: character_diff) -> None:
        super().__init__(sprite_path, size, pos)
        self.DIFF: character_diff = diff
        self.is_collected: bool = False

    def fixed_step_behaviour(self) -> None:
        from Game import GAME
        character = GAME._level.PLAYER
        collide_with_character = self.overlap(character)
        if(collide_with_character and not self.is_collected):
            character.give_air_jumps(self.DIFF.air_jumps)
            character.increase_air_jumps(self.DIFF.def_air_jumps)
            character.give_dashes(self.DIFF.dashes)
            character.increase_dashes(self.DIFF.def_dashes)
            self.is_collected = True
            GAME._level.collect_object(self)

class MovingCollectable(Collectable):
    def __init__(self, sprite_path: str | None, size: Vector2, pos: Vector2, diff: character_diff, speed: float, destination: Vector2) -> None:
        from Game import GAME
        super().__init__(sprite_path, size, pos, diff)
        self.SPEED: float = speed * GAME.fixed_dt()
        self.START: Vector2 = self.pos.copy()
        self.DESTINATION: Vector2 = destination
        self.DIR: Vector2 = (self.DESTINATION - self.START).normalize()
        self.to_end: bool = True

    def fixed_step_behaviour(self) -> None:
        target: Vector2 = None
        if(self.to_end):
            target = self.DESTINATION
        else:
            target = self.START
        left = (target - self.pos).length()
        offset = self.DIR.copy() * direction(self.to_end)
        if(self.SPEED < left):
            offset *= self.SPEED
        else:
            offset *= left
            self.to_end = not self.to_end
        self.move_by(offset)
        super().fixed_step_behaviour()
