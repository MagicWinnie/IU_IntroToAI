from typing import Tuple, List, Dict
from copy import deepcopy
from enum import Enum


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


class Direction(Enum):
    PLUS_Y = (0, 1)
    MINUS_Y = (0, -1)
    PLUS_X = (1, 0)
    MINUS_X = (-1, 0)


def possible_moves(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
    moves: List[Tuple[int, int]] = []
    if pos[0] > 0:
        moves.append((pos[0] + Direction.MINUS_X.value[0], pos[1] + Direction.MINUS_X.value[1]))
    if pos[0] < N - 1:
        moves.append((pos[0] + Direction.PLUS_X.value[0], pos[1] + Direction.PLUS_X.value[1]))
    if pos[1] > 0:
        moves.append((pos[0] + Direction.MINUS_Y.value[0], pos[1] + Direction.MINUS_Y.value[1]))
    if pos[1] < N - 1:
        moves.append((pos[0] + Direction.PLUS_Y.value[0], pos[1] + Direction.PLUS_Y.value[1]))
    return moves


def can_move(pos: Tuple[int, int]) -> bool:
    return map_[pos[0]][pos[1]] in (Entity.INFINITY_STONE, Entity.SHIELD, Entity.EMPTY)


map_: List[List[Entity]] = [[Entity.EMPTY for _ in range(N)] for _ in range(N)]
min_path: List[Tuple[int, int]] = []


def backtrack(goal: Tuple[int, int], path: List[Tuple[int, int]]):
    global min_path

    current = path[-1]
    if current == goal:
        if len(min_path) == 0 or len(path) < len(min_path):
            min_path = path
        return
    if len(min_path) > 0 and len(path) >= len(min_path):
        return
    if len(path) > 81:
        return

    for new_cell in possible_moves(current):
        if new_cell in path:
            continue
        if not can_move(new_cell):
            continue

        print(f"m {new_cell[0]} {new_cell[1]}")
        n = int(input())
        for _ in range(n):
            x, y, e = input().split()
            cell = (int(x), int(y))
            entity = Entity(e)
            map_[cell[0]][cell[1]] = entity

        backtrack(goal, path + [new_cell])

        print(f"m {current[0]} {current[1]}")
        n = int(input())
        for _ in range(n):
            x, y, e = input().split()
            cell = (int(x), int(y))
            entity = Entity(e)
            map_[cell[0]][cell[1]] = entity


def main():
    variant_number = int(input())
    x, y = map(int, input().split())
    infinity_stone = (x, y)
    goal = infinity_stone
    print(f"m {0} {0}")
    n = int(input())
    for _ in range(n):
        x, y, e = input().split()
        cell = (int(x), int(y))
        entity = Entity(e)
        map_[cell[0]][cell[1]] = entity
    if len(list(filter(lambda x: can_move(x), possible_moves((0, 0))))) > 0:
        backtrack(goal, [(0, 0)])
    print(f"e {len(min_path) - 1}")


if __name__ == "__main__":
    main()
