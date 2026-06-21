import os
from math import ceil
import pygame
from pygame import Vector2
from Game import Game_manager
from UI import UI_Screen

def close_game(game: Game_manager) -> None:
    game.close_game()

def load_level(level_path: str) -> function:
    def start_level(game: Game_manager):
        try:
            game.start_level_from_file(level_path)
        except RuntimeError:
            pass
    return start_level

def level_selection(game: Game_manager) -> UI_Screen:
    files = os.listdir("Levels")
    files = list(filter(lambda file: file.endswith(".json"), files))
    rows = 3
    cols = 5
    levels_per_page = cols * (rows -1 )
    pages_count = max(1, ceil(len(files) / levels_per_page))
    size = Vector2(10, 10 * 16 / 9)
    gap = Vector2((100 - size.x * cols) / (cols + 1), (100 - size.y * rows) / (rows + 1))
    pages: list[UI_Screen] = []
    for page in range(pages_count):
        pages.append(UI_Screen(GAME))
        for level_number in range(min(10, len(files) - page * levels_per_page)):
            level = level_number + page * levels_per_page
            row = level_number // cols
            col = level_number - row * cols
            pos = gap + size / 2 + Vector2(col * (size.x + gap.x), row * (size.y + gap.y))
            pages[page].add_button("", pos, size, load_level(files[level]))
            pages[page].add_button("", Vector2(50 - size.x / 2, gap.y + (rows - 1) * (size.y + gap.y)), size, switch_to(game.UI.start_menu, game))
            level_name = files[level].replace(".json", "")
            pages[page].add_text(level_name, Vector2(pos.x, pos.y + size.y / 2 + gap.y / 4), Vector2(size.x + gap.x / 2, gap.y / 2))
    if(pages_count > 1):
        for page in range(len(pages)):
            if(page < len(pages) - 1):
                pages[page].add_button("", Vector2(gap.x + (cols - 1) * (size.x + gap.x), gap.y + (rows - 1) * (size.y + gap.y)), size, switch_to(pages[page+1], game))
            if(page > 0):
                pages[page].add_button("", Vector2(gap.x, gap.y + (rows - 1) * (size.y + gap.y)), size, switch_to(pages[page-1], game))
    return pages[0]

def open_level_selection(game: Game_manager) -> None:
    game.UI.switch_ui(level_selection(game))

def switch_to(ui: UI_Screen, game: Game_manager):
    def change(game: Game_manager):
        game.UI.switch_ui(ui)
    return change

pygame.init()
GAME = Game_manager()
menu = UI_Screen(GAME)
menu.add_button("CharBlock.png", Vector2(50, 30), Vector2(50, 20), open_level_selection)
menu.add_button("HazardBlock.png", Vector2(50, 70), Vector2(50, 20), close_game)
GAME.start(menu)

while GAME.is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GAME.close_game()
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if(keys[pygame.K_ESCAPE]):
                GAME.close_level()
            if(keys[pygame.K_END]):
                GAME.close_game()

    if(GAME.UI.ui != None):
        GAME.UI.press_buttons()
    if(GAME.level != None):
        GAME.level.logic()
    GAME.FRAME.render()
    GAME.FRAME.next()

pygame.quit()
