import pygame
from pygame import Vector2
from BasicObjects import BasicSprite, Player_diff, Control, Jump_params, Dash_params, Transform, PhysicsSystem, Frame
from Utils import in_rect, direction, trunc_vector2, vector2_div, vector2_mult, Interval
from math import ceil

class Level:
    __DEF_LEVEL_SIZE: Vector2 = Vector2(16, 9)
    __DEF_TILEMAP_LAYERS: list[str] = ["ground", "hazard"]

    def __init__(self, generator: Callable[[Level], None], tilemap_size: Vector2) -> None:
        self.__SPRITES: pygame.sprite.Group = pygame.sprite.Group()
        self.__GENERATOR: Callable[[Level], None] = generator
        self.__TILEMAP: Tilemap = Tilemap(tilemap_size)
        self.__OBJECTS: list[type[BasicSprite]] = []
        self.__COLLECTABLES: list[type[Collectable]] = []
        self.__FINISHES: list[type[Finish]] = []
        self.__PLAYER: Player = None
        self.__build_level()
        self.__command: Control = None

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

    @property
    def command(self) -> Control:
        if (self.__command != None):
            return self.__command
        else:
            return Control.wait()

    @classmethod
    def parse_level(cls, level_struct: dict[str, Any]) -> Callable[[Level], None]:
        def has_keys(keys: list[str] | str, where: dict[str, Any], type: type | tuple[type, ...]) -> bool:
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

        def has_sprite(where: dict[str, Any]):
            return has_keys("spr", where, str)

        def validate_list(arr: list[Any], size: int, type: type | tuple[type, ...]) -> bool:
            valid: bool = False
            if (len(arr) == size or size == 0):
                valid = True
                for element in arr:
                    if (not isinstance(element, type)):
                        valid = False
                        break
            return valid

        def validate_point(pos: list[Any], is_int: bool = False) -> bool:
            pos_type: type | tuple[type, ...] = None
            if (is_int):
                pos_type = int
            else:
                pos_type = (int, float)
            return validate_list(pos, 2, pos_type)

        def validate_poses(poses: list[Any], is_int: bool = False, include_lines: bool = False) -> bool:
            valid: bool = validate_list(poses, 0, list)
            if (valid):
                for pos in poses:
                    valid_point: bool = validate_point(pos, is_int)
                    valid_line: bool = include_lines and validate_list(pos, 2, list) and validate_point(pos[0], is_int) and validate_point(pos[1], is_int)
                    if (not (valid_point or valid_line)):
                        valid = False
                        break
            return valid

        def has_valid_pos(where: dict[str, Any]) -> bool:
            return has_keys("pos", where, list) and validate_point(where["pos"])

        def has_valid_poses(where: dict[str, Any]) -> bool:
            return has_keys("pos", where, list) and validate_poses(where["pos"])

        def has_valid_size(where: dict[str, Any]) -> bool:
            return has_keys("size", where, list) and validate_point(where["size"])

        def validate_tilemap(tilemap: list[Any]) -> bool:
            valid_tilemap: bool = True
            for tile in tilemap:
                valid_sprite: bool = has_sprite(tile)
                valid_pos: bool = has_keys("pos", tile, list) and validate_poses(tile["pos"], True, True)
                valid_tilemap = valid_sprite and valid_pos
                if (not valid_tilemap):
                    break
            return valid_tilemap

        def generator(level: Level) -> None:
            level_size: Vector2 = cls.__DEF_LEVEL_SIZE * level_struct["size_factor"]

            def point_to_vector(point: list[float | int]) -> Vector2:
                return Vector2(point[0], point[1])

            def build_tilemap(tilemap: list[dict[str, Any]], add_tile: Callable[[str, Vector2], None]) -> None:
                for tile in tilemap:
                    for pos in tile["pos"]:
                        if (isinstance(pos[0], list)):
                            first_pos: Vector2 = point_to_vector(pos[0])
                            second_pos: Vector2 = point_to_vector(pos[1])
                            leftop: Vector2 = Vector2(min(first_pos.x, second_pos.x), min(first_pos.y, second_pos.y))
                            botright: Vector2 = Vector2(max(first_pos.x, second_pos.x), max(first_pos.y, second_pos.y))
                            size: Vector2 = botright - leftop + Vector2(1, 1)
                            for i in range(int(size.x)):
                                for j in range(int(size.y)):
                                    offset = Vector2(i, j)
                                    add_tile(tile["spr"], leftop + offset)
                        else:
                            tile_pos: Vector2 = point_to_vector(pos)
                            add_tile(tile["spr"], tile_pos)

            def to_screen_vector(level_vector: Vector2) -> Vector2:
                return vector2_div(level_vector, level_size)

            player: dict[str, Any] = level_struct["player"]
            jump: dict[str, Any] = player["jump"]
            dash: dict[str, Any] = player["dash"]
            ground: dict[str, Any] = level_struct["tiles"]["grnd"]
            hazard: dict[str, Any] = level_struct["tiles"]["hzrd"]
            finishes: dict[str, Any] = level_struct["finishes"]
            static_items: dict[str, Any] = level_struct["items"]["stc"]
            moving_items: dict[str, Any] = level_struct["items"]["mov"]

            player_pos: Vector2 = to_screen_vector(point_to_vector(player["pos"]))
            player_size: Vector2 = to_screen_vector(point_to_vector(player["size"]))
            jump: Jump_params = Jump_params(jump["dist"] / level_size.x, jump["height"] / level_size.y, jump["time"])
            dash: Dash_params = Dash_params(dash["dist"] / level_size.x, dash["time"])
            level.add_player(player["spr"], Transform(player_size, player_pos), jump, dash)

            for finish in finishes:
                for pos in finish["pos"]:
                    finish_pos: Vector2 = to_screen_vector(point_to_vector(pos))
                    finish_size: Vector2 = to_screen_vector(point_to_vector(finish["size"]))
                    level.add_finish(finish["spr"], Transform(finish_size, finish_pos))

            build_tilemap(ground, level.add_ground_tile)

            build_tilemap(hazard, level.add_hazard_tile)

            for item in static_items:
                for pos in item["pos"]:
                    item_size: Vector2 = to_screen_vector(point_to_vector(item["size"]))
                    item_pos: Vecttor2 = to_screen_vector(point_to_vector(pos))
                    item_diff: Player_diff = Player_diff(item["diff"][0], item["diff"][1], item["diff"][2], item["diff"][3])
                    level.add_static_item(item["spr"], Transform(item_size, item_pos), item_diff)

            for item in moving_items:
                for i in range(len(item["pos"])):
                    item_size: Vector2 = to_screen_vector(point_to_vector(item["size"]))
                    item_pos: Vector2 = to_screen_vector(point_to_vector(item["pos"][i]))
                    item_dest: Vector2 = to_screen_vector(point_to_vector(item["dest"][i]))
                    item_speed: float = (item_dest - item_pos).length() / item["time"]
                    item_diff: Player_diff = Player_diff(item["diff"][0], item["diff"][1], item["diff"][2], item["diff"][3])
                    level.add_moving_item(item["spr"], Transform(item_size, item_pos), item_diff, item_speed, item_dest)

        valid_size_factor: bool = has_keys("size_factor", level_struct, int)

        valid_tiles: bool = has_keys("tilemap_size", level_struct, list) and validate_point(level_struct["tilemap_size"], True)

        valid_player: bool = has_keys("player", level_struct, dict)
        if (valid_player):
            player: dict[str, Any] = level_struct["player"]
            valid_sprite: bool = has_sprite(player)
            valid_size: bool = has_valid_size(player)
            valid_pos: bool = has_valid_pos(player)
            valid_jump: bool = has_keys("jump", player, dict) and has_keys(["height", "dist", "time", "temp", "def"], player["jump"], (int, float))
            valid_dash: bool = has_keys("dash", player, dict) and has_keys(["dist", "time", "temp", "def"], player["dash"], (int, float))
            valid_player: bool = valid_sprite and valid_size and valid_pos and valid_jump and valid_dash

        tiles: dict[str, Any] = dict()
        if (has_keys("tiles", level_struct, dict)):
            tiles = level_struct["tiles"]
        valid_ground: bool = has_keys("grnd", tiles, list) and validate_list(tiles["grnd"], 0, dict) and validate_tilemap(tiles["grnd"])
        valid_hazard: bool = has_keys("hzrd", tiles, list) and validate_list(tiles["hzrd"], 0, dict) and validate_tilemap(tiles["hzrd"])

        valid_finishes: bool = has_keys("finishes", level_struct, list) and validate_list(level_struct["finishes"], 0, dict)
        valid_finishes: bool = valid_finishes and len(level_struct["finishes"]) > 0
        if (valid_finishes):
            for finish in level_struct["finishes"]:
                valid_spr: bool = has_sprite(finish)
                valid_size: bool = has_valid_size(finish)
                valid_pos: bool = has_valid_poses(finish)
                valid_finishes: bool = valid_spr and valid_size and valid_pos
                if (not valid_finishes):
                    break

        items: dict[str, Any] = dict()
        if (has_keys("items", level_struct, dict)):
            items = level_struct["items"]

        valid_static_items: bool = has_keys("stc", items, list) and validate_list(items["stc"], 0, dict)
        if (valid_static_items):
            for item in items["stc"]:
                valid_sprite: bool = has_sprite(item)
                valid_size: bool = has_valid_size(item)
                valid_diff: bool = has_keys("diff", item, list) and validate_list(item["diff"], 4, int)
                valid_pos: bool = has_valid_poses(item)
                valid_static_items: bool = valid_sprite and valid_size and valid_diff and valid_pos
                if (not valid_static_items):
                    break

        valid_moving_items: bool = has_keys("mov", items, list) and validate_list(items["mov"], 0, dict)
        if (valid_moving_items):
            for item in items["mov"]:
                valid_sprite: bool = has_sprite(item)
                valid_size: bool = has_valid_size(item)
                valid_diff: bool = has_keys("diff", item, list) and validate_list(item["diff"], 4, int)
                valid_time: bool = has_keys("time", item, (int, float))
                valid_pos: bool = has_valid_poses(item)
                valid_dest: bool = valid_pos and has_keys("dest", item, list) and len(item["dest"]) == len(item["pos"]) and validate_poses(item["dest"])
                valid_moving_items: bool = valid_sprite and valid_diff and valid_pos and valid_time and valid_dest
                if (not valid_moving_items):
                    break

        valid_tilemaps: bool = valid_tiles and valid_ground and valid_hazard
        valid_items: bool = valid_static_items and valid_moving_items
        if (not (valid_size_factor and valid_player and valid_tilemaps and valid_finishes and valid_items)):
            raise RuntimeError("Not valid structure of a level")

        return generator

    def __build_level(self) -> None:
        for name in Level.__DEF_TILEMAP_LAYERS:
            self.__TILEMAP.add_layer(name)
        self.__GENERATOR(self)

    def __set_command(self, command: Control) -> None:
        if (self.__command == None):
            self.__command = command

    def logic(self, fixed_steps: int) -> None:
        for object in self.__OBJECTS:
            object.update()
        for i in range(fixed_steps):
            for object in self.__OBJECTS:
                object.fixed_update()
            if (self.__PLAYER.dead):
                self.__set_command(Control.restart_level())
            for finish in self.__FINISHES:
                if (finish.finished):
                    self.__set_command(Control.close_level())
                    break
        self.__collect_items()

    def add_ground_tile(self, sprite_path: str, tile_pos: Vector2) -> None:
        self.__TILEMAP.add_tile(sprite_path, "ground", tile_pos)

    def add_hazard_tile(self, sprite_path: str, tile_pos: Vector2) -> None:
        self.__TILEMAP.add_tile(sprite_path, "hazard", tile_pos)

    def add_player(self, sprite_path: str, transform: Transform, jump: Jump_params, dash: Dash_params) -> None:
        if (self.__PLAYER != None):
            raise RuntimeError("More than one player can't be spawned")
        self.__PLAYER = Player(sprite_path, transform, jump, dash, self.__TILEMAP)
        self.__OBJECTS.append(self.__PLAYER)
        self.__SPRITES.add(self.__PLAYER)

    def add_finish(self, sprite_path: str, transform: Transform) -> None:
        finish = Finish(sprite_path, transform, self.__PLAYER)
        self.__OBJECTS.append(finish)
        self.__FINISHES.append(finish)
        self.__SPRITES.add(finish)

    def add_static_item(self, sprite_path: str, transform: Transform, diff: Player_diff) -> None:
        collectable: Collectable = Collectable(sprite_path, transform, diff, self.__PLAYER)
        self.__OBJECTS.append(collectable)
        self.__COLLECTABLES.append(collectable)
        self.__SPRITES.add(collectable)

    def add_moving_item(self, sprite_path: str, transform: Transform, diff: Player_diff, speed: float, destination: Vector2) -> None:
        collectable: Collectable = MovingCollectable(sprite_path, transform, diff, speed, destination, self.__PLAYER)
        self.__OBJECTS.append(collectable)
        self.__COLLECTABLES.append(collectable)
        self.__SPRITES.add(collectable)

    def __collect_items(self) -> None:
        for object in self.__COLLECTABLES:
            if (object.is_collected):
                self.__OBJECTS.remove(object)
                self.__COLLECTABLES.remove(object)
                self.__SPRITES.remove(object)

class Player(BasicSprite):
    def __init__(self, sprite_path: str, transform: Transform, jump: Jump_params, dash: Dash_params, tilemap: Tilemap) -> None:
        super().__init__(sprite_path, transform)
        jump_force: float = 2 * jump.height / jump.time * Frame.FIXED_DT()
        gravity: float = jump_force / jump.time * Frame.FIXED_DT()
        speed: float = jump.dist / (2 * jump.time) * Frame.FIXED_DT()
        dash_speed: float = dash.dist / dash.time * Frame.FIXED_DT()

        self.__PHYSICS: PhysicsSystem = PhysicsSystem(speed, jump_force, gravity, dash.dist, dash_speed)
        self.__TILEMAP: Tilemap = tilemap
        self.__dead: bool = False

    @property
    def dead(self) -> bool:
        return self.__dead

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
        hazard_contacts: list[BasicSprite] = self.__TILEMAP.collides("hazard", self, False)
        if (len(hazard_contacts) > 0):
            self.__dead = True

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
        self.__finished: bool = False

    @property
    def finished(self) -> bool:
        return self.__finished

    def fixed_update(self) -> None:
        if (self.overlap(self.__PLAYER)):
            self.__finished = True

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
        super().__init__(sprite_path, transform, diff, player)
        self.__SPEED: float = speed * Frame.FIXED_DT()
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

