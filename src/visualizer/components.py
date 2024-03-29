import tkinter as tk
from typing import (
    Dict,
    List,
    Tuple,
    Optional
)
from dataclasses import (
    field,
    dataclass
)
from threading import (
    Event,
    Thread
)

import settings

logger = settings.getLogger(__name__)


@dataclass
class Grid:
    width: int
    height: int

    start: Tuple[int, int]
    goal: Tuple[int, int]
    barriers: List[Tuple[int, int]] = field(default_factory=list)
    increased_cost_cells: Dict[Tuple[int, int], int] = field(default_factory=dict)

    def is_goal_state(self, node: 'Node') -> bool:
        """
        Check if the current Node state is the goal state.
        """
        return node.state == self.goal

    def get_neighbors(self, node: 'Node') -> List['Node']:
        """
        Returns the given Node's neighbors against the grid size and barriers.
        """
        directions = [
            (0, -1),  # Up
            (1, 0),   # Right
            (0, 1),   # Down
            (-1, 0)   # Left
        ]
        x, y       = node.state
        neighbors  = []

        for dir_x, dir_y in directions:
            new_x = x + dir_x
            new_y = y + dir_y

            if (0 <= new_x < self.width) and (0 <= new_y < self.height):
                if (new_x, new_y) not in self.barriers:
                    new_cost = node.cost + self.increased_cost_cells.get((new_x, new_y), 1)
                    neighbors.append(Node(state=(new_x, new_y), parent=node, cost=new_cost))

        return neighbors

    def print_grid_cli(self, current_position=None, path=None):
        print("+" + "-" * (self.width * 2) + "+")

        for y in range(self.height):
            print("|", end="")

            for x in range(self.width):
                if (x, y) == self.start:
                    print("S", end=" ")
                elif (x, y) == self.goal:
                    print("G", end=" ")
                elif (x, y) in self.barriers:
                    print("#", end=" ")
                elif (x, y) in self.increased_cost_cells:
                    print("$", end=" ")
                elif path and (x, y) in path:
                    print(".", end=" ")
                elif current_position and (x, y) == current_position:
                    print("X", end=" ")
                else:
                    print("-", end=" ")

            print("|")

        print("+" + "-" * (self.width * 2) + "+")


class GridGUI:

    def __init__(self, grid, search_class):
        self.grid = grid
        self.search_class = search_class
        self.window = tk.Tk()
        self.window.title("Search Algorithm Visualizer")

        self.window.protocol('WM_DELETE_WINDOW', self.on_close)
        self.stop_event = Event()

        self.cell_size = 100
        self.canvas = tk.Canvas(
            self.window,
            width=self.grid.width * self.cell_size,
            height=self.grid.height * self.cell_size
        )
        self.canvas.pack()

        self.click_event = Event()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.draw_grid()

        self.search_class = search_class
        self.search_thread = None

    def on_canvas_click(self, event):
        logger.info('Click at %s, %s', event.x, event.y)

        if self.search_thread is None:
            self.search_thread = Thread(target=self.search_class.run, daemon=True)
            self.search_thread.start()

        self.click_event.set()

    def wait_for_click(self):
        logger.info('Waiting for click event...')

        self.click_event.clear()
        self.click_event.wait()

    def draw_grid(self, path=None, current_position=None):
        self.canvas.delete("all")

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                fill = "white"
                text_color = "black"

                if (x, y) == self.grid.start:
                    fill = "green"
                    text_color = "white"
                elif (x, y) == self.grid.goal:
                    fill = "red"
                    text_color = "white"
                elif (x, y) in self.grid.barriers:
                    fill = "black"
                    text_color = "white"
                elif path and (x, y) in path:
                    fill = "blue"
                    text_color = "white"
                elif current_position and (x, y) == current_position:
                    fill = "orange"
                    text_color = "white"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="gray")
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=f"({x},{y})", fill=text_color)

    def on_close(self):
        self.stop_event.set()
        self.window.destroy()

    def run(self):
        self.window.mainloop()


@dataclass
class Node:
    state: Tuple[int, int]
    parent: Optional['Node']

    cost: int = 0
    depth: int = 0

    def __hash__(self):
        """
        Custom __hash__ method for hashing the state of the Node rather than
        the object.
        """
        return hash(self.state)

    def __eq__(self, other: 'Node'):
        """
        Custom __eq__ method for comparing two Node instances by state.
        """
        if not isinstance(other, Node):
            return TypeError('other must be an instance of Node')

        return self.state == other.state

    def __lt__(self, other: 'Node'):
        """
        Custom __lt__ method for queue.PriorityQueue insert comparisons.
        """
        if not isinstance(other, Node):
            return TypeError('other must be an instance of Node')

        return self.cost < other.cost
