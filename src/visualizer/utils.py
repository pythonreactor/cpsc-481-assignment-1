from typing import (
    Dict,
    List,
    Tuple
)

import settings
from constants import (
    VisualizationMethod,
    UninformedSearchStrategy,
    DEFAULT_GRID_BY_STRATEGY_MAP
)
from components import (
    Grid,
    GridGUI
)
from algorithms import UninformedSearch

logger = settings.getLogger(__name__)


def exit_program():
    """
    Helper function to log and exit the program.
    """
    logger.info('Exiting the program.')
    exit('Goodbye!')


def get_search_strategy() -> UninformedSearchStrategy:
    print('Uninformed Search Algorithms:')
    for idx, strategy in enumerate(UninformedSearchStrategy, start=1):
        print(f'{idx}. {strategy.value}')
    print()

    while True:
        choice = input('Enter a strategy number ("q" to quit): ')
        if choice.lower() == settings.MAIN_EXIT_CHAR:
            exit_program()

        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0:
                raise ValueError

            strategy = list(UninformedSearchStrategy)[choice_idx]

            return strategy
        except (ValueError, IndexError):
            print('Invalid choice. Please try again.')


def get_visualizer_method() -> str:
    print('0. Just run the search algorithm (no visualization)')
    print('1. Command-line interface (CLI)')
    print('2. Graphical user interface (GUI)', end='\n\n')

    while True:
        choice = input('Choose a number ("q" to quit): ')
        if choice.lower() == settings.MAIN_EXIT_CHAR:
            exit_program()

        if choice == '0':
            return VisualizationMethod.Nothing
        elif choice == '1':
            return VisualizationMethod.CLI
        elif choice == '2':
            return VisualizationMethod.GUI
        else:
            print('Invalid choice. Please try again.')


def get_grid(strategy: UninformedSearchStrategy) -> Grid:
    """
    Return a default grid configuration or have the user enter
    the configuration manually.
    """

    def _get_grid_size() -> Tuple[int, int]:
        """
        Get the grid size from the CLI.
        """
        while True:
            grid_size = input('Enter the size of the grid (e.g., 5x5): ')
            if grid_size.lower() == settings.MAIN_EXIT_CHAR:
                exit_program()

            try:
                width, height = map(int, grid_size.split('x'))
                return width, height
            except ValueError:
                print('Invalid input. Please try again.')

    def _get_start_state() -> Tuple[int, int]:
        """
        Get the start state tuple from the CLI.
        """
        while True:
            start_state = input('Enter the start position (e.g., 0,0): ')
            if start_state.lower() == settings.MAIN_EXIT_CHAR:
                exit_program()

            try:
                start_state = tuple(map(int, start_state.split(',')))
                return start_state
            except ValueError:
                print('Invalid input. Please try again.')

    def _get_goal_state() -> Tuple[int, int]:
        """
        Get the goal state tuple from the CLI.
        """
        while True:
            goal_state = input('Enter the goal position (e.g., 4,4): ')
            if goal_state.lower() == settings.MAIN_EXIT_CHAR:
                exit_program()

            try:
                goal_state = tuple(map(int, goal_state.split(',')))
                return goal_state
            except ValueError:
                print('Invalid input. Please try again.')

    def _get_barriers() -> List[Tuple[int, int]]:
        """
        Get the barriers list from the CLI if the user wants to
        add any.
        """
        barriers = []

        add_barriers = input('Would you like to add barriers? (y/n): ')
        if add_barriers.lower() == settings.MAIN_EXIT_CHAR:
            exit_program()

        while add_barriers.lower() == 'y':
            barrier = input('Enter a barrier position (e.g., 2,2), or "done" to finish: ')
            if barrier.lower() == settings.MAIN_EXIT_CHAR:
                exit_program()

            elif barrier.lower() == 'done':
                break

            try:
                barrier = tuple(map(int, barrier.split(',')))
                if barrier in barriers:
                    print("Barrier already exists at this position. Please enter a different position.")
                    continue

                barriers.append(barrier)
                add_barriers = input('Add another barrier? (y/n): ')

            except ValueError:
                print('Invalid input. Please try again.')

        return barriers

    def _get_increased_cost_cells() -> Dict[Tuple[int, int], int]:
        """
        Get the increased cost cells dictionary from the CLI if the user wants to
        add any.
        """
        increased_cost_cells = {}

        add_increased_cost = input('Would you like to add cells with increased cost? (y/n): ')
        if add_increased_cost.lower() == settings.MAIN_EXIT_CHAR:
            exit_program()

        while add_increased_cost.lower() == 'y':
            cell_input = input('Enter a cell position and its cost (e.g., 3,3,5), or "done" to finish: ')
            if cell_input.lower() == settings.MAIN_EXIT_CHAR:
                exit_program()

            elif cell_input.lower() == 'done':
                break

            try:
                cell_position, cost = cell_input.rsplit(',', 1)
                cell_position = tuple(map(int, cell_position.split(',')))
                cost = int(cost)

                if cell_position in increased_cost_cells:
                    print("This cell already has a defined cost. Please enter a different position or finish adding.")
                    continue

                increased_cost_cells[cell_position] = cost
                add_increased_cost = input('Add another cell with increased cost? (y/n): ')

            except ValueError:
                print('Invalid input. Please try again.')

        return increased_cost_cells

    print('Would you like to manually enter grid details or use a default grid?')
    grid_method = input('Enter "m" for manual, "d" for default ("q" to quit"): ')

    if grid_method.lower() == settings.MAIN_EXIT_CHAR:
        exit_program()

    elif grid_method.lower() == 'd':
        grid = DEFAULT_GRID_BY_STRATEGY_MAP.get(strategy, None)
        if not grid:
            logger.error('Invalid strategy: %s', strategy)
            raise ValueError(f'Invalid strategy: {strategy}')

    elif grid_method.lower() == 'm':
        print('Enter "q" to quit at any time.', end='\n\n')

        width, height        = _get_grid_size()
        start_state          = _get_start_state()
        goal_state           = _get_goal_state()
        barriers             = _get_barriers()
        increased_cost_cells = _get_increased_cost_cells()

        grid = Grid(
            width=width,
            height=height,
            start=start_state,
            goal=goal_state,
            barriers=barriers,
            increased_cost_cells=increased_cost_cells
        )

    return grid


def run_search(strategy: UninformedSearchStrategy, grid: Grid, visualizer_method: VisualizationMethod):
    """
    Run the algorithm search method utilizing the appropriate visualizer
    method.
    """
    if visualizer_method == VisualizationMethod.GUI:
        search = UninformedSearch(
            grid=grid,
            strategy=strategy,
            visualizer_method=visualizer_method
        )
        gui = GridGUI(grid, search)
        search.visualizer = gui
        gui.run()
    else:
        search = UninformedSearch(
            grid=grid,
            strategy=strategy,
            visualizer_method=visualizer_method
        )
        search.run()

    print(f'Final path: {search.path}')
    print(f'Final cost: {search.final_cost}')
