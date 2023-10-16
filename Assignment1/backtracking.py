from typing import Tuple, Set, List, Union
from map import Map
from map import Entity
from map import Direction


min_path: List[Tuple[int, int]] = []


def backtrack(map_: Map, shielded: bool, path: List[Tuple[int, int]]):
    global min_path
    current = path[-1]
    if map_.get(current) == Entity.INFINITY_STONE:
        if len(min_path) == 0 or len(path) < len(min_path):
            min_path = path
        return
    if len(min_path) > 0 and len(path) > len(min_path):
        return

    if map_.get(current) == Entity.SHIELD:
        shielded = True

    for direction in Direction.PLUS_X, Direction.MINUS_Y, Direction.MINUS_X, Direction.PLUS_Y:
        can_go = map_.can_move(current, direction, shielded)
        if can_go[0] and can_go[1] not in path:
            print(f"m {can_go[1][0]} {can_go[1][1]}")
            n = int(input())
            for _ in range(n):
                x, y, e = input().split()
                map_.put((int(x), int(y)), Entity(e))
            backtrack(map_, shielded, path + [can_go[1]])
            print(f"m {current[0]} {current[1]}")
            n = int(input())
            for _ in range(n):
                x, y, e = input().split()
                map_.put((int(x), int(y)), Entity(e))


def main():
    variant_number = int(input())
    x, y = map(int, input().split())
    infinity_stone = (x, y)
    map_ = Map()
    map_.put(infinity_stone, Entity.INFINITY_STONE)
    backtrack(map_, False, [(0, 0)])
    print(f"e {len(min_path) - 1}")


if __name__ == "__main__":
    main()
