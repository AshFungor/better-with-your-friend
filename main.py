import pathlib
import sys

import pygame

from game import *
from network_utils import Client, Server


def redirect(return_value):
    if return_value is None:
        single_game()
        exit(0)
    if isinstance(return_value, Client):
        client_game(return_value)
        exit(0)
    if isinstance(return_value, Server):
        host_game(return_value)
        exit(0)


if __name__ == '__main__':

    curr_path = str(pathlib.Path().resolve())
    sys.path.append(curr_path + '/network_utils')

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    menu = StartMenu()
    clock = pygame.time.Clock()
    run = True
    while run:
        delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            menu = menu.process_event(event)
            redirect(menu)
        menu = menu.loop(delta, background)
        redirect(menu)
        pygame.display.update()
