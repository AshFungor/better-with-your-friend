import pygame
from .level import SCREEN_HEIGHT, SCREEN_WIDTH


class Player(pygame.sprite.Sprite):
    right = True

    def __init__(self):

        super().__init__()

        self.image = pygame.image.load('game/assets/luigi.png')

        self.rect = self.image.get_rect()

        self.change_x = 0
        self.change_y = 0

    def update(self):

        self.calc_grav()

        self.rect.x += self.change_x

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)

        for block in block_hit_list:

            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:

                self.rect.left = block.rect.right

        self.rect.y += self.change_y

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:

            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            self.change_y = 0

    def calc_grav(self):

        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .95

        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        self.rect.y += 10
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 10

        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -16

    def go_left(self):
        self.change_x = -9
        if self.right:
            self.flip()
            self.right = False

    def go_right(self):
        self.change_x = 9
        if not self.right:
            self.flip()
            self.right = True

    def stop(self):
        self.change_x = 0

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)
