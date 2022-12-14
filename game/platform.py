import pygame


class Platform(pygame.sprite.Sprite):

    def __init__(self, width, height):

        super().__init__()
        self.image = pygame.image.load('game/assets/platform.png')
        self.rect = self.image.get_rect()
