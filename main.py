import pygame
from pygame import Vector2
from Game import Game_manager
from Objects import character_diff as diff

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



pygame.init()
GAME = Game_manager()
GAME.start_level(test_level, 1)

while GAME.is_running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            GAME.close_game()

    GAME.level.logic()
    GAME.FRAME.render()
    GAME.FRAME.next()

pygame.quit()
