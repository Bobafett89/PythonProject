classDiagram
	GameManager *-- UI
	GameManager *-- Frame
	GameManager *-- Level
	GameManager *-- Control
	Level *-- tilemap_info
	Level *-- TilemapLayer
	Level *-- Character
	Level *-- Collectable
	Level *-- MovingCollectable
	Level *-- Finish
	UI *-- UIScreen
	UIScreen *-- Button
	UIScreen ..> Text
	Button --|> BasicSprite
	Text --|> BasicSprite
	LevelSprite --|> BasicSprite
	BasicSprite --|> pygame.sprite.Sprite
	Character --|> LevelSprite
	Character ..> character_physics_controller
	TilemapLayer ..> BasicSprite
	Finish --|> LevelSprite
	Collectable --|> LevelSprite
	Collectable ..> character_diff
	MovingCollectable --|> Collectable
	character_physics_controller ..> jump_struct
	character_physics_controller ..> dash_struct
	Control ..> Command
	class GameManager {
		+is_running: bool
		+FRAME: Frame
		+UI: UI
		+level: Level
		+control: Control
		+start() None
		+set_command() None
		+execute_command() None
		-start_level_from_file() None
		-start_level() None
		-close_level() None
		-reset_level() None
		-close_game() None
	}
	class UI {
		+start_menu: UIScreen
		+current_screen: UIScreen
		+GAME: GameManager
		+set_start_menu() None
		+open_start_menu() None
		+switchUI() None
		+clearUI() None
		+press_buttons() None
	}
	class Frame {
		+SCREEN: pygame.Surface
		+CLOCK: pygame.Clock
		+RENDER_GROUPS: List~pygame.sprite.Group~
		+delta_time: float
		+FIXED_DELTA_TIME: float
		+next() None
		+render() None
	}
	class Level {
		+GAME: GameManager
		+SPRITES: pygame.sprite.Group
		+GENERATOR: Callable[[GameManager], None]
		+SIZE_FACTOR: float
		+UNITS: pygame.Vector2
		+UNIT_PIXEL_SIZE: float
		+TILEMAP: tilemap_info
		+GROUND: TilemapLayer
		+HAZARD: TilemapLayer
		+OBJECTS: List~type[BasicSprite]~
		+COLLECTED: List~type[BasicSprite]~
		+PLAYER: Character
		+acc_delta_time: float
		+static parse_level() Callable[[GameManager], None]
		+convert_tilemap_vector() pygame.Vector2
		+convert_unit_vector() Vector2
		+build_level() None
		+logic() None
		+add_ground_tile() None
		+add_hazard_tile() None
		+add_character() None
		+add_finish() None
		+add_static_item() None
		+add_moving_item() None
		+collect_object() None
		+remove_collected_objects() None
	}
	class UIScreen {
		+SPRITES: pygame.sprite.Group
		+BUTTONS: List~Button~
		+GAME: GameManager
		+add_text() None
		+add_button() None
		+press_buttons() None
	}
	class Button {
		+CALLBACK: Callable[[GameManager], None]
		+behaviour() bool
	}
	class Text {
		+get_max_point_size() int
	}
	class BasicSprite {
		+GAME: GameManager
		+pos: pygame.Vector2
		+size: pygame.Vector2
		+set_center() None
		+move_to() None
		+move_by() None
		+rescale() None
		+set_size() None
		+set_image() None
		+load_image() None
		+overlap() bool
		+behaviour() None
		+fixed_step_behaviour()
	}
	class LevelSprite {
	}
	class Character {
		+PHYSICS: character_physics_controller
		+death_check() None
		+give_air_jumps() None
		+give_dashes() None
		+increase_air_jumps() None
		+increase_dashes() None
	}
	class TilemapLayer {
		+GAME: GameManager
		+SPRITES: pygame.sprite.Group
		+MAP: List~List~BasicSprite~~
		+convert_to_screen() pygame.Vector2
		+convert_to_tilemap() pygame.Vector2
		+addTile() None
		+getTile() BasicSprite | None
		+collides() List~BasicSprite~
	}
	class Finish {
	}
	class Collectable {
		+DIFF: character_diff
		+is_collected: bool
	}
	class MovingCollectable {
		+SPEED: float
		+START: pygame.Vector2
		+DESTINATION: pygame.Vector2
		+DIR: pygame.Vector2
		+to_end: bool
	}
	class character_physics_controller {
		+VELOCITY: pygame.Vector2
		+GRAVITY: float
		+JUMP: jump_struct
		+DASH: dash_struct
		+SPEED: float
		+CHAR: Character
		+dir: float
		+collide() None
		+apply_grav() None
		+run() None
		+dash() None
		+jump() None
		+move() None
	}
	class Command {
		<<Enumeration>>
		WAIT
		SWITCH_UI
		OPEN_LEVEL
		RESTART_LEVEL
		CLOSE_LEVEL
		CLOSE_GAME
	}
	class Control {
		+command: Command
		+parameter: Any
		+static wait() Control
		+static switch_ui() Control
		+static open_level() Control
		+static restart_level() Control
		+static close_level() Control
		+static close_game() Control
	}
	class jump_struct {
		<<dataclass>>
		+on_ground: bool
		+force: int
		+air_jumps: int
		+def_air_jumps: int
	}
	class dash_struct {
		<<dataclass>>
		+is_active: bool
		+speed: float
		+distance: float
		+left: float
		+count: int
		+def_count: int
	}
	class character_diff {
		<<dataclass>>
		+air_jumps: int
		+def_air_jumps: int
		+dashes: int
		+def_dashes: int
	}
	class tilemap_info {
		<<dataclass>>
		+size: pygame.Vector2
		+tile_size: pygame.Vector2
	}
