from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Tuple
from queue import PriorityQueue


N = 9  # size of the map (NxN)
INF = N**3


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


def move_in_map(pos: Cell) -> bool:
    """Checks whether `pos` is in the map.

    Args:
        pos (Cell): Cell that needs to be checked.

    Returns:
        bool: Whether `pos` is in the map.
    """
    return 0 <= pos.x < N and 0 <= pos.y < N


def can_move(map_: List[List[Character]], pos: Cell) -> bool:
    """Returns whether one can move into `pos`.

    Args:
        map_ (List[List[Entity]]): Map.
        pos (Cell): Cell that one wants to move into.

    Returns:
        bool: Whether one can move into `pos`.
    """
    # we can move into a cell which does not contain obstacles
    return map_[pos.x][pos.y] not in (Character.CAPTAIN_MARVEL, Character.HULK, Character.THOR, Character.PERCEPTION)


def ask_to_move(map_: List[List[Character]], pos: Cell, variant: int, with_shield: bool) -> None:
    """Ask the interactor to move into `pos` and gather information about surroundings.

    Args:
        map_ (List[List[Entity]]): Map.
        pos (Cell): Cell that one wants to move into.
        variant (int): Thanos' perception variant.
        with_shield (bool): Whether we are with the Shield.
    """
    print(f"m {pos.x} {pos.y}")
    n = int(input())
    for _ in range(n):
        x_, y_, e_ = input().split()
        x, y, e = int(x_), int(y_), Character(e_)
        # if we put the character the first time
        if map_[x][y] == Character.EMPTY:
            # for variant 1 we can be sure only for Hulk
            if variant == 1:
                if not with_shield:
                    if e == Character.HULK:
                        build_hulk_perception(map_, Cell(x, y))
            elif variant == 2:
                # for variant 2 we are sure about everyone
                if e == Character.CAPTAIN_MARVEL:
                    build_marvel_perception(map_, Cell(x, y))
                if not with_shield:
                    if e == Character.HULK:
                        build_hulk_perception(map_, Cell(x, y))
                    elif e == Character.THOR:
                        build_thor_perception(map_, Cell(x, y))
            map_[x][y] = e


def build_thor_perception(map_: List[List[Character]], center: Cell) -> None:
    """Put Thor's perception zones onto the map.

    Args:
        map_ (List[List[Character]]): Map itself.
        center (Cell): Cell with Thor.
    """
    for direction in (
        Cell(1, 0),
        Cell(1, 1),
        Cell(0, 1),
        Cell(-1, 1),
        Cell(-1, 0),
        Cell(-1, -1),
        Cell(0, -1),
        Cell(1, -1),
    ):
        cell = center + direction
        if move_in_map(cell) and map_[cell.x][cell.y] == Character.EMPTY:
            map_[cell.x][cell.y] = Character.PERCEPTION


def build_hulk_perception(map_: List[List[Character]], center: Cell) -> None:
    """Put Hulk's perception zones onto the map.

    Args:
        map_ (List[List[Character]]): Map itself.
        center (Cell): Cell with Hulk.
    """
    for direction in (
        Cell(1, 0),
        Cell(0, 1),
        Cell(-1, 0),
        Cell(0, -1),
    ):
        cell = center + direction
        if move_in_map(cell) and map_[cell.x][cell.y] == Character.EMPTY:
            map_[cell.x][cell.y] = Character.PERCEPTION


def build_marvel_perception(map_: List[List[Character]], center: Cell) -> None:
    """Put Captain Marvel's perception zones onto the map.

    Args:
        map_ (List[List[Character]]): Map itself.
        center (Cell): Cell with Captain Marvel.
    """
    for direction in (
        Cell(1, 0),
        Cell(1, 1),
        Cell(0, 1),
        Cell(-1, 1),
        Cell(-1, 0),
        Cell(-1, -1),
        Cell(0, -1),
        Cell(1, -1),
        Cell(2, 0),
        Cell(0, 2),
        Cell(-2, 0),
        Cell(0, -2),
    ):
        cell = center + direction
        if move_in_map(cell) and map_[cell.x][cell.y] == Character.EMPTY:
            map_[cell.x][cell.y] = Character.PERCEPTION


def heuristics(start: Cell, goal: Cell) -> int:
    """Heuristics function for A*. Returns manhattan distance between `start` and `goal`.

    Args:
        start (Cell): Start cell.
        goal (Cell): Goal cell.

    Returns:
        int: Manhattan distance between `start` and `goal`.
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
    h: Callable[[Cell, Cell], int],
    grab_shield: bool,
    go_to_start_after_finish: bool,
    variant_number: int,
) -> List[Cell]:
    """A* search algorithm implementation.
    Based on pseudocode from https://en.wikipedia.org/wiki/A*_search_algorithm

    Args:
        map_ (List[List[Entity]]): Map.
        start (Cell): Start cell.
        goal (Cell): Goal cell.
        h (Callable[[Cell, Cell], int]): Function for heuristics.
        grab_shield (bool): Whether to grab the shield.
        go_to_start_after_finish (bool): Whether to go back to the start after finishing.
        variant_number (int): Thanos' vision variant.

    Returns:
        List[Cell]: Shortest path from `start` to `goal` (empty list if not found)
    """
    # set of discovered cells that may need to be (re-)expanded
    open_set: PriorityQueue[Tuple[int, Cell]] = PriorityQueue()
    open_set.put((0, start))

    # parent dictionary (stores the closest parent)
    parent: Dict[Cell, Cell] = {}

    # g_score[x][y] is the shortest distance from `start` to `Cell(x, y)`
    g_score: Dict[Cell, int] = {}
    g_score[start] = 0

    # f_score[x][y] is the guess for the shortest distance from `start` to `goal` through `Cell(x, y)`
    f_score: Dict[Cell, int] = {}
    f_score[start] = h(start, goal)

    # previous visited cell
    previous = start
    while not open_set.empty():
        # get the cell with the lowest f_score
        current: Cell = open_set.get()[1]

        # move the interactor from the previous cell to the current one to prevent teleportation
        if current.manhattan(previous) != 1:
            # move through cells from `previous` to `start`
            for cell in path_from_parents(parent, previous)[::-1]:
                ask_to_move(map_, cell, variant_number, grab_shield)
            # move through cells from `start` to preceding of current
            for cell in path_from_parents(parent, current)[1:]:
                ask_to_move(map_, cell, variant_number, grab_shield)
        # move to the current cell
        ask_to_move(map_, current, variant_number, grab_shield)

        # when we reach the destination we can reconstruct the path
        if current == goal:
            if go_to_start_after_finish:
                for cell in path_from_parents(parent, current)[::-1]:
                    ask_to_move(map_, cell, variant_number, grab_shield)
            return path_from_parents(parent, current)

        previous = current

        # check the neighbors
        for direction in Cell(1, 0), Cell(0, 1), Cell(-1, 0), Cell(0, -1):
            neighbor = current + direction
            # check that we can move there and not meet enemies
            if not move_in_map(neighbor):
                continue
            if not can_move(map_, neighbor):
                continue
            if map_[neighbor.x][neighbor.y] == Character.SHIELD and not grab_shield:
                continue

            # distance from `start` to the `neighbor` through `current`
            g_score_neighbor = g_score.get(current, INF) + 1
            # if we found a shorter path
            if g_score_neighbor < g_score.get(neighbor, INF):
                # update the parent
                parent[neighbor] = current
                # update the `g_score`
                g_score[neighbor] = g_score_neighbor
                # update the `f_score`
                f_score[neighbor] = g_score_neighbor + h(neighbor, goal)
                # add the neighbor for future exploration
                open_set.put((f_score[neighbor], neighbor))

    # path from `start` to `goal` does not exist
    if go_to_start_after_finish:
        for cell in path_from_parents(parent, previous)[::-1]:
            ask_to_move(map_, cell, variant_number, grab_shield)

    return []


def main():
    """Main function of the solution."""
    map_: List[List[Character]] = [[Character.EMPTY for _ in range(N)] for _ in range(N)]

    variant_number = int(input())
    x, y = map(int, input().split())
    goal = Cell(x, y)
    start = Cell(0, 0)

    # find the shortest path from the start to the goal without grabbing the shield
    min_path = a_star(map_, start, goal, heuristics, False, True, variant_number)

    # find shield if it was spotted
    shield = Cell(-1, -1)
    for i in range(N):
        for j in range(N):
            if map_[i][j] == Character.SHIELD:
                shield = Cell(i, j)

    # if the shield was spotted
    if shield != Cell(-1, -1):
        # find the shortest path from the start to the shield
        min_path_to_shield = a_star(map_, start, shield, heuristics, True, False, variant_number)
        if min_path_to_shield:
            # remove perception zones from the map
            # (ones for Captain Marvel will reappear during further exploration)
            for i in range(N):
                for j in range(N):
                    if map_[i][j] == Character.PERCEPTION:
                        map_[i][j] = Character.EMPTY
            # find the shortest path from the shield to the goal
            min_path_from_shield = a_star(map_, shield, goal, heuristics, True, False, variant_number)
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
