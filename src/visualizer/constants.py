from enum import Enum

from components import Grid


class UninformedSearchStrategy(str, Enum):
    """
    An enumeration of valid strategies for an Uninformed Search.
    """
    DepthFirstSearch         = "Depth-first search"
    DepthLimitedSearch       = "Depth-limited search"
    BreadthFirstSearch       = "Breadth-first search"
    UniformCostSearch        = "Uniform-cost search"
    IterativeDeepeningSearch = "Iterative deepening search"


class InformedSearchStrategy(str, Enum):
    """
    An enumeration of valid strategies for an Informed Search.
    """
    AStarSearch           = "A* search"
    GreedyBestFirstSearch = "Greedy best-first search"


class VisualizationMethod(str, Enum):
    """
    An enumeration of valid visualization methods.
    """
    Nothing = 'Nothing'
    CLI     = 'CLI'
    GUI     = 'GUI'


DEFAULT_GRID_BY_STRATEGY_MAP = {
    UninformedSearchStrategy.DepthFirstSearch: Grid(
        width=5,
        height=5,
        start=(0, 0),
        goal=(4, 4),
        barriers=[(2, 2)]
    ),
    UninformedSearchStrategy.DepthLimitedSearch: Grid(
        width=5,
        height=5,
        start=(0, 0),
        goal=(4, 4),
        barriers=[(2, 2)]
    ),
    UninformedSearchStrategy.BreadthFirstSearch: Grid(
        width=5,
        height=5,
        start=(0, 0),
        goal=(4, 4),
        barriers=[(2, 2)]
    ),
    UninformedSearchStrategy.UniformCostSearch: Grid(
        width=5,
        height=5,
        start=(0, 0),
        goal=(4, 4),
        barriers=[(2, 2)],
        increased_cost_cells={(3, 3): 5, (2, 1): 9}
    ),
    UninformedSearchStrategy.IterativeDeepeningSearch: Grid(
        width=5,
        height=5,
        start=(0, 0),
        goal=(4, 4),
        barriers=[(2, 2)]
    )
}
