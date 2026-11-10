# План рефакторинга (модуль 1-4)

## Модуль 1
- [ ] Настроить ENV и добавить Requirements
- [x] Сокрыть ненужные для внешнего пользования функции и свойства
- [ ] Добавить README.md

## Модуль 2
- [x] Попытаться выделить dataclass'ы
- [ ] Добавить slots

## Модуль 3
1) Single responsibility:
	- [x] UI знает о Frame и зависит от него - UI должен хранить, что надо рендерить, а GameManager передаёт это в Frame
	- [x] Level отслеживает фиксированные шаги сам вместо Frame - перенести фикс. шаги в Frame
	- [x] TilemapLayer и TilemapInfo хранятся отдельно, хотя отвечают оба отвечают за один концепт - объединить в один объект Tilemap
2) Open-close
3) Liskov substitution
4) Interface segregation
5) Dependancy inversion
	- [x] Объекты обращаются к уровню через GameManager - Нужные для взаимодействия объекты передаются в конструктор
	- [x] Character получает доступ к TilemapLayer через GameManager - См. предыдущий пункт
	- [x] Ещё сильнее ограничить доступ к объектам верхнего уровня (например, объект не отдаёт комманду игре, а владелец объекта отслеживает, когда надо отправить команду 

## Модуль 4
- [x] Добавить ограничение на delta_time
- [x] Выделить компоненты (например, местоположение)
- [x] Выделить системы
- [x] Добавить интерполяцию движения

## Модуль 5
- [ ] Сделать FSM для GAME

# Диаграмма классов
## Упрощённая
```mermaid
---
title: UML class diagram
config:
  layout: elk
  fontSize: 20
  elk:
    lineHops: false
  class:
    hideEmptyMembersBox: true
---
classDiagram
	GAME --* Frame
	GAME --* UI
	GAME --* Level
	GAME --o Control
	Level --* Tilemap
	Level --* Player
	Level --* Collectable
	Level --* MovingCollectable
	Level --* Finish
	Level ..> Control
	Player --|> BasicSprite
	Player --* PhysicsSystem
	Player --o InterpolationSystem
	Player ..> Tilemap
	Player ..|> Interpolatable
	Tilemap --o BasicSprite
	Finish --|> BasicSprite
	Finish ..> BasicSprite
	Collectable --|> BasicSprite
	Collectable ..> BasicSprite
	MovingCollectable --|> Collectable
	MovingCollectable --o InterpolationSystem
	MovingCollectable ..|> Interpolatable
	UI --* UIScreen
	UIScreen --* Text
	UIScreen --* Button
	Text --|> BasicSprite
	Button --|> BasicSprite
	Button ..> Control
	BasicSprite --|> pygame.sprite.Sprite
	BasicSprite ..> Frame
	Control --* Command
	PhysicsSystem ..> BasicSprite
	class GAME {
		-active: bool
		-FRAME: Frame
		-UI: UI
		-level: Level
		-control: Control
		+active() bool
		+init() None
		+start() None
		+set_command() None
		+execute_command() None
		+update() None
		+next_frame() None
		-start_level_from_file() None
		-start_level() None
		-close_level() None
		-reset_level() None
		-open_main_menu() None
		-close_game() None
	}
	class Level {
		-DEF_LEVEL_SIZE: Vector2
		-DEF_TILEMAP_LAYERS: list[str]
		-SPRITES: pygame.sprite.Group
		-GENERATOR: Callable[[Level], None]
		-TILEMAP: Tilemap
		-OBJECTS: list[type[BasicSprite]]
		-COLLECTABLES: list[type[Collectable]]
		-FINISHES: list[type[Finish]]
		-PLAYER: Player
		-command: Control
		+/SPRITES: pygame.sprite.Group
		+/TILEMAP_SPRITES: pygame.sprite.Group
		+/TILEMAP_SIZE: Vector2
		+/GENERATOR: Callable[[Level], None]
		+/command: Control
		+parse_level() Callable[[Level], None]
		-build_level() None
		-set_command() None
		+logic() None
		+add_ground_tile() None
		+add_hazard_tile() None
		+add_player() None
		+add_finish() None
		+add_static_item() None
		+add_moving_item() None
		-collect_items() None
	}
	class Player {
		-PHYSICS: PhysicsSystem
		-TILEMAP: Tilemap
		-INTERPOLATOR: InterpolationSystem
		-dead: bool
		+/dead: bool
		+death_check() None
		+apply_diff() None
	}
	class Tilemap {
		-SIZE: Vector2
		-TILESIZE: Vector2
		-SPRITES: pygame.sprite.Group
		-LAYERS: list[list[BasicSprite]]
		+/SIZE: Vector2
		+/SPRITES: pygame.sprite.Group
		-convert_to_screen(): Vector
		-convert_to_tilemap(): Vector
		+add_layer() None
		+get_layer() list[BasicSprite]
		+add_tile() None
		+get_tile() BasicSprite | None
		+collides() list[BasicSprite]
	}
	class Finish {
		-PLAYER: type[BasicSprite]
		-finished: bool
		+/finished: bool
	}
	class Collectable {
		-DIFF: Player_diff
		-is_collected: bool
		-PLAYER: type[BasicSprite]
		+/DIFF: Player_diff
		+/is_collected: bool
	}
	class MovingCollectable {
		-SPEED: float
		-START: Vector2
		-DESTINATION: Vector2
		-DIR: Vector2
		-to_end: bool
		-INTERPOLATOR: InterpolationSystem
	}
	class UI {
		-start_menu: UIScreen
		-current_screen: UIScreen
		+/SPRITES: pygame.sprite.Group | None
		+set_start_menu() None
		+open_start_menu() None
		+switch_ui() None
		+clear_ui() None
		+press_buttons() Control
	}
	class UIScreen {
		-SPRITES: pygame.sprite.Group
		-BUTTONS: list[Button]
		+/SPRITES: pygame.sprite.Group
		+add_text() None
		+add_button() None
		+press_buttons() Control | None
	}
	class Text {
		-get_max_point_size() int
	}
	class Button {
		-CALLBACK: Callable[[], Control]
		+update() Control | None
	}
	class Frame {
		-FIXED_DT: float
		-MAX_DT: float
		-MAX_FPS: int
		-screen_size: tuple[int, int]
		-SCREEN: pygame.Surface
		-CLOCK: pygame.Clock
		-RENDER_GROUPS: list[pygame.sprite.Group]
		-dt: float
		-fixed_steps: float
		+dt() float
		+FIXED_DT() float
		+fixed_steps() float
		+screen_size() Vector2
		+next() None
		+render() None
		+add_sprite_group() None
		+remove_sprite_group() None
		+clear_sprite_group() None
	}
	class BasicSprite {
		-transform: Transform
		+/size: Vector2
		+/pos: Vector2
		+/edge_offset: Vector2
		+/topleft: Vector2
		+/botright: Vector2
		+/screen_size: Vector2
		+/FIXED_DT: float
		#set_center() None
		#move_to() None
		#move_by() None
		-rescale() None
		#set_size() None
		#set_image() None
		#load_image() None
		+overlap() bool
		+update() None
		+fixed_update() None
	}
	class Command {
		<<enum>>
		WAIT
		OPEN_MENU
		SWITCH_UI
		OPEN_LEVEL
		RESTART_LEVEL
		CLOSE_LEVEL
		CLOSE_GAME
	}
	class Control {
		+command: Command
		+parameter: Any
		+wait() Control
		+open_menu() Control
		+switch_ui() Control
		+open_level() Control
		+restart_level() Control
		+close_level() Control
		+close_game() Control
	}
	class PhysicsSystem {
		-VELOCITY: Vector2
		-GRAVITY: float
		-JUMP: Jump_info
		-DASH: Dash_info
		-SPEED: float
		-dir: float
		+/on_ground: bool
		+apply_diff() None
		+collide() None
		+apply_grav() None
		+run() None
		+dash() None
		+jump() None
		+move() Vector2
	}
	class InterpolationSystem {
		-last_pos: Vector2
		+update_last_pos() None
		+interpolate_pos() Vector2
	}
	class Interpolatable {
		<<Interface>>
		+interpolate_sprite_pos()
	}
```
## Полная
```mermaid
---
title: UML class diagram
config:
  layout: elk
  fontSize: 20
  elk:
    lineHops: false
  class:
    hideEmptyMembersBox: true
---
classDiagram
	GAME --* Frame
	GAME --* UI
	GAME --* Level
	GAME --o Control
	Level --* Tilemap
	Level --* Player
	Level --* Collectable
	Level --* MovingCollectable
	Level --* Finish
	Level ..> Control
	Player --|> BasicSprite
	Player --* PhysicsSystem
	Player --o InterpolationSystem
	Player ..> Tilemap
	Player ..> Jump_params
	Player ..> Dash_params
	Player ..|> Interpolatable
	Tilemap --o BasicSprite
	Finish --|> BasicSprite
	Finish ..> BasicSprite
	Collectable --|> BasicSprite
	Collectable ..> BasicSprite
	MovingCollectable --|> Collectable
	MovingCollectable --o InterpolationSystem
	MovingCollectable ..|> Interpolatable
	UI --* UIScreen
	UIScreen --* Text
	UIScreen --* Button
	Text --|> BasicSprite
	Button --|> BasicSprite
	Button ..> Control
	BasicSprite --|> pygame.sprite.Sprite
	BasicSprite --* Transform
	BasicSprite ..> Frame
	Control --* Command
	PhysicsSystem --* Jump_info
	PhysicsSystem --* Dash_info
	PhysicsSystem --* Player_diff
	PhysicsSystem ..> BasicSprite
	class GAME {
		-active: bool
		-FRAME: Frame
		-UI: UI
		-level: Level
		-control: Control
		+active() bool
		+init() None
		+start(start_menu: UIScreen) None
		+set_command(command: Control) None
		+execute_command() None
		+update() None
		+next_frame() None
		-start_level_from_file(level_name: str) None
		-start_level(generator: Callable[[Level], None], tilemap_size: Vector2) None
		-close_level() None
		-reset_level() None
		-open_main_menu() None
		-close_game() None
	}
	class Level {
		-DEF_LEVEL_SIZE: Vector2
		-DEF_TILEMAP_LAYERS: list[str]
		-SPRITES: pygame.sprite.Group
		-GENERATOR: Callable[[Level], None]
		-TILEMAP: Tilemap
		-OBJECTS: list[type[BasicSprite]]
		-COLLECTABLES: list[type[Collectable]]
		-FINISHES: list[type[Finish]]
		-PLAYER: Player
		-command: Control
		+/SPRITES: pygame.sprite.Group
		+/TILEMAP_SPRITES: pygame.sprite.Group
		+/TILEMAP_SIZE: Vector2
		+/GENERATOR: Callable[[Level], None]
		+/command: Control
		+parse_level(level_struct: dict[str, Any]) Callable[[Level], None]
		-build_level() None
		-set_command(command: Control) None
		+logic(fixed_steps: int) None
		+add_ground_tile(sprite_path: str, tile_pos: Vector2) None
		+add_hazard_tile(sprite_path: str, tile_pos: Vector2) None
		+add_player(sprite_path: str, transform: Transform, jump: Jump_params, dash: Dash_params) None
		+add_finish(sprite_path: str, transform: Transform) None
		+add_static_item(sprite_path: str, transform: Transform, diff: Player_diff) None
		+add_moving_item(sprite_path: str, transform: Transform, diff: Player_diff, speed: float, destination: Vector2) None
		-collect_items() None
	}
	class Player {
		-PHYSICS: PhysicsSystem
		-TILEMAP: Tilemap
		-INTERPOLATOR: InterpolationSystem
		-dead: bool
		+/dead: bool
		+death_check() None
		+apply_diff(diff: chacracter_diff) None
	}
	class Tilemap {
		-SIZE: Vector2
		-TILESIZE: Vector2
		-SPRITES: pygame.sprite.Group
		-LAYERS: list[list[BasicSprite]]
		+/SIZE: Vector2
		+/SPRITES: pygame.sprite.Group
		-convert_to_screen(pos: Vector2): Vector
		-convert_to_tilemap(pos: Vector2): Vector
		+add_layer(layer_name: str) None
		+get_layer(layer_name: str, pseudo_border: bool) list[BasicSprite]
		+add_tile(sprite_path: str, layer_name: str, tile_pos: Vector2) None
		+get_tile(layer_name: str, tile_pos: Vector2, pseudo_tile: bool) BasicSprite | None
		+collides(layer_name: str, object: type[BasicSprite], pseudo_tiles: bool) list[BasicSprite]
	}
	class Finish {
		-PLAYER: type[BasicSprite]
		-finished: bool
		+/finished: bool
	}
	class Collectable {
		-DIFF: Player_diff
		-is_collected: bool
		-PLAYER: type[BasicSprite]
		+/DIFF: Player_diff
		+/is_collected: bool
	}
	class MovingCollectable {
		-SPEED: float
		-START: Vector2
		-DESTINATION: Vector2
		-DIR: Vector2
		-to_end: bool
		-INTERPOLATOR: InterpolationSystem
	}
	class UI {
		-start_menu: UIScreen
		-current_screen: UIScreen
		+/SPRITES: pygame.sprite.Group | None
		+set_start_menu(start_menu: UIScreen) None
		+open_start_menu() None
		+switch_ui(screen: UIScreen) None
		+clear_ui() None
		+press_buttons() Control
	}
	class UIScreen {
		-SPRITES: pygame.sprite.Group
		-BUTTONS: list[Button]
		+/SPRITES: pygame.sprite.Group
		+add_text(text: str, transform: Transform) None
		+add_button(sprite_path: str, transform: Transform, callback: Callable[[], Control]) None
		+press_buttons() Control | None
	}
	class Text {
		-get_max_point_size(text: str, max_size: Vector2) int
	}
	class Button {
		-CALLBACK: Callable[[], Control]
		+update() Control | None
	}
	class Frame {
		-FIXED_DT: float
		-MAX_DT: float
		-MAX_FPS: int
		-screen_size: tuple[int, int]
		-SCREEN: pygame.Surface
		-CLOCK: pygame.Clock
		-RENDER_GROUPS: list[pygame.sprite.Group]
		-dt: float
		-fixed_steps: float
		+dt() float
		+FIXED_DT() float
		+fixed_steps() float
		+screen_size() Vector2
		+next() None
		+render() None
		+add_sprite_group(group: pygame.sprite.Group) None
		+remove_sprite_group(group: pygame.sprite.Group) None
		+clear_sprite_group() None
	}
	class BasicSprite {
		-transform: Transform
		+/size: Vector2
		+/pos: Vector2
		+/edge_offset: Vector2
		+/topleft: Vector2
		+/botright: Vector2
		+/screen_size: Vector2
		+/FIXED_DT: float
		#set_center(pos: Vector2) None
		#move_to(new_pos: Vector2) None
		#move_by(offset: Vector2) None
		-rescale() None
		#set_size(new_size: Vector2) None
		#set_image(image: pygame.Surface) None
		#load_image(sprite_path: str | None) None
		+overlap(other: type[BasicSprite]) bool
		+update() None
		+fixed_update() None
	}
	class Command {
		<<enum>>
		WAIT
		OPEN_MENU
		SWITCH_UI
		OPEN_LEVEL
		RESTART_LEVEL
		CLOSE_LEVEL
		CLOSE_GAME
	}
	class Control {
		+command: Command
		+parameter: Any
		+wait() Control
		+open_menu() Control
		+switch_ui(screen: UIScreen) Control
		+open_level(level_name: str) Control
		+restart_level() Control
		+close_level() Control
		+close_game() Control
	}
	class Transform {
		<<dataclass>>
		+size: Vector2
		+pos: Vector2
	}
	class Jump_info {
		<<dataclass>>
		+on_ground: bool
		+force: int
		+air_jumps: int
		+def_air_jumps: int
	}
	class Dash_info {
		<<dataclass>>
		+is_active: bool
		+speed: float
		+distance: float
		+left: float
		+count: int
		+def_count: int
	}
	class Player_diff {
		<<dataclass>>
		+air_jumps: int
		+def_air_jumps: int
		+dashes: int
		+def_dashes: int
	}
	class Jump_params {
		<<dataclass>>
		+dist: float
		+height: float
		+time: float
	}
	class Dash_params {
		<<dataclass>>
		+dist: float
		+time: float
	}
	class PhysicsSystem {
		-VELOCITY: Vector2
		-GRAVITY: float
		-JUMP: Jump_info
		-DASH: Dash_info
		-SPEED: float
		-dir: float
		+/on_ground: bool
		+apply_diff(diff: Player_diff) None
		+collide(obj: type[BasicSprite], ground: TilemapLayer) None
		+apply_grav() None
		+run(dir: float) None
		+dash() None
		+jump() None
		+move() Vector2
	}
	class InterpolationSystem {
		-last_pos: Vector2
		+update_last_pos(pos: Vector2) None
		+interpolate_pos(pos: Vector2) Vector2
	}
	class Interpolatable {
		<<Interface>>
		+interpolate_sprite_pos()
	}
```
