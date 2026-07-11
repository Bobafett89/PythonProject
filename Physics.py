from pygame import Vector2
from Utils import jump_struct, dash_struct, direction, abs_vector2

class character_physics_controller:
        from Game import Game_manager
        from Objects import Character
        def __init__(self, char: Character, speed: float, jump_force: float, gravity: float, dash_dist: float, dash_speed: float) -> None:
            from Objects import Character
            self.VELOCITY: Vector2 = Vector2(0, 0)
            self.GRAVITY: float = gravity
            self.JUMP: jump_struct = jump_struct(force=jump_force)
            self.DASH: dash_struct = dash_struct(distance=dash_dist, speed=dash_speed)
            self.SPEED: float = speed
            self.CHAR: Character = char
            self.dir: float = 1

        @property
        def GAME(self) -> Game_manager:
            return self.CHAR.GAME

        def collide(self) -> None:
            from BasicObjects import BasicSprite
            def hit_floor() -> None:
                if(self.VELOCITY.y > 0):
                    self.JUMP.on_ground = True
                    if(self.JUMP.air_jumps < self.JUMP.def_air_jumps):
                        self.JUMP.air_jumps = self.JUMP.def_air_jumps
                    if(self.DASH.count < self.DASH.def_count):
                        self.DASH.count = self.DASH.def_count

            def hit_wall() -> None:
                self.DASH.is_active = False
                self.DASH.destination = None

            def next_state() -> BasicSprite:
                return BasicSprite(None, self.CHAR.pos + self.VELOCITY, self.CHAR.size, self.GAME)

            if(self.VELOCITY.y != 0):
                self.JUMP.on_ground = False
            new_state = next_state()
            tiles = self.GAME.level.GROUND.collides(new_state, True)
            tiles.sort(key=(lambda tile: (tile.pos - self.CHAR.pos).length()))
            for tile in tiles:
                min_dist = self.CHAR.edge_offset + tile.edge_offset
                dir = tile.pos - self.CHAR.pos
                dist = abs_vector2(tile.pos - new_state.pos)
                if(dist.x < min_dist.x and dist.y < min_dist.y):
                    epsilon = 2 ** (-53)
                    size = min_dist - dist + Vector2(epsilon, epsilon)
                    offset = Vector2(0, 0)
                    if(abs(dir.x) < min_dist.x or (size.x >= size.y and not abs(dir.y) < min_dist.y)):
                        offset.y = size.y * direction(dir.y < 0)
                        hit_floor()
                    else:
                        offset.x = size.x * direction(dir.x < 0)
                        hit_wall()
                    self.VELOCITY += offset
                    new_state = next_state()
                
        def apply_grav(self) -> None:
            if(not self.DASH.is_active):
                self.VELOCITY.y += self.GRAVITY
            else:
                self.VELOCITY.y = 0
                self.JUMP.on_ground = False

        def run(self, dir: float) -> None:
            if(not self.DASH.is_active):
                self.VELOCITY.x = self.SPEED * dir

        def dash(self) -> None:
            dash = self.DASH
            if(not dash.is_active and dash.count > 0):
                dash.is_active = True
                dash.left = dash.distance
                dash.count -= 1
                self.VELOCITY.x = dash.speed * self.dir

        def jump(self) -> None:
            if(not self.DASH.is_active):
                if(self.JUMP.on_ground or self.JUMP.air_jumps > 0):
                    self.VELOCITY.y = -self.JUMP.force
                    if(not self.JUMP.on_ground):
                        self.JUMP.air_jumps -= 1

        def move(self) -> None:
            if(self.VELOCITY.x != 0):
                self.dir = direction(self.VELOCITY.x > 0)
                dash = self.DASH
                if(dash.is_active):
                    if(abs(self.VELOCITY.x) >= dash.left):
                        self.VELOCITY.x = dash.left * self.dir
                        dash.is_active = False
                    dash.left -= abs(self.VELOCITY.x)
            self.CHAR.move_by(self.VELOCITY)
