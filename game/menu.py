import typing

import pygame
import pygame_gui

from network_utils import Server, Client, HOST, PORT
from .player import SCREEN_HEIGHT, SCREEN_WIDTH

"""
Файл с классами меню.
"""


class HostMenu:
    """
    Меню хоста игры.
    """

    def __init__(self) -> 'HostMenu':
        """
        Единственный конструктор рисует label с информацией о хосте
        и кнопку начала игры.
        """

        pygame.init()
        lbl_text = f'ожидание игрока... хост: {HOST}, порт: {PORT}'

        self.__server = Server()
        self.__state = 0
        self.__surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__ui_manager = pygame_gui.ui_manager.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__info_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 250), (500, 50)),
                                                        text=lbl_text,
                                                        manager=self.__ui_manager)
        self.__start_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 250 + 50 + 25), (200, 50)),
            text='начать',
            manager=self.__ui_manager)
        self.__start_game_button.disable()

    # вспомогательный метод
    def __update_status(self) -> None:

        self.__start_game_button.enable()
        self.__info_label.set_text('игрок присоединился!')
        self.__state = 1

    def process_event(self, event: pygame.event.Event) -> typing.Union['HostMenu', Server]:
        """
        Метод обработки событий меню.

        Args:
            event (Event): событие для обработки

        Returns:
            текущий экземпляр HostMenu или переходное значение
        """

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.__start_game_button:
                return self.__server

        self.__ui_manager.process_events(event)
        return self

    def loop(self, delta: float, parent_surface: pygame.surface.Surface) -> 'HostMenu':
        """
        Метод обновления меню.

        Args:
            delta (float): дельта времени для стабилизации FPS
            parent_surface (Surface): поверхность для наложения UI меню

        Returns:
            текущий экземпляр HostMenu
        """

        self.__server.loop(timeout=delta)
        if self.__server.connected and not self.__state:
            self.__update_status()
        self.__surface.blit(parent_surface, (0, 0))
        self.__ui_manager.update(delta)
        self.__ui_manager.draw_ui(self.__surface)
        return self


class ClientMenu:
    """
    Меню клиента хоста.
    """

    def __init__(self) -> 'ClientMenu':
        """
        Единственный конструктор рисует label, два поля
        для ввода порта и имени хоста и одну кнопку для
        подключения.
        """

        pygame.init()
        lbl_text = 'введите IP адрес хоста и порт для подключения'

        self.__client = None
        self.__state = 0
        self.__surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__ui_manager = pygame_gui.ui_manager.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__info_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 150), (500, 50)),
                                                        text=lbl_text,
                                                        manager=self.__ui_manager)
        self.__host_input = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((350, 150 + 50 + 25), (200, 50)),
            manager=self.__ui_manager)
        self.__port_input = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((350, 150 + 50 + 25 + 50 + 25), (200, 50)),
            manager=self.__ui_manager)
        self.__ask_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((350, 150 + 50 + 25 + 50 + 25 + 50 + 50), (200, 50)),
            text='подключиться',
            manager=self.__ui_manager)
        self.__ask_button.disable()

    def process_event(self, event: pygame.event.Event) -> 'ClientMenu':
        """
        Метод обработки событий меню.

        Args:
            event (Event): событие для обработки

        Returns:
            текущий экземпляр ClientMenu
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.__ask_button:
                try:
                    self.__client = Client(self.__host_input.get_text(),
                                           int(self.__port_input.get_text()))
                    self.__client.loop()
                    self.__state = 1
                    self.__info_label.set_text('ожидание хоста...')
                except ConnectionError:
                    self.__port_input.clear()
                    self.__host_input.clear()
                    self.__ask_button.disable()
                    self.__info_label.set_text('соединение не удалось')

        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if len(self.__host_input.get_text()) > 0 and len(self.__port_input.get_text()) > 0:
                self.__ask_button.enable()

        self.__ui_manager.process_events(event)
        return self

    def loop(self, delta, parent_surface) -> typing.Union['ClientMenu', Client]:
        """
        Метод обновления меню.

        Args:
            delta (float): дельта времени для стабилизации FPS
            parent_surface (Surface): поверхность для наложения UI меню

        Returns:
            текущий экземпляр ClientMenu или переходное значение
        """
        if self.__state != 0:
            self.__client.loop(timeout=delta)
            if self.__client.state == 1:
                return self.__client
        self.__surface.blit(parent_surface, (0, 0))
        self.__ui_manager.update(delta)
        self.__ui_manager.draw_ui(self.__surface)
        return self


class StartMenu:
    """
    Базовое меню, которое вызывается при старте скрипта.
    """

    def __init__(self) -> 'StartMenu':
        """
        Единственный конструктор класса создает
        в окне три кнопки-перехода, одна из
        которых начинает однопользовательскую игру,
        другие две - ведут к меню многопользовательской
        игры.
        """

        pygame.init()

        self.__surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__ui_manager = pygame_gui.ui_manager.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__start_single_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 275), (200, 50)),
                                                                  text='начать',
                                                                  manager=self.__ui_manager)
        self.__begin_session_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 275 + 50 + 25), (200, 50)),
            text='создать сервер',
            manager=self.__ui_manager)
        self.__join_session_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 275 + 50 + 25 + 50 + 25), (200, 50)),
            text='присоединиться',
            manager=self.__ui_manager)

    def process_event(self, event: pygame.event.Event) -> typing.Union[None, 'StartMenu', ClientMenu, HostMenu]:
        """
        Метод обработки событий меню.

        Args:
            event (Event): событие для обработки

        Returns:
            текущий экземпляр StartMenu или переходное значение
        """

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.__start_single_button:
                return None
            if event.ui_element == self.__join_session_button:
                return ClientMenu()
            if event.ui_element == self.__begin_session_button:
                return HostMenu()

        self.__ui_manager.process_events(event)
        return self

    def loop(self, delta: float, parent_surface: pygame.surface.Surface) -> 'StartMenu':
        """
        Метод обновления меню.

        Args:
            delta (float): дельта времени для стабилизации FPS
            parent_surface (Surface): поверхность для наложения UI меню

        Returns:
            текущий экземпляр StartMenu
        """

        self.__surface.blit(parent_surface, (0, 0))
        self.__ui_manager.update(delta)
        self.__ui_manager.draw_ui(self.__surface)
        return self
