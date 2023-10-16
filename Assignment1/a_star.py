from typing import Tuple, Set, List, Union, Dict, Callable
from map import Map
from map import Entity
from map import Direction


def heuristics(start: Tuple[int, int], goal: Tuple[int, int]) -> float:
    distance = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    return distance


def reconstruct_path(
    cameFrom: Dict[Tuple[int, int], Tuple[int, int]], current: Tuple[int, int]
) -> List[Tuple[int, int]]:
    total_path: List[Tuple[int, int]] = [current]
    while current in cameFrom.keys():
        current = cameFrom[current]
        total_path = [current] + total_path
    return total_path


def a_star(
    map_: Map,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    h: Callable[[Tuple[int, int], Tuple[int, int]], float],
    shielded: bool,
    n: int = 9,
) -> List[Tuple[int, int]]:
    """
    Direct translation of pseudocode from https://en.wikipedia.org/wiki/A*_search_algorithm
    """
    # The set of discovered nodes that may need to be (re-)expanded.
    # Initially, only the start node is known.
    # This is usually implemented as a min-heap or priority queue rather than a hash-set.
    openSet: Set[Tuple[int, int]] = set()
    openSet.add(start)

    # For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from the start
    # to n currently known.
    cameFrom: Dict[Tuple[int, int], Tuple[int, int]] = {}

    # For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
    gScore: List[List[float]] = [[float("inf") for _ in range(n)] for _ in range(n)]
    gScore[start[0]][start[1]] = 0

    # For node n, fScore[n] := gScore[n] + h(n). fScore[n] represents our current best guess as to
    # how cheap a path could be from start to finish if it goes through n.
    fScore: List[List[float]] = [[float("inf") for _ in range(n)] for _ in range(n)]
    fScore[start[0]][start[1]] = h(start, goal)

    while openSet:
        # This operation can occur in O(Log(N)) time if openSet is a min-heap or a priority queue
        current = min(openSet, key=lambda x: fScore[x[0]][x[1]])
        if current == goal:
            return reconstruct_path(cameFrom, current)

        openSet.discard(current)
        for direction in Direction.PLUS_X, Direction.MINUS_Y, Direction.MINUS_X, Direction.PLUS_Y:
            can_go, neighbor = map_.can_move(current, direction, shielded)
            if not can_go:
                continue
            # d(current,neighbor) is the weight of the edge from current to neighbor
            # tentative_gScore is the distance from start to the neighbor through current
            tentative_gScore = gScore[current[0]][current[1]] + 1
            if tentative_gScore < gScore[neighbor[0]][neighbor[1]]:
                # This path to neighbor is better than any previous one. Record it!
                cameFrom[neighbor] = current
                gScore[neighbor[0]][neighbor[1]] = tentative_gScore
                fScore[neighbor[0]][neighbor[1]] = tentative_gScore + h(neighbor, goal)
                if neighbor not in openSet:
                    openSet.add(neighbor)

    # Open set is empty but goal was never reached
    return []


def main():
    # variant_number = int(input())
    # x, y = map(int, input().split())
    # infinity_stone = (x, y)
    # map_ = Map()
    # map_.put(infinity_stone, Entity.INFINITY_STONE)
    variant_number = 1
    map_ = Map()
    map_.load("local_tests/1.txt")
    infinity_stone = map_.get_location(Entity.INFINITY_STONE)
    path = a_star(map_, (0, 0), infinity_stone, heuristics, False)
    print(path)
    for cell in path:
        map_.put(cell, Entity.PATH)
    print(map_)


if __name__ == "__main__":
    main()
