from typing import Tuple, List
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
    # print("[INTERACTOR] Move to", pos, file=open("backtracking.log", "a"))
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

    # print(start, file=open("backtracking.log", "a"))
    # for row in map_:
    #     print(" ".join(row), file=open("backtracking.log", "a"))
    # print(file=open("backtracking.log", "a"))
    visited[start[0]][start[1]] = True
    path.append(start)
    ask_to_move(map_, start)

    if start == goal:
        if not path_to_goal or len(path) < len(path_to_goal):
            # print("HERE", path, file=open("backtracking.log", "a"))
            path_to_goal = path.copy()
    elif (not path_to_goal or len(path) < len(path_to_goal)) and len(path) < N * N:
        for new_cell in possible_moves(start):
            if visited[new_cell[0]][new_cell[1]]:
                continue
            if not can_move(map_, new_cell):
                continue
            if map_[new_cell[0]][new_cell[1]] == Entity.SHIELD:
                if not path_to_shield or len(path) + 1 < len(path_to_shield):
                    path_to_shield = path.copy() + [new_cell]
                continue

            dfs(map_, new_cell, goal, path)
            ask_to_move(map_, start)

    visited[start[0]][start[1]] = False
    path.pop()


def main():
    global path_to_goal

    map_: List[List[Entity]] = [[Entity.EMPTY for _ in range(N)] for _ in range(N)]

    variant_number = int(input())
    x, y = map(int, input().split())
    goal = (x, y)
    start = (0, 0)

    ask_to_move(map_, start)

    if next(filter(lambda x: can_move(map_, x), possible_moves(start)), None) is None:
        print("e -1")
        return

    dfs(map_, start, goal)
    # print(path_to_goal, path_to_shield, file=open("backtracking.log", "a"))
    if path_to_shield:
        pre_path = path_to_shield[:-1]
        for cell in path_to_shield:
            ask_to_move(map_, cell)
        for i in range(N):
            for j in range(N):
                if map_[i][j] == Entity.PERCEPTION:
                    map_[i][j] = Entity.EMPTY
        dfs(map_, path_to_shield[-1], goal, pre_path)

    # for cell in path_to_goal:
    #     map_[cell[0]][cell[1]] = Entity.PATH
    # for row in map_:
    #     print(" ".join(row), file=open("backtracking.log", "a"))
    # print("-" * 100, file=open("backtracking.log", "a"))

    print(f"e {len(path_to_goal) - 1}")


if __name__ == "__main__":
    main()
