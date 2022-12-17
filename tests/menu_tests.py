from game.menu import StartMenu, HostMenu
import pygame
import unittest


class MenuTests(unittest.TestCase):

    def test_events_processed(self):

        background = pygame.Surface((800, 600))
        background.fill(pygame.Color('#000000'))

        menu = StartMenu()
        clock = pygame.time.Clock()
        run = True
        skip = False
        while run:
            delta = clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                menu = menu.process_event(event)
            menu = menu.loop(delta, background)
            pygame.display.update()
