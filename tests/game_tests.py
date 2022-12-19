import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock

from game.player import Player, SCREEN_HEIGHT


@patch("pygame.image")
class PlayerTests(unittest.TestCase):

    def test_grav(self, img):
        img.load = Mock()
        test_img = Mock()
        test_img.image.get_rect = Mock()
        img.load.return_value = test_img
        test_rect = SimpleNamespace(height=0, y=SCREEN_HEIGHT + 100, x=0)
        test_img.get_rect.return_value = test_rect
        player = Player()
        player.change_y = 1
        player.calc_grav()
        assert player.change_y == 0
        assert player.rect.y == SCREEN_HEIGHT
