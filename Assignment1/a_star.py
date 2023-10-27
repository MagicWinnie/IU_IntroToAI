from typing import Tuple, List, Dict, Callable
from enum import Enum
from queue import PriorityQueue
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


def heuristics(start: Tuple[int, int], goal: Tuple[int, int]) -> float:
    distance = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    return distance


def reconstruct_path(
    came_from: Dict[Tuple[int, int], Tuple[int, int]], current: Tuple[int, int]
) -> List[Tuple[int, int]]:
    total_path: List[Tuple[int, int]] = [current]
    while current in came_from.keys():
        current = came_from[current]
        total_path = [current] + total_path
    return total_path


def a_star(
    map_: List[List[Entity]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    h: Callable[[Tuple[int, int], Tuple[int, int]], float],
) -> List[Tuple[int, int]]:
    """
    Direct translation of pseudocode from https://en.wikipedia.org/wiki/A*_search_algorithm
    """
    # The set of discovered nodes that may need to be (re-)expanded.
    # Initially, only the start node is known.
    # This is usually implemented as a min-heap or priority queue rather than a hash-set.
    open_set = PriorityQueue()
    open_set.put((0, start))

    # For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from the start
    # to n currently known.
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

    # For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
    g_score: List[List[float]] = [[float("inf") for _ in range(N)] for _ in range(N)]
    g_score[start[0]][start[1]] = 0

    # For node n, fScore[n] := gScore[n] + h(n). fScore[n] represents our current best guess as to
    # how cheap a path could be from start to finish if it goes through n.
    f_score: List[List[float]] = [[float("inf") for _ in range(N)] for _ in range(N)]
    f_score[start[0]][start[1]] = h(start, goal)

    previous = (0, 0)
    while open_set:
        # This operation can occur in O(Log(N)) time if openSet is a min-heap or a priority queue
        _, current = open_set.get()
        if map_[current[0]][current[1]] == Entity.SHIELD:
            pass
        if current == goal:
            return reconstruct_path(came_from, current)

        for cell in reconstruct_path(came_from, previous)[::-1]:
            ask_to_move(map_, cell)
        for cell in reconstruct_path(came_from, current)[1:]:
            ask_to_move(map_, cell)
        ask_to_move(map_, current)

        previous = current

        for neighbor in possible_moves(current):
            if not can_move(map_, neighbor):
                continue
            # if map_[neighbor[0]][neighbor[1]] == Entity.SHIELD:
            #     continue

            # d(current,neighbor) is the weight of the edge from current to neighbor
            # tentative_gScore is the distance from start to the neighbor through current
            tentative_g_score = g_score[current[0]][current[1]] + 1
            if tentative_g_score < g_score[neighbor[0]][neighbor[1]]:
                # This path to neighbor is better than any previous one. Record it!
                came_from[neighbor] = current
                g_score[neighbor[0]][neighbor[1]] = tentative_g_score
                f_score[neighbor[0]][neighbor[1]] = tentative_g_score + h(neighbor, goal)
                open_set.put((f_score[neighbor[0]][neighbor[1]], neighbor))

    # Open set is empty but goal was never reached
    return []


def main():
    open("a_star.log", "w").close()

    map_: List[List[Entity]] = [[Entity.EMPTY for _ in range(N)] for _ in range(N)]

    variant_number = int(input())
    x, y = map(int, input().split())
    goal = (x, y)
    start = (0, 0)
    shield = (-1, -1)

    min_path = a_star(map_, start, goal, heuristics)
    print(f"e {len(min_path) - 1}")

    # for cell in min_path:
    #     map_[cell[0]][cell[1]] = Entity.PATH
    # for row in map_:
    #     print(" ".join(row), file=open("a_star.log", "a"))


if __name__ == "__main__":
    main()
