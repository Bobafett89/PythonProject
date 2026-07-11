import pygame
from pygame import Vector2
from Utils import Control, vector2_div, vector2_mult
from Game import Game_manager
from UI import UI_Screen
from os import listdir
from math import ceil

def close_game(game: Game_manager) -> None:
    game.set_command(Control.close_game())

def switch_to(screen: UI_Screen) -> function:
    def change(game: Game_manager):
        game.set_command(Control.switch_ui(screen))
    return change

def load_level(level_path: str) -> function:
    def start_level(game: Game_manager):
        game.set_command(Control.open_level(level_path))
    return start_level

def level_selection(game: Game_manager) -> UI_Screen:
    files = listdir("Levels")
    files = list(filter(lambda file: file.endswith(".json"), files))
    grid = Vector2(5, 3)
    levels_per_page = int(grid.x * (grid.y - 1))
    pages_count = max(1, ceil(len(files) / levels_per_page))
    button_size = Vector2(0.1, 0.1 / 9 * 16)
    gaps = grid + Vector2(1, 1)
    buttons_area = vector2_mult(button_size, grid)
    gap = vector2_div(Vector2(1, 1) - buttons_area, gaps)
    grid_offset = button_size + gap
    text_size = Vector2(button_size.x, 0) + gap / 2
    pages: list[UI_Screen] = []
    def calc_pos(grid_pos: Vector2) -> Vector2:
        return vector2_mult(grid_pos, grid_offset) + gap + button_size / 2
    for page in range(pages_count):
        pages.append(UI_Screen(GAME))
        for level_number in range(min(levels_per_page, len(files) - page * levels_per_page)):
            level = level_number + page * levels_per_page
            grid_pos = Vector2(level_number % grid.x, level_number // grid.x)
            open_pos = calc_pos(grid_pos)
            pages[page].add_button("", open_pos, button_size, load_level(files[level]))

            level_name = files[level].replace(".json", "")
            text_pos = open_pos + Vector2(0, button_size.y / 2 + gap.y / 4)
            pages[page].add_text(level_name, text_pos, text_size)
        return_pos = Vector2(0.5, calc_pos(Vector2(0, grid.y - 1)).y)
        pages[page].add_button("", return_pos, button_size, switch_to(game.UI.start_menu))
    if(pages_count > 1):
        for page in range(len(pages)):
            if(page < len(pages) - 1):
                grid_pos = grid - Vector2(1, 1)
                next_pos = calc_pos(grid_pos)
                pages[page].add_button("", next_pos, button_size, switch_to(pages[page+1]))
            if(page > 0):
                grid_pos = Vector2(0, grid.y - 1)
                back_pos = calc_pos(grid_pos)
                pages[page].add_button("", back_pos, button_size, switch_to(pages[page-1]))
    return pages[0]

def open_level_selection(game: Game_manager) -> None:
    game.set_command(Control.switch_ui(level_selection(game)))

pygame.init()
GAME = Game_manager()
menu = UI_Screen(GAME)
menu.add_button("CharBlock.png", Vector2(0.5, 0.3), Vector2(0.5, 0.2), open_level_selection)
menu.add_button("HazardBlock.png", Vector2(0.5, 0.7), Vector2(0.5, 0.2), close_game)
GAME.start(menu)

while GAME.is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GAME.set_command(Control.close_game())
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if(keys[pygame.K_ESCAPE]):
                GAME.set_command(Control.close_level())
            if(keys[pygame.K_END]):
                GAME.set_command(Control.close_game())

    if(GAME.UI.current_screen != None):
        GAME.UI.press_buttons()
    if(GAME.level != None):
        GAME.level.logic()
    GAME.execute_command()
    GAME.FRAME.render()
    GAME.FRAME.next()

pygame.quit()
