import pygame
from .platform import Platform

BACKGROUND = pygame.image.load('game/assets/bg.jpg')
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Level(object):
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.player = player

    def update(self):
        self.platform_list.update()

    def draw(self, screen):
        screen.blit(BACKGROUND, (0, 0))
        self.platform_list.draw(screen)


class BaseLevel(Level):
    def __init__(self, player):
        Level.__init__(self, player)

        level = [
            [210, 32, 500, 500],
            [210, 32, 150, 400],
            [210, 32, 600, 300],
        ]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)
