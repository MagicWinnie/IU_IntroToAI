from dataclasses import dataclass
from enum import Enum
from typing import List


N = 9  # size of the map (NxN)


class Character(str, Enum):
    """
    Enum for characters that can be found on the map:
        Hulk, Thor, Captain Marvel, Infinity Stone, Shield, and Perception Zone.
    Note: EMPTY, and PATH are technical entities.
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


@dataclass
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


def move_is_empty(map_: List[List[Character]], pos: Cell) -> bool:
    """Checks whether one can move into `pos`.

    Args:
        map_ (List[List[Entity]]): Map.
        pos (Cell): Cell that one wants to move into.

    Returns:
        bool: Whether one can move into `pos`.
    """
    # we can move into a cell which does not contain obstacles
    return map_[pos.x][pos.y] in (Character.EMPTY, Character.INFINITY_STONE)


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


def get_accessible_neighbours(pos: Cell) -> List[Cell]:
    """Get accessible neighbours of `pos`.

    Args:
        pos (Cell): Cell to use.

    Returns:
        List[Cell]: Neighbours of `pos`.
    """
    neighbours = []
    # we can move in 4 directions
    for direction in Cell(1, 0), Cell(0, 1), Cell(-1, 0), Cell(0, -1):
        neighbour = pos + direction
        if move_in_map(neighbour):
            neighbours.append(neighbour)
    # wishing a great day to whom ever is checking this work right now :)
    return neighbours


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


# storing whether one has visited cell (i, j)
visited: List[List[bool]] = [[False for _ in range(N)] for _ in range(N)]
# storing the minimum distance from start to cell (i, j)
distance: List[List[int]] = [[N**3 for _ in range(N)] for _ in range(N)]
# storing the minimum path from start to infinity stone
path_to_goal: List[Cell] = []
# storing the minimum path from start to shield
path_to_shield: List[Cell] = []


def backtracking(
    map_: List[List[Character]],
    current: Cell,
    goal: Cell,
    path: List[Cell],
    variant_number: int,
    with_shield: bool,
) -> None:
    """Backtracking algorithm to find the shortest path between `current` and `goal`.
    Puts the path for the goal in global `path_to_goal`.
    Puts the path for the shield in global `path_to_shield`.

    Args:
        map_ (List[List[Character]]): Map to work on.
        current (Cell): Start cell.
        goal (Cell): Goal cell.
        path (List[Cell]): Current path before entering `current`.
        variant_number (int): Variant of Thanos' vision.
        with_shield (bool): Whether Thanos is under shield's effects.
    """
    global path_to_goal, path_to_shield, visited, distance

    # do not check if we have worse distance
    if len(path) + 1 >= distance[current.x][current.y]:
        return
    # do not check if the distance to the goal is worse
    if path_to_goal and len(path) + 1 >= len(path_to_goal):
        return
    # if we reached the goal update the path
    # as the path now is now shorter
    if current == goal:
        path_to_goal = path.copy() + [current]
        return

    # mark this cell as visited to not to visit it in later recursive calls
    visited[current.x][current.y] = True
    # update the shortest path to here
    distance[current.x][current.y] = len(path) + 1
    # update the path with our current cell
    path.append(current)
    # move the interactor to the current cell
    ask_to_move(map_, current, variant_number, with_shield)

    # in variant 2 we can see into cells where thor and captain marvel are located

    # get neighbours and sort them by their distance to the goal
    neighbours = get_accessible_neighbours(current)
    neighbours.sort(key=goal.manhattan)
    for neighbour in neighbours:
        # cell should not be visited
        if visited[neighbour.x][neighbour.y]:
            continue
        # process the shield
        if map_[neighbour.x][neighbour.y] == Character.SHIELD:
            # update the path to it
            if not path_to_shield or len(path) + 1 < len(path_to_shield):
                path_to_shield = path.copy() + [neighbour]
            # do not allow to move there
            continue
        # check if the cell does not contain enemies
        if not move_is_empty(map_, neighbour):
            continue

        # recursive call on the neighbour
        backtracking(map_, neighbour, goal, path, variant_number, with_shield)
        # move the interactor back so next neighbour can run
        ask_to_move(map_, current, variant_number, with_shield)

        # do not check others if the goal can be reached from here
        if neighbour == goal:
            break

    # unmark the cell so we can try to visit it later
    visited[current.x][current.y] = False
    # remove the cell from the current path
    path.pop()


def main() -> None:
    """Main function of the solution."""
    global visited, distance

    variant_number = int(input())
    x, y = map(int, input().split())
    goal = Cell(x, y)
    start = Cell(0, 0)
    map_: List[List[Character]] = [[Character.EMPTY for _ in range(N)] for _ in range(N)]

    # run backtracking from start to goal without picking up the shield
    backtracking(map_, start, goal, [], variant_number, False)

    # if the shield was spotted and is accessible
    if path_to_shield:
        # move to the shield to pick it up
        for cell in path_to_shield[1:-1]:
            ask_to_move(map_, cell, variant_number, True)
        # remove perception zones
        # captain marvels perception zone will be restore when asking interactor
        for i in range(N):
            for j in range(N):
                if map_[i][j] == Character.PERCEPTION:
                    map_[i][j] = Character.EMPTY
        # reset visited and distances
        visited = [[False for _ in range(N)] for _ in range(N)]
        distance = [[N**3 for _ in range(N)] for _ in range(N)]
        # run backtracking from shield to goal
        backtracking(map_, path_to_shield[-1], goal, path_to_shield[:-1], variant_number, True)

    # print the shortest path
    # note: if path_to_goal is empty then -1 will be printed
    print(f"e {len(path_to_goal) - 1}")


if __name__ == "__main__":
    main()
