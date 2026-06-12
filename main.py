import pygame
from pygame import Vector2
from Game import Game_manager
from Objects import character_diff as diff
from UI import UI_Screen

def test_level(game: Game_manager):
    level = game.level
    level.add_character("Assets/Char.png", Vector2(3.5, 6.5), 5)
    for i in range(6):
        level.add_ground_tile("Assets/Block.png", (i, 8))
    for i in range(3):
        level.add_ground_tile("Assets/Block.png", (0, 5+i))
    for i in range(6):
        level.add_ground_tile("Assets/Block.png", (i, 4))
    level.add_ground_tile("Assets/Block.png", (2, 6))
    level.add_ground_tile("Assets/Block.png", (7, 8))
    level.add_hazard_tile("Assets/HazardBlock.png", (2, 5))
    level.add_hazard_tile("Assets/HazardBlock.png", (5, 7))

    # level.add_static_collectable("Assets/CharBlock.png", Vector2(7.5, 8.5), diff(0, 1, 0, 1))
    level.add_static_collectable("Assets/CharBlock.png", Vector2(10.5, 8.5), diff(0, 1, 0, 1))
    level.add_dynamic_collectable("Assets/CharBlock.png", Vector2(12.5, 8.5), diff(1, 0, 1, 0), 5, Vector2(12.5, 0.5))

def close_game(game: Game_manager) -> None:
    game.close_game()

def start_level(game: Game_manager) -> None:
    game.start_level_from_file("Levels/test_level.json")

pygame.init()
GAME = Game_manager()
menu = UI_Screen(GAME)
menu.add_button("CharBlock.png", Vector2(25, 20), Vector2(50, 20), start_level)
menu.add_button("HazardBlock.png", Vector2(25, 60), Vector2(50, 20), close_game)
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
