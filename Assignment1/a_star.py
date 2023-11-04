from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Tuple
from queue import PriorityQueue


N = 9  # size of the map (NxN)


class Character(str, Enum):
    """
    Enum for characters that can be found on the map:
        Hulk, Thor, Captain Marvel, Infinity Stone, Shield, and Perception Zone.
    Note: EMPTY and PATH are technical entities.
    """

    HULK = "H"
    INFINITY_STONE = "I"
    THOR = "T"
    CAPTAIN_MARVEL = "M"
    SHIELD = "S"
    PERCEPTION = "P"
    EMPTY = "."
    PATH = "*"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


@dataclass(order=True, unsafe_hash=True)
class Cell:
    """
    Dataclass that represents the coordinates (x, y) for a cell.
    """

    x: int
    y: int

    def __add__(self, other: "Cell") -> "Cell":
        return Cell(self.x + other.x, self.y + other.y)

    def manhattan(self, other: "Cell") -> int:
        """Returns manhattan distance from current cell to `other`.

        Args:
            other (Cell): Another cell for calculating distance to.

        Returns:
            int: Manhattan distance to `other`.
        """
        return abs(self.x - other.x) + abs(self.y - other.y)


def can_move(map_: List[List[Character]], pos: Cell) -> bool:
    """Returns whether one can move into `pos`.
    Note: it checks only for obstacles and does not check for out of bounds.

    Args:
        map_ (List[List[Entity]]): Map.
        pos (Cell): Cell that one wants to move into.

    Returns:
        bool: Whether one can move into `pos`.
    """
    # we can move into a cell which does not contain obstacles
    if pos.x < 0 or pos.y < 0 or pos.x >= N or pos.y >= N:
        return False
    return map_[pos.x][pos.y] not in (Character.CAPTAIN_MARVEL, Character.HULK, Character.THOR, Character.PERCEPTION)


def ask_to_move(map_: List[List[Character]], pos: Cell) -> None:
    """Ask the interactor to move into `pos` and gather information about surroundings.

    Args:
        map_ (List[List[Entity]]): Map.
        pos (Cell): Cell that one wants to move into.
    """
    print(f"m {pos.x} {pos.y}")
    n = int(input())
    for _ in range(n):
        x, y, e = input().split()
        map_[int(x)][int(y)] = Character(e)


def heuristics(start: Cell, goal: Cell) -> float:
    """Heuristics function for A*. Returns manhattan distance between `start` and `goal`.

    Args:
        start (Cell): Start cell.
        goal (Cell): Goal cell.

    Returns:
        float: Manhattan distance between `start` and `goal`.
    """
    return start.manhattan(goal)


def path_from_parents(parent: Dict[Cell, Cell], current: Cell) -> List[Cell]:
    """Reconstructs the path based on `parent` dictionary and the `goal` cell.

    Args:
        parent (Dict[Cell, Cell]): Parent dictionary.
        current (Cell): `goal` cell.

    Returns:
        List[Cell]: Path from `start` to `goal`.
    """
    total_path: List[Cell] = [current]
    while current in parent.keys():
        current = parent[current]
        total_path = [current] + total_path
    return total_path


def a_star(
    map_: List[List[Character]],
    start: Cell,
    goal: Cell,
    h: Callable[[Cell, Cell], float],
    grab_shield: bool,
    go_to_start_after_finish: bool,
) -> List[Cell]:
    """A* search algorithm implementation.
    Based on pseudocode from https://en.wikipedia.org/wiki/A*_search_algorithm

    Args:
        map_ (List[List[Entity]]): Map.
        start (Cell): Start cell.
        goal (Cell): Goal cell.
        h (Callable[[Cell, Cell], float]): Function for heuristics.
        grab_shield (bool): Whether to grab the shield.
        go_to_start_after_finish (bool): Whether to go back to the start after finishing.

    Returns:
        List[Cell]: Shortest path from `start` to `goal` (empty list if not found)
    """
    # set of discovered cells that may need to be (re-)expanded
    open_set: PriorityQueue[Tuple[float, Cell]] = PriorityQueue()
    open_set.put((0, start))

    # parent dictionary (stores the closest parent)
    parent: Dict[Cell, Cell] = {}

    # g_score[x][y] is the shortest distance from `start` to `Cell(x, y)`
    g_score: List[List[float]] = [[float("inf") for _ in range(N)] for _ in range(N)]
    g_score[start.x][start.y] = 0

    # f_score[x][y] is the guess for the shortest distance from `start` to `goal` through `Cell(x, y)`
    f_score: List[List[float]] = [[float("inf") for _ in range(N)] for _ in range(N)]
    f_score[start.x][start.y] = h(start, goal)

    # previous visited cell
    previous = start
    while not open_set.empty():
        # get the cell with the lowest f_score
        current: Cell = open_set.get()[1]

        # move the interactor from the previous cell to the current one to prevent teleportation
        if current.manhattan(previous) != 1:
            # move through cells from `previous` to `start`
            for cell in path_from_parents(parent, previous)[::-1]:
                ask_to_move(map_, cell)
            # move through cells from `start` to preceding of current
            for cell in path_from_parents(parent, current)[1:]:
                ask_to_move(map_, cell)
        # move to the current cell
        ask_to_move(map_, current)

        # when we reach the destination we can reconstruct the path
        if current == goal:
            if go_to_start_after_finish:
                for cell in path_from_parents(parent, current)[::-1]:
                    ask_to_move(map_, cell)
            return path_from_parents(parent, current)

        previous = current

        # check the neighbors
        for direction in Cell(1, 0), Cell(0, 1), Cell(-1, 0), Cell(0, -1):
            neighbor = current + direction
            # check that we can move there and not meet enemies
            if not can_move(map_, neighbor):
                continue
            if map_[neighbor.x][neighbor.y] == Character.SHIELD and not grab_shield:
                continue

            # distance from `start` to the `neighbor` through `current`
            g_score_neighbor = g_score[current.x][current.y] + 1
            # if we found a shorter path
            if g_score_neighbor < g_score[neighbor.x][neighbor.y]:
                # update the parent
                parent[neighbor] = current
                # update the `g_score`
                g_score[neighbor.x][neighbor.y] = g_score_neighbor
                # update the `f_score`
                f_score[neighbor.x][neighbor.y] = g_score_neighbor + h(neighbor, goal)
                # add the neighbor for future exploration
                open_set.put((f_score[neighbor.x][neighbor.y], neighbor))

    # path from `start` to `goal` does not exist
    if go_to_start_after_finish:
        for cell in path_from_parents(parent, previous)[::-1]:
            ask_to_move(map_, cell)
    return []


def main():
    map_: List[List[Character]] = [[Character.EMPTY for _ in range(N)] for _ in range(N)]

    variant_number = int(input())
    x, y = map(int, input().split())
    goal = Cell(x, y)
    start = Cell(0, 0)

    # find the shortest path from the start to the goal without grabbing the shield
    min_path = a_star(map_, start, goal, heuristics, False, True)

    # find shield if it was spotted
    shield = Cell(-1, -1)
    for i in range(N):
        for j in range(N):
            if map_[i][j] == Character.SHIELD:
                shield = Cell(i, j)

    # if the shield was spotted
    if shield != Cell(-1, -1):
        # find the shortest path from the start to the shield
        min_path_to_shield = a_star(map_, start, shield, heuristics, True, False)
        if min_path_to_shield:
            # remove perception zones from the map
            # (ones for Captain Marvel will reappear during further exploration)
            for i in range(N):
                for j in range(N):
                    if map_[i][j] == Character.PERCEPTION:
                        map_[i][j] = Character.EMPTY
            # find the shortest path from the shield to the goal
            min_path_from_shield = a_star(map_, shield, goal, heuristics, False, False)
            if min_path_from_shield:
                # update the shortest path if neccessary
                min_path_with_shield = min_path_to_shield[:-1] + min_path_from_shield
                if not min_path or len(min_path_with_shield) < len(min_path):
                    min_path = min_path_with_shield
    # print the length of the shortest path from `start` to `goal`
    # note: if path_to_goal is empty, then -1 will be printed
    print(f"e {len(min_path) - 1}")


if __name__ == "__main__":
    main()
