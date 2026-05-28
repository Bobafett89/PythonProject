import pygame
from Classes import GAME

def test_level():
    GAME.init.player("Assets/Char.png", pygame.Vector2(3.5, 6.5), 5)
    for i in range(6):
        GAME.add.ground_tile("Assets/Block.png", (i, 8))
    for i in range(3):
        GAME.add.ground_tile("Assets/Block.png", (0, 5+i))
    for i in range(6):
        GAME.add.ground_tile("Assets/Block.png", (i, 4))
    GAME.add.ground_tile("Assets/Block.png", (2, 6))
    GAME.add.hazard_tile("Assets/HazardBlock.png", (2, 5))
    GAME.add.hazard_tile("Assets/HazardBlock.png", (5, 7))


pygame.init()
GAME.init.level(1, test_level)

while GAME.is_running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            GAME.is_running = False

    GAME.level.logic()
    GAME.frame.render()
    GAME.frame.next()

pygame.quit()
