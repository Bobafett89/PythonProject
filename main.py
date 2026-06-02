import pygame
from Game import Game_manager

def test_level(game: Game_manager):
    level = game.level
    level.add_character("Assets/Char.png", pygame.Vector2(3.5, 6.5), 5)
    for i in range(6):
        level.add_ground_tile("Assets/Block.png", (i, 8))
    for i in range(3):
        level.add_ground_tile("Assets/Block.png", (0, 5+i))
    for i in range(6):
        level.add_ground_tile("Assets/Block.png", (i, 4))
    level.add_ground_tile("Assets/Block.png", (2, 6))
    level.add_hazard_tile("Assets/HazardBlock.png", (2, 5))
    level.add_hazard_tile("Assets/HazardBlock.png", (5, 7))


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
