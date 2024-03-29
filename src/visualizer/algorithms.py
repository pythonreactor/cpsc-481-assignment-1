from abc import (
    ABC,
    abstractmethod
)
from queue import (
    Queue,
    LifoQueue,
    PriorityQueue
)
from typing import (
    Dict,
    List,
    Union
)

from components import (
    Grid,
    GridGUI,
    Node
)
from constants import (
    VisualizationMethod,
    UninformedSearchStrategy
)
import settings

logger = settings.getLogger(__name__)


class BaseSearch(ABC):
    """
    Base search class for Uninformed and Informed search algorithms.
    """

    frontier_type_map: Dict = {}

    @abstractmethod
    def _reconstruct_path(self, current_node: Node) -> List:
        """
        Reconstruct the path backwards from the goal to start node.
        """
        raise NotImplementedError('_reconstruct_path method called from the Base class')

    @abstractmethod
    def _update_priority_queue(self, cost: int, node: Node):
        """
        Update a PriorityQueue frontier.
        """
        raise NotImplementedError('_update_priority_queue called from the Base class')

    @abstractmethod
    def update_frontier(self, node: Node, cost: int = None):
        """
        Update a non-priority queue frontier.
        """
        raise NotImplementedError('update_frontier method called from the Base class')

    @abstractmethod
    def search(self):
        """
        Run the search algorithm based on the initialized strategy.
        """
        raise NotImplementedError('search method called from the Base class')

    @abstractmethod
    def run(self):
        """
        Run the search method and log messages based on the result.
        """
        raise NotImplementedError('run method called from the Base class')


class UninformedSearch(BaseSearch):
    """
    This class implements different uninformed search strategies to find
    a path from the start state to a goal state.
    """

    frontier_type_map = {
        UninformedSearchStrategy.DepthFirstSearch: LifoQueue,
        UninformedSearchStrategy.DepthLimitedSearch: LifoQueue,
        UninformedSearchStrategy.BreadthFirstSearch: Queue,
        UninformedSearchStrategy.UniformCostSearch: PriorityQueue
    }
    frontier_type_map[UninformedSearchStrategy.IterativeDeepeningSearch] = frontier_type_map.get(UninformedSearchStrategy.DepthLimitedSearch)

    def __init__(
        self,
        grid: Grid,
        strategy: UninformedSearchStrategy,
        depth_limit: int = None,
        visualizer_method: VisualizationMethod = VisualizationMethod.Nothing,
        visualizer: Union[GridGUI, None] = None
    ):
        # TODO: Generate CLI visualizer class
        self.visualizer_method = visualizer_method
        self.visualizer        = visualizer

        if not isinstance(grid, Grid):
            raise TypeError('Grid must be an instance of Grid')
        self.grid = grid

        if strategy not in UninformedSearchStrategy:
            raise ValueError(f"Invalid strategy: {strategy}")
        self.strategy = strategy

        self.start_node: Node = Node(state=self.grid.start, parent=None, cost=0)
        self.frontier         = UninformedSearch.frontier_type_map[strategy]()
        self.frontier_set     = set()  # Maintain O(1) lookup times for PriorityQueue
        self.explored         = set()

        self.path: List      = []
        self.final_cost: int = 0

        # Restrict the depth limit to no more than 100 for performance reasons
        self.depth_limit: int      = min(depth_limit, 100) if depth_limit else None
        self.depth_limit_hit: bool = False

    def _reconstruct_path(self, current_node: Node) -> List:
        """
        Reconstructs the path from the goal to the start node.
        """
        if not isinstance(current_node, Node):
            raise TypeError('Current node must be an instance of Node')

        path = []
        while current_node:
            path.append(current_node.state)
            current_node = current_node.parent

        return path[::-1]

    def _update_priority_queue(self, cost: int, node: Node):
        """
        Update the priority queue for the Uniform Cost Search with the
        cost and node.
        """
        if not isinstance(cost, int):
            raise TypeError('Cost must be an integer')
        elif not isinstance(node, Node):
            raise TypeError('Node must be an instance of Node')

        if node.state not in self.frontier_set:
            self.frontier.put((cost, node))
            self.frontier_set.add(node.state)

    def update_frontier(self, node: Node, cost: int = None):
        """
        Update the frontier based on the search strategy being used.
        """
        if not isinstance(node, Node):
            raise TypeError('Node must be an instance of Node')

        if not cost:
            cost = node.cost

        if type(self.frontier) == PriorityQueue:
            self._update_priority_queue(cost=cost, node=node)
        else:
            self.frontier.put(node)
            self.frontier_set.add(node.state)

    def search(self):
        """
        Run the search based on the initialized strategy.
        """
        self.update_frontier(self.start_node)

        while not self.frontier.empty():
            if type(self.frontier) == PriorityQueue:
                # NOTE: We are always putting (cost, node) into the PriorityQueue
                cost, current_node = self.frontier.get()
            else:
                # NOTE: We only put the node into the non-Priority queue
                current_node = self.frontier.get()

            if self.visualizer_method == VisualizationMethod.GUI and isinstance(self.visualizer, GridGUI):
                self.visualizer.draw_grid(path=self.path, current_position=current_node.state)
                self.visualizer.wait_for_click()

            if type(self.visualizer) == GridGUI:
                self.visualizer.draw_grid(path=self.path, current_position=current_node.state)

            if current_node.state in self.frontier_set:
                self.frontier_set.remove(current_node.state)

            if self.grid.is_goal_state(node=current_node):
                logger.debug('%s: Goal state found -> %s', self.strategy.value, self.grid.goal)

                self.path       = self._reconstruct_path(current_node)
                self.final_cost = current_node.cost

                break

            if self.depth_limit is not None and current_node.depth >= self.depth_limit:
                logger.debug('%s: Depth limit hit!', self.strategy.value)

                self.depth_limit_hit = True
                self.final_cost      = current_node.cost

                self.grid.print_grid_cli(current_position=current_node.state)

                break

            self.explored.add(current_node.state)
            for neighbor in self.grid.get_neighbors(current_node):
                # NOTE: Since a Node is considered "immutable," we'd want to create
                # a new one when updating the depth value. But we don't necessarily want
                # to do that for every single search algorithm (for performance purposes).
                if self.depth_limit is not None:
                    new_neighbor = Node(
                        state=neighbor.state,
                        parent=current_node,
                        cost=neighbor.cost,
                        depth=current_node.depth + 1
                    )
                else:
                    new_neighbor = neighbor

                if new_neighbor.state not in self.explored and new_neighbor.state not in self.frontier_set:
                    self.update_frontier(new_neighbor)

            print(f'{self.strategy.value}: Exploring node {current_node.state} at depth {current_node.depth}')

            if self.visualizer_method == VisualizationMethod.CLI:
                self.grid.print_grid_cli(current_position=current_node.state)
                input('Press Enter to continue...')

    def iterative_deepening_search(self):
        """
        Perform a series of Depth-Limited Searches.
        """
        depth = 0
        max_depth = self.depth_limit or 100

        while depth <= max_depth:
            self.depth_limit = depth
            self.frontier = self.__class__.frontier_type_map[UninformedSearchStrategy.IterativeDeepeningSearch]()
            self.frontier_set.clear()
            self.explored.clear()
            self.path.clear()
            self.final_cost = 0
            self.depth_limit_hit = False

            self.search()

            if not self.path:
                depth += 1
            else:
                logger.debug('%s: Path found', self.strategy.value)
                logger.debug('Final depth: %s', depth)
                break

    def run(self):
        """
        Run the search method and log messages based on the result.
        """
        logger.info('Running %s...', self.strategy.value)

        if self.strategy == UninformedSearchStrategy.IterativeDeepeningSearch:
            self.iterative_deepening_search()
        else:
            self.search()

        logger.info('%s completed.', self.strategy.value)
