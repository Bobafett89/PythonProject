from pygame import Vector2
from BasicObjects import BasicSprite
from Utils import jump_struct, dash_struct, direction, abs_vector2, character_diff

class character_physics_controller:
        def __init__(self, speed: float, jump_force: float, gravity: float, dash_dist: float, dash_speed: float) -> None:
            self.__VELOCITY: Vector2 = Vector2(0, 0)
            self.__GRAVITY: float = gravity
            self.__JUMP: jump_struct = jump_struct(force=jump_force)
            self.__DASH: dash_struct = dash_struct(distance=dash_dist, speed=dash_speed)
            self.__SPEED: float = speed
            self.__dir: float = 1

        @property
        def on_ground(self) -> bool:
            return self.__JUMP.on_ground

        def apply_diff(self, diff: character_diff) -> None:
            self.__JUMP.air_jumps += diff.air_jumps
            self.__JUMP.def_air_jumps += diff.def_air_jumps
            self.__DASH.count += diff.dashes
            self.__DASH.def_count += diff.def_dashes

        def collide(self, obj: type[BasicSprite], ground: TilemapLayer) -> None:
            def hit_floor() -> None:
                if (self.__VELOCITY.y > 0):
                    self.__JUMP.on_ground = True
                    if (self.__JUMP.air_jumps < self.__JUMP.def_air_jumps):
                        self.__JUMP.air_jumps = self.__JUMP.def_air_jumps
                    if (self.__DASH.count < self.__DASH.def_count):
                        self.__DASH.count = self.__DASH.def_count

            def hit_wall() -> None:
                self.__DASH.is_active = False
                self.__DASH.destination = None

            def next_state() -> BasicSprite:
                return BasicSprite(None, obj.size, obj.pos + self.__VELOCITY)

            if (self.__VELOCITY.y != 0):
                self.__JUMP.on_ground = False
            new_state = next_state()
            tiles = ground.collides(new_state, True)
            tiles.sort(key = (lambda tile: (tile.pos - obj.pos).length()))
            for tile in tiles:
                min_dist = new_state.edge_offset + tile.edge_offset
                dir = tile.pos - obj.pos
                dist = abs_vector2(tile.pos - new_state.pos)
                if (dist.x < min_dist.x and dist.y < min_dist.y):
                    epsilon = 2 ** (-53)
                    size = min_dist - dist + Vector2(epsilon, epsilon)
                    offset = Vector2(0, 0)
                    if (abs(dir.x) < min_dist.x or (size.x >= size.y and not abs(dir.y) < min_dist.y)):
                        offset.y = size.y * direction(dir.y < 0)
                        hit_floor()
                    else:
                        offset.x = size.x * direction(dir.x < 0)
                        hit_wall()
                    self.__VELOCITY += offset
                    new_state = next_state()

        def apply_grav(self) -> None:
            if (not self.__DASH.is_active):
                self.__VELOCITY.y += self.__GRAVITY
            else:
                self.__VELOCITY.y = 0
                self.__JUMP.on_ground = False

        def run(self, dir: float) -> None:
            if (not self.__DASH.is_active):
                self.__VELOCITY.x = self.__SPEED * dir

        def dash(self) -> None:
            dash = self.__DASH
            if (not dash.is_active and dash.count > 0):
                dash.is_active = True
                dash.left = dash.distance
                dash.count -= 1
                self.__VELOCITY.x = dash.speed * self.__dir

        def jump(self) -> None:
            if (not self.__DASH.is_active):
                if (self.__JUMP.on_ground or self.__JUMP.air_jumps > 0):
                    self.__VELOCITY.y = -self.__JUMP.force
                    if (not self.__JUMP.on_ground):
                        self.__JUMP.air_jumps -= 1

        def move(self) -> Vector2:
            if (self.__VELOCITY.x != 0):
                self.__dir = direction(self.__VELOCITY.x > 0)
                dash = self.__DASH
                if (dash.is_active):
                    if (abs(self.__VELOCITY.x) >= dash.left):
                        self.__VELOCITY.x = dash.left * self.__dir
                        dash.is_active = False
                    dash.left -= abs(self.__VELOCITY.x)
            return self.__VELOCITY
