import settings
from utils import (
    get_search_strategy,
    get_visualizer_method,
    get_grid,
    run_search
)
from constants import VisualizationMethod
from components import GridGUI

logger = settings.getLogger(__name__)


def main():
    """
    Gather information on the Grid and how to visualize the algorithm
    before running the search visualizer.
    """
    print('Welcome to the Search Algorithm Visualizer!')
    print('------------------------------------------', end='\n\n')

    strategy = get_search_strategy()
    print(f'You selected: {strategy.value}', end='\n\n')

    visualizer_method: VisualizationMethod = get_visualizer_method()
    print(f'{visualizer_method} visualization selected.', end='\n\n')

    grid = get_grid(strategy=strategy)
    print(f'Grid configuration:\n{grid}', end='\n\n')

    if visualizer_method in VisualizationMethod:
        run_search(strategy=strategy, grid=grid, visualizer_method=visualizer_method)
    else:
        logger.error('Invalid visualization method selected. Exiting the program.')
        exit('Goodbye!')


if __name__ == '__main__':
    main()
