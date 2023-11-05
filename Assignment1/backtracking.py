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
    return 0 <= pos.x < N and 0 <= pos.y < N


def move_is_empty(map_: List[List[Character]], pos: Cell) -> bool:
    """Returns whether one can move into `pos`.

    Args:
        map_ (List[List[Entity]]): Map.
        pos (Cell): Cell that one wants to move into.

    Returns:
        bool: Whether one can move into `pos`.
    """
    # we can move into a cell which does not contain obstacles
    return map_[pos.x][pos.y] in (Character.EMPTY, Character.INFINITY_STONE)


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


def get_accessible_neighbours(pos: Cell) -> List[Cell]:
    neighbours = []
    for direction in Cell(1, 0), Cell(0, 1), Cell(-1, 0), Cell(0, -1):
        neighbour = pos + direction
        if move_in_map(neighbour):
            neighbours.append(neighbour)
    return neighbours


def get_accessible_perception(pos: Cell, variant: int) -> List[Cell]:
    perception = (Cell(1, 0), Cell(1, 1), Cell(0, 1), Cell(-1, 1), Cell(-1, 0), Cell(-1, -1), Cell(0, -1), Cell(1, -1))
    if variant == 2:
        perception += (Cell(2, 2), Cell(-2, 2), Cell(-2, -2), Cell(2, -2))

    neighbours = []
    for direction in perception:
        neighbour = pos + direction
        if move_in_map(neighbour):
            neighbours.append(neighbour)

    return neighbours


visited: List[List[bool]] = [[False for _ in range(N)] for _ in range(N)]
distance: List[List[int]] = [[N**3 for _ in range(N)] for _ in range(N)]
path_to_goal: List[Cell] = []
path_to_shield: List[Cell] = []


def backtracking(
    map_: List[List[Character]],
    current: Cell,
    goal: Cell,
    path: List[Cell],
    variant_number: int,
) -> None:
    global path_to_goal, path_to_shield, visited, distance

    if len(path) + 1 >= distance[current.x][current.y]:
        return
    if path_to_goal and len(path) + 1 >= len(path_to_goal):
        return
    if current == goal:
        path_to_goal = path.copy() + [current]
        return

    visited[current.x][current.y] = True
    distance[current.x][current.y] = len(path) + 1
    path.append(current)
    ask_to_move(map_, current)

    neighbours = get_accessible_neighbours(current)
    neighbours.sort(key=goal.manhattan)
    for neighbour in neighbours:
        if visited[neighbour.x][neighbour.y]:
            continue
        if map_[neighbour.x][neighbour.y] == Character.SHIELD:
            if not path_to_shield or len(path) + 1 < len(path_to_shield):
                path_to_shield = path.copy() + [neighbour]
            continue
        if not move_is_empty(map_, neighbour):
            continue

        backtracking(map_, neighbour, goal, path, variant_number)
        ask_to_move(map_, current)

        if neighbour == goal:
            break

    visited[current.x][current.y] = False
    path.pop()


def main():
    global visited, distance

    variant_number = int(input())
    x, y = map(int, input().split())
    goal = Cell(x, y)
    start = Cell(0, 0)
    map_: List[List[Character]] = [[Character.EMPTY for _ in range(N)] for _ in range(N)]

    backtracking(map_, start, goal, [], variant_number)

    if path_to_shield:
        for cell in path_to_shield[1:-1]:
            ask_to_move(map_, cell)
        for i in range(N):
            for j in range(N):
                if map_[i][j] == Character.PERCEPTION:
                    map_[i][j] = Character.EMPTY
        visited = [[False for _ in range(N)] for _ in range(N)]
        distance = [[N**3 for _ in range(N)] for _ in range(N)]
        backtracking(map_, path_to_shield[-1], goal, path_to_shield[:-1], variant_number)

    print(f"e {len(path_to_goal) - 1}")


if __name__ == "__main__":
    main()
