import pygame
import sys
pygame.init()
win = pygame.display.set_mode((1200,800))
pygame.display.set_caption("Ходилка-Бродилка")
player = pygame.image.load("luigi.png")
clock = pygame.time.Clock()

x = 100
y = 100
speed = 10




run = True
while (run):
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed

    win.blit( player, (x, y))
    pygame.display.update()


pygame.quit()
