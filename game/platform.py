import pygame


class Platform(pygame.sprite.Sprite):
    """Класс, описывающий платформу"""

    def __init__(self):
        """Инициализирует платформу"""
        super().__init__()
        self.image = pygame.image.load('game/assets/platform.png')
        self.rect = self.image.get_rect()
