from typing import List
from enum import Enum
from dataclasses import dataclass


N = 9  # size of the map (NxN)


class Entity(str, Enum):
    """
    Enum for enitites that can be found on the map:
        Hulk, Thor, Captain Marvel, Infinity Stone, Shield, and Perception Zone.
    Note: EMPTY, WALL, and PATH are technical entities.
    """

    HULK = "H"
    INFINITY_STONE = "I"
    THOR = "T"
    CAPTAIN_MARVEL = "M"
    SHIELD = "S"
    PERCEPTION = "P"
    EMPTY = "."
    PATH = "*"
    WALL = "W"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


@dataclass(unsafe_hash=True)
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


def possible_moves(pos: Cell) -> List[Cell]:
    """Returns a list of possible moves from `pos` cell.
    Note: it checks only for out of bounds and does not check for obstacles.

    Args:
        pos (Cell): Cell to start from.

    Returns:
        List[Cell]: Possible moves from `pos`.
    """
    moves: List[Cell] = []
    # we can move up, down, left, right
    if pos.x > 0:
        moves.append(pos + Cell(-1, 0))
    if pos.x < N - 1:
        moves.append(pos + Cell(1, 0))
    if pos.y > 0:
        moves.append(pos + Cell(0, -1))
    if pos.y < N - 1:
        moves.append(pos + Cell(0, 1))
    return moves


def can_move(map_: List[List[Entity]], pos: Cell) -> bool:
    """Returns whether one can move into `pos`.
    Note: it checks only for obstacles and does not check for out of bounds.

    Args:
        map_ (List[List[Entity]]): Map.
        pos (Cell): Cell that one wants to move into.

    Returns:
        bool: Whether one can move into `pos`.
    """
    # we can move into a cell which does not contain obstacles
    return map_[pos.x][pos.y] not in (Entity.CAPTAIN_MARVEL, Entity.HULK, Entity.THOR, Entity.PERCEPTION, Entity.WALL)


def ask_to_move(map_: List[List[Entity]], pos: Cell) -> None:
    """Ask the interactor to move into `pos` and gather information about surroundings.

    Args:
        map_ (List[List[Entity]]): Map.
        pos (Cell): Cell that one wants to move into.
    """
    print(f"m {pos.x} {pos.y}")
    n = int(input())
    for _ in range(n):
        x, y, e = input().split()
        map_[int(x)][int(y)] = Entity(e)


path_to_goal: List[Cell] = []  # contains the shortest path to our goal (infinity stone)
path_to_shield: List[Cell] = []  # contains the shortest path to the shield
visited = [[False for _ in range(N)] for _ in range(N)]  # keeping track of visited cells


def dfs(
    map_: List[List[Entity]],
    start: Cell,
    goal: Cell,
    path: List[Cell],
    reset_visited: bool = True,
) -> None:
    """Explores recursively the `map_` using the interactor.

    Stores the first found path to `goal` in global variable `path_to_goal`
    (if it is shorter than the current value of `path_to_goal`).

    Stores the first found path to the shield in global variable `path_to_shield`.
    (if it is shorter than the current value of `path_to_shield`).

    Keeps track of visited cells in global variable `visited`.

    Args:
        map_ (List[List[Entity]]): Map.
        start (Cell): Source cell.
        goal (Cell): Destination cell.
        path (List[Cell]): Current path.
        reset_visited (bool, optional): Whether to reset `visited` variable. Defaults to True.
    """
    global path_to_goal, path_to_shield, visited

    if reset_visited:
        visited = [[False for _ in range(N)] for _ in range(N)]

    # visit a new cell
    visited[start.x][start.y] = True
    # add it to our current path
    path.append(start)
    # ask the interactor about the surroundings
    ask_to_move(map_, start)

    # when we reach our destination we can update the path to it and exit the exploration
    if start == goal:
        if not path_to_goal or len(path) < len(path_to_goal):
            path_to_goal = path.copy()
        return

    # move into neighbouring cells
    for new_cell in sorted(possible_moves(start), key=goal.manhattan):
        # check that we did not visit it
        if visited[new_cell.x][new_cell.y]:
            continue
        # check that we can move there and not meet enemies
        if not can_move(map_, new_cell):
            continue
        # if we encounter a shield
        if map_[new_cell.x][new_cell.y] == Entity.SHIELD:
            # update the path to it
            if not path_to_shield or len(path) + 1 < len(path_to_shield):
                path_to_shield = path.copy() + [new_cell]
            # mark it as visited
            visited[new_cell.x][new_cell.y] = True
            # do not grab it
            continue

        # explore the neigbouring cell
        dfs(map_, new_cell, goal, path, False)

        # backtracking into `start`
        ask_to_move(map_, start)
        path.append(start)


def dfs_shortest(
    map_: List[List[Entity]],
    start: Cell,
    goal: Cell,
    path: List[Cell],
    reset_visited: bool = True,
    update_goal: bool = True,
    can_visit_shield: bool = True,
) -> None:
    """Traverses recursively the `map_` without using the interactor.

    Stores the shortest path to `goal` in global variable `path_to_goal`

    Stores the shortest path to the shield in global variable `path_to_shield`.

    Keeps track of visited cells in global variable `visited`.

    Args:
        map_ (List[List[Entity]]): Map.
        start (Cell): Source cell.
        goal (Cell): Destination cell.
        path (List[Cell]): Current path.
        reset_visited (bool, optional): Whether to reset `visited` variable. Defaults to True.
        update_goal (bool, optional): Whether to update `path_to_goal` variable. Defaults to True.
        can_visit_shield (bool, optional): Whether can go into a cell with a shield. Defaults to True.
    """
    global path_to_goal, path_to_shield, visited

    if reset_visited:
        visited = [[False for _ in range(N)] for _ in range(N)]

    # visit a new cell
    visited[start.x][start.y] = True
    # add it to our current path
    path.append(start)

    # when we reach our destination we can update the path to it and continue the exploitation
    if start == goal:
        if not path_to_goal or len(path) < len(path_to_goal):
            if update_goal:
                path_to_goal = path.copy()
    elif not path_to_goal or len(path) < len(path_to_goal) - 1:
        # visit neighbours in such manner that we check the ones with smaller distance first
        for new_cell in sorted(possible_moves(start), key=goal.manhattan):
            # check that we did not visit it
            if visited[new_cell.x][new_cell.y]:
                continue
            # check that we can move there and not meet enemies
            if not can_move(map_, new_cell):
                continue
            # if we encounter a shield
            if map_[new_cell.x][new_cell.y] == Entity.SHIELD:
                # update the path to it
                if not path_to_shield or len(path) + 1 < len(path_to_shield):
                    path_to_shield = path.copy() + [new_cell]
                # do not grab it
                if not can_visit_shield:
                    continue

            # exploit the neighbour
            dfs_shortest(map_, new_cell, goal, path, False, update_goal)

    # backtracking
    # unmark the cell, so we can visit it in the future
    visited[start.x][start.y] = False
    # remove the cell from path
    path.pop()


def main():
    global path_to_goal, path_to_shield

    variant_number = int(input())
    x, y = map(int, input().split())
    goal = Cell(x, y)
    start = Cell(0, 0)
    shield = Cell(-1, -1)

    # first we explore the map from start without picking up the shield
    without_shield_map = [[Entity.EMPTY for _ in range(N)] for _ in range(N)]
    dfs(without_shield_map, start, goal, [])

    # find the location if the shield if found
    for i in range(N):
        for j in range(N):
            if without_shield_map[i][j] == Entity.SHIELD:
                shield = Cell(i, j)

    # if we have reached the goal then we can find the shortest path to it (explore then exploit)
    if visited[goal.x][goal.y]:
        dfs_shortest(without_shield_map, start, goal, [])

    # if we have found the shield in the first exploration
    if shield != Cell(-1, -1) and path_to_shield:
        with_shield_map = [x[:] for x in without_shield_map]

        # move to the shield
        for cell in path_to_shield[:-1]:
            ask_to_move(with_shield_map, cell)

        # remove the perception zones from our map
        # perception zone for Captain Marvel will reappear as we use the interactor
        for i in range(N):
            for j in range(N):
                if with_shield_map[i][j] == Entity.PERCEPTION:
                    with_shield_map[i][j] = Entity.EMPTY

        # explore the map with the shield from its location
        dfs(with_shield_map, shield, goal, path_to_shield[:-1])

        # if we have reached the goal then we can find the shortest path to it (explore then exploit)
        if visited[goal.x][goal.y]:
            # first we find the shortest path to the shield
            dfs_shortest(without_shield_map, start, shield, [], update_goal=False)
            # then we find the shortest path from the shield to the goal
            dfs_shortest(with_shield_map, shield, goal, path_to_shield[:-1])
    # print the length of the shortest path from `start` to `goal`
    # note: if path_to_goal is empty, then -1 will be printed
    print(f"e {len(path_to_goal) - 1}")


if __name__ == "__main__":
    main()
