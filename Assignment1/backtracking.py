from typing import Tuple, List
from enum import Enum
from functools import lru_cache
from pprint import pprint


N = 9


class Entity(str, Enum):
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


def possible_moves(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
    moves: List[Tuple[int, int]] = []
    if pos[0] > 0:
        moves.append((pos[0] - 1, pos[1]))
    if pos[0] < N - 1:
        moves.append((pos[0] + 1, pos[1]))
    if pos[1] > 0:
        moves.append((pos[0], pos[1] - 1))
    if pos[1] < N - 1:
        moves.append((pos[0], pos[1] + 1))
    return moves


def can_move(map_: List[List[Entity]], pos: Tuple[int, int]) -> bool:
    return map_[pos[0]][pos[1]] in (Entity.INFINITY_STONE, Entity.SHIELD, Entity.EMPTY)


def ask_to_move(map_: List[List[Entity]], pos: Tuple[int, int]) -> None:
    print(f"m {pos[0]} {pos[1]}")
    n = int(input())
    for _ in range(n):
        x, y, e = input().split()
        cell = (int(x), int(y))
        entity = Entity(e)
        map_[cell[0]][cell[1]] = entity


path_to_goal: List[Tuple[int, int]] = []
path_to_shield: List[Tuple[int, int]] = []
visited = [[False for _ in range(N)] for _ in range(N)]


def dfs(
    map_: List[List[Entity]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    path: List[Tuple[int, int]] = [],
) -> None:
    global path_to_goal, path_to_shield, visited

    visited[start[0]][start[1]] = True
    path.append(start)
    ask_to_move(map_, start)

    if start == goal:
        if not path_to_goal or len(path) < len(path_to_goal):
            path_to_goal = path.copy()

    for new_cell in possible_moves(start):
        if visited[new_cell[0]][new_cell[1]]:
            continue
        if not can_move(map_, new_cell):
            continue
        if map_[new_cell[0]][new_cell[1]] == Entity.SHIELD:
            if not path_to_shield or len(path) + 1 < len(path_to_shield):
                path_to_shield = path.copy() + [new_cell]
            visited[new_cell[0]][new_cell[1]] = True
            continue

        dfs(map_, new_cell, goal, path)
        ask_to_move(map_, start)
        path.append(start)


# @lru_cache(maxsize=None)
def dfs_shortest(
    map_: List[List[Entity]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    path: List[Tuple[int, int]] = [],
) -> None:
    global path_to_goal, path_to_shield, visited

    visited[start[0]][start[1]] = True
    path.append(start)

    if start == goal:
        if not path_to_goal or len(path) < len(path_to_goal):
            path_to_goal = path.copy()
    elif (not path_to_goal or len(path) < len(path_to_goal)) and len(path) < N * N:
        for new_cell in sorted(possible_moves(start), key=lambda pt: (goal[0] - pt[0]) + (goal[1] - pt[1])):
            if visited[new_cell[0]][new_cell[1]]:
                continue
            if not can_move(map_, new_cell):
                continue
            if map_[new_cell[0]][new_cell[1]] == Entity.SHIELD:
                if not path_to_shield or len(path) + 1 < len(path_to_shield):
                    path_to_shield = path.copy() + [new_cell]
                continue

            dfs_shortest(map_, new_cell, goal, path)

    visited[start[0]][start[1]] = False
    path.pop()


def main():
    global path_to_goal, visited

    variant_number = int(input())
    x, y = map(int, input().split())
    goal = (x, y)
    start = (0, 0)

    shield = (-1, -1)

    without_shield_map = [[Entity.EMPTY for _ in range(N)] for _ in range(N)]
    dfs(without_shield_map, start, goal)  # explore map from start without picking up shield
    for i in range(N):
        for j in range(N):
            if without_shield_map[i][j] == Entity.SHIELD:
                shield = (i, j)
    if visited[goal[0]][goal[1]]:
        visited = [[False for _ in range(N)] for _ in range(N)]
        # print("DFS SHORT 1", file=open("backtracking.log", "a"))
        dfs_shortest(without_shield_map, start, goal)

    if shield != (-1, -1):
        with_shield_map = [x[:] for x in without_shield_map]
        # move to shield
        for cell in path_to_shield[:-1]:
            ask_to_move(with_shield_map, cell)
        # remove perception zones from map
        for i in range(N):
            for j in range(N):
                if with_shield_map[i][j] == Entity.PERCEPTION:
                    with_shield_map[i][j] = Entity.EMPTY
        visited = [[False for _ in range(N)] for _ in range(N)]
        dfs(with_shield_map, shield, goal)  # explore map from shield
        # print("PT 1", file=open("backtracking.log", "a"))
        if visited[goal[0]][goal[1]]:
            visited = [[False for _ in range(N)] for _ in range(N)]
            # find shortest path to shield
            # print("DFS SHORT 2", file=open("backtracking.log", "a"))
            dfs_shortest(with_shield_map, start, shield)
            # print("PT 2", file=open("backtracking.log", "a"))

            visited = [[False for _ in range(N)] for _ in range(N)]
            # find shortest path to goal
            # print("DFS SHORT 3", file=open("backtracking.log", "a"))
            dfs_shortest(with_shield_map, shield, goal, path_to_shield[:-1])
            # print("PT 3", file=open("backtracking.log", "a"))

    # for cell in path_to_goal:
    #     map_[cell[0]][cell[1]] = Entity.PATH
    # for row in map_:
    #     print(" ".join(row), file=open("backtracking.log", "a"))
    # print("-" * 100, file=open("backtracking.log", "a"))

    # print(path_to_goal, file=open("backtracking.log", "a"))
    print(f"e {len(path_to_goal) - 1}")


if __name__ == "__main__":
    main()
