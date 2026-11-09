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
- [ ] Добавить интерполяцию движения

## Модуль 5
- [ ] Сделать FSM для GAME

# Диаграмма классов
```mermaid
---
title: UML class diagram
config:
  layout: elk
  class:
    hideEmptyMembersBox: true
---
classDiagram
	GAME *-- Frame
	GAME *-- UI
	GAME *-- Level
	GAME ..> Control
	UI *-- UIScreen
	Level *-- Tilemap
	Level *-- Character
	Level *-- Finish
	Level *-- Collectable
	Level *-- MovingCollectable
	Level ..> GAME
	UIScreen *-- Button
	UIScreen *-- Text
	Text --|> BasicSprite
	Text ..> GAME
	Button --|> BasicSprite
	Button ..> GAME
	Character --|> BasicSprite
	Character *-- Character_physics_controller
	Character ..> Tilemap
	Character ..> GAME
	Character ..> dash_params
	Character ..> jump_params
	Tilemap *-- TilemapLayer
	TilemapLayer ..> BasicSprite
	Finish --|> BasicSprite
	Finish ..> GAME
	Finish ..> BasicSprite
	Collectable --|> BasicSprite
	Collectable ..> Character
	MovingCollectable --|> Collectable
	MovingCollectable ..> GAME
	BasicSprite --|> pygame.sprite.Sprite
	BasicSprite ..> GAME
	Control ..> Command
	Character_physics_controller ..> character_diff
	Character_physics_controller ..> TilemapLayer
	Character_physics_controller ..> BasicSprite
	Character_physics_controller ..> jump_struct
	Character_physics_controller ..> dash_struct
	class GAME {
		-active: bool
		-FRAME: Frame
		-UI: UI
		-level: Level
		-control: Control
		+active() bool
		+screen_size() Vector2
		+dt() float
		+FIXED_DT() float
		+fixed_steps() int
		+init() None
		+start(start_menu: UI_Screen) None
		+set_command(command: Control) None
		+execute_command() None
		+update() None
		+next_frame() None
		-start_levev_from_file(level_name: str) None
		-start_level(generator: Callable[[Level], None], tilemap_size: Vector2) None
		-close_level() None
		-reset_level() None
		-open_main_menu() None
		-close_game() None
	}
	class UI {
		-start_menu: UI_Screen
		-current_screen: UI_Screen
		+/SPRITES: pygame.sprite.Group | None
		+set_start_menu(start_menu: UI_Screen) None
		+open_start_menu() None
		+switch_ui(screen: UI_Screen) None
		+clear_ui() None
		+press_buttons() None
	}
	class Frame {
		-FIXED_DT: float
		-MAX_DT: float
		-SCREEN: pygame.Surface
		-CLOCK: pygame.Clock
		-RENDER_GROUPS: list[pygame.sprite.Group]
		-dt: float
		-acc_dt: float
		-fixed_steps: int
		+/dt: float
		+/FIXED_DT: float
		+/fixed_steps: int
		+/screen_size: Vector2
		+next() None
		+render() None
		+add_sprite_group(group: pygame.sprite.Group) None
		+remove_sprite_group(group: pygame.sprite.Group) None
		+clear_sprite_group() None
	}
	class Level {
		-DEF_LEVEL_SIZE: Vector2
		-DEF_TILEMAP_LAYERS: list[str]
		-SPRITES: pygame.sprite.Group
		-GENERATOR: Callable[[Level], None]
		-TILEMAP: Tilemap
		-OBJECTS: list[type[BasicSprite]]
		-COLLECTABLES: list[type[Collectable]]
		-PLAYER: Character
		+/SPRITES: pygame.sprite.Group
		+/TILEMAP_SPRITES: pygame.sprite.Group
		+/TILEMAP_SIZE: Vector2
		+/GENERATOR: Callable[[Level], None]
		+parse_level(level_struct: dict) Callable[[Level], None]
		-build_level() None
		+logic() None
		+add_ground_tile(sprite_path: str, tile_pos: Vector2) None
		+add_hazard_tile(sprite_path: str, tile_pos: Vector2) None
		+add_character(sprite_path: str, size: Vector2, pos: Vector2, jump: jump_params, dash: dash_params) None
		+add_finish(sprite_path: str, size: Vector2, pos: Vector2) None
		+add_static_item(sprite_path: str, size: Vector2, pos: Vector2, diff: character_diff) None
		+add_moving_item(sprite_path: str, size: Vector2, pos: Vector2, diff: character_diff, speed: float, destination: Vector2) None
		-collect_items() None
	}
	class UIScreen {
		-SPRITES: pygame.sprite.Group
		-BUTTONS: list[Button]
		+/SPRITES: pygame.sprite.Group
		+add_text(text: str, size: Vector2, pos: Vector2) None
		+add_button(sprite_path: str, size: Vector2, pos: Vector2, callback: Callable[[], None]) None
		+press_buttons() None
	}
	class Text {
		-get_max_point_size(text: str, max_size: Vector2) int
	}
	class Button {
		-CALLBACK: Callable[[], None]
		+update() bool
	}
	class Character {
		-PHYSICS: physics
		-TILEMAP: Tilemap
		+update() None
		+fixed_update() None
		+death_check() None
		+apply_diff(diff: chacracter_diff) None
		-debug() None
	}
	class Tilemap {
		-SIZE: Vector2
		-SPRITES: pygame.sprite.Group
		-LAYERS: dict[TilemapLayer]
		+/SIZE: Vector2
		+/SPRITES: pygame.sprite.Group
		+add_layer(name: str) None
		+get_layer(name: str) TilemapLayer
		+add_tile(sprite_path: str, layer_name: str, tile_pos: Vector2) None
		+get_tile(layer_name: str, tile_pos: Vector2, pseudo_tile: bool) BasicSprite | None
		+collides(layer_name: str, object: type[BasicSprite], pseudo_tiles: bool) list[BasicSprite]
	}
	class TilemapLayer {
		-SIZE: Vector2
		-TILESIZE: Vector2
		-SPRITES: pygame.sprite.Group
		-MAP: list[list[BasicSprite]]
		-convert_to_screen(pos: Vector2) Vector2
		-convert_to_tilemap(pos: Vector2) Vector2
		+add_tile(sprite_path: str, tile_pos: Vector2) None
		+get_tile(tile_pos: Vector2, pseudo_tile: bool) BasicSprite | None
		+collides(object: type[BasicSprite], pseudo_tiles: bool) list[BasicSprite]
	}
	class Finish {
		-CHAR: type[BasicSprite]
		+fixed_update() None
	}
	class Collectable {
		-DIFF: character_diff
		-is_collected: bool
		-CHAR: type[Character]
		+/is_collected: bool
		+fixed_update() None
	}
	class MovingCollectable {
		-SPEED: float
		-START: Vector2
		-DESTINATION: Vector2
		-DIR: Vector2
		-to_end: bool
		+fixed_update() None
	}
	class BasicSprite {
		-size: Vector2
		-pos: Vector2
		+/size: Vector2
		+/pos: Vector2
		+/edge_offset: Vector2
		+/topleft: Vector2
		+/botright: Vector2
		-set_center() None
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
		+switch_ui(screen: UI_Screen) Control
		+open_level(level_name: str) Control
		+restart_level() Control
		+close_level() Control
		+close_game() Control
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
	class jump_params {
		<<dataclass>>
		+dist: float
		+height: float
		+time: float
	}
	class dash_params {
		<<dataclass>>
		+dist: float
		+time: float
	}
	class Character_physics_controller {
		-VELOCITY: Vector2
		-GRAVITY: float
		-JUMP: jump_struct
		-DASH: dash_struct
		-SPEED: float
		-dir: float
		+/on_ground: bool
		+apply_diff(diff: character_diff) None
		+collide(obj: type[BasicSprite], ground: TilemapLayer) None
		+apply_grav() None
		+run(dir: float) None
		+dash() None
		+jump() None
		+move() Vector2
	}
```
