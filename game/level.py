import pygame
from .platform import Platform
from .player import Player, AnotherPlayer
from .player import SCREEN_HEIGHT, SCREEN_WIDTH, BACKGROUND


class Level(object):
    def __init__(self, player):
        """Функция создающая группы спрайтов, игркор тоже будет в ней
        """
        self.platform_list = pygame.sprite.Group()
        self.player = player

    def update(self):
        """Функция, которая обновляет экран"""
        self.platform_list.update()

    def draw(self, screen):
        """Функция, рисующая все платформы на экране"""
        screen.blit(BACKGROUND, (0, 0))
        self.platform_list.draw(screen)


class BaseLevel(Level):
    """Класс, описывающий расположение платформ"""
    def __init__(self, player):
        """Функция, отвечающая за расположение платформ в окне, можно менять конфигурацию платформ
        на вход подаются данные player"""
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


class MultiplayerLevel(Level):
    """Класс, описывающий расположение платформ"""
    def __init__(self, player):
        """Функция, отвечающая за расположение платформ в окне, можно менять конфигурацию платформ
        на вход подаются данные player"""
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

        second = AnotherPlayer()
        self.platform_list.add(second)
        self.another_player = second

