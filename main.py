from game import game
import pathlib
import sys


if __name__ == '__main__':

    curr_path = str(pathlib.Path().resolve())
    sys.path.append(curr_path + '/network_utils')
    game()

