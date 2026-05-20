import pygame
from Classes import GAME

pygame.init()
GAME.init.level(1)
GAME.init.player("Assets/Char.png", (3, 6), 5)

for i in range(6):
    GAME.add.ground_tile("Assets/Block.png", (i, 8))
for i in range(3):
    GAME.add.ground_tile("Assets/Block.png", (0, 5+i))
for i in range(6):
    GAME.add.ground_tile("Assets/Block.png", (i, 4))
GAME.add.ground_tile("Assets/Block.png", (2, 6))

while GAME.is_running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            GAME.is_running = False

    GAME.level.logic()
    GAME.frame.render()
    GAME.frame.next()

pygame.quit()