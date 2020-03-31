import curses
import time
from enum import Enum
from typing import Tuple, Optional
from random import randint
from abc import ABC, abstractmethod

class Widget(ABC):
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def draw_rect(self, top_left, dimensions, inner_text=None):
        bottom_left = (top_left[0] + dimensions[0], top_left[1])

        # Draw top line
        self.stdscr.addstr(*top_left, f'/{"$" * (dimensions[1]-1)}')

        # Draw bottom lines
        self.stdscr.addstr(*bottom_left, f'|{"_" * (dimensions[1]-3)} /')

        # Draw the vertical lines
        for i in range(top_left[0] + 1, bottom_left[0]):
            if i == bottom_left[0] - 1:
                self.stdscr.addstr(bottom_left[0] - 1, bottom_left[1], f'|$${"_" * (dimensions[1] - 6)}|$$')
            else:
                self.stdscr.addstr(i, top_left[1], f'|$${" " * (dimensions[1]-6)}|$$')

        if inner_text:
            # TODO: improve centering algo
            text_pos = tuple(map(int, map(sum, zip(top_left, (dimensions[0]/3, dimensions[1]/3)))))
            self.stdscr.addstr(*text_pos, inner_text)

    @abstractmethod
    def draw(self):
        pass


class MainMenu(Widget):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self.hovering_button = 1
        self.chosen_button = None

    def draw(self):
        # Read the text from a file
        main_menu_file_path = './assets/word_art/main_menu.txt'
        with open(main_menu_file_path) as f:
            main_menu_art = f.readlines()

        # Draw the main title
        for i, line in enumerate(main_menu_art):
            self.stdscr.addstr(i, 0, line, curses.color_pair(1))

        # Draw the game options
        play_button_location = (len(main_menu_art) + 2, 1)
        settings_button_location = (len(main_menu_art) + 2, 34)
        self.draw_rect(top_left=play_button_location, dimensions=(3, 25), inner_text='Play')
        self.draw_rect(top_left=settings_button_location, dimensions=(3, 25), inner_text='Settings')

        self.stdscr.refresh()


class CursesGameEngine:
    class GameState(Enum):
        UNKNOWN = 0
        MAIN_MENU = 1
        SETTING = 2

    def __init__(self):
        # Hide the cursor
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)

        curses.curs_set(False)
        curses.noecho()
        curses.cbreak()

        # Init the colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

        # The current game state
        self.game_state = self.GameState.UNKNOWN

    def play(self):
        main_menu = MainMenu(self.stdscr)
        main_menu.draw()
        while not main_menu.chosen_button:
            pass

    def __del__(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        self.stdscr.keypad(False)


class Controller:
    def __init__(self):
        pass

class Snake:
    FRAMERATE = 6
    SNAKE_CHAR = '#'
    FOOD_CHAR = '*'

    def __init__(self):
        self.snake = [(0, 0)]
        self.food = None
        self.stdscr = None
        self.facing = 'right'
        self.score = 0

    # Do all the initializing of settings
    def create_screen(self):
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)

    @staticmethod
    def _add_tuples(*args: Optional[Tuple[int, ...]]) -> Tuple[int, ...]:
        return tuple(map(sum, zip(*args)))

    def _update_logic(self):
        # Coordinates are (y, x)
        keypress_movement_mapping = {
            curses.KEY_LEFT: 'left',
            curses.KEY_RIGHT: 'right',
            curses.KEY_UP: 'up',
            curses.KEY_DOWN: 'down'
        }

        directional_mapping = {
            'left': (0, -1),
            'right': (0, 1),
            'up': (-1, 0),
            'down': (1, 0)
        }

        if not self.food:
            self.food = (randint(0, curses.LINES - 1), randint(0, curses.COLS - 1))

        input_val = keypress_movement_mapping.get(self.stdscr.getch(), None)
        if input_val:
            self.facing = input_val

        head = self.snake[-1]
        new_pos = self._add_tuples(head, directional_mapping[self.facing])

        # Try not to run off screen
        if 0 <= new_pos[0] < curses.LINES and 0 < new_pos[1] <= curses.COLS:
            self.snake.append(new_pos)
            self.snake.pop(0)
        else:
            return False

        if head == self.food:
            self.snake.insert(0, self.snake[0])
            self.food = (randint(0, curses.LINES - 1), randint(0, curses.COLS - 1))

        return True

    def _draw_screen(self):
        self.stdscr.clear()
        for square in self.snake:
            if square:
                self.stdscr.addch(*square, self.SNAKE_CHAR)

        self.stdscr.addch(*self.food, self.FOOD_CHAR)

    def play(self):
        try:
            self.create_screen()
            playing = True
            while playing:
                playing = self._update_logic()
                self._draw_screen()
                self.stdscr.refresh()
                time.sleep(self.FRAMERATE ** -1)
        finally:
            self.close_screen()

    def close_screen(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()


# if __name__ == '__main__':
engine = CursesGameEngine()
engine.play()
print('Done')
