import os
import time
from typing import Tuple, Set
from random import randint, seed
from argparse import ArgumentParser
from map import Map, Entity
from neighbourhoods import in_moore, in_von_neumann


seed(time.time())


def create_thor(thanos: Tuple[int, int] = (0, 0)) -> Tuple[int, int]:
    while True:
        thor = (randint(0, 8), randint(0, 8))
        if not in_moore(thanos, thor):
            return thor


def create_hulk(thor: Tuple[int, int], thanos: Tuple[int, int] = (0, 0)) -> Tuple[int, int]:
    while True:
        hulk = (randint(0, 8), randint(0, 8))
        if thor != hulk and not in_von_neumann(thanos, hulk, 1):
            return hulk


def create_captain_marvel(
    hulk: Tuple[int, int], thor: Tuple[int, int], thanos: Tuple[int, int] = (0, 0)
) -> Tuple[int, int]:
    while True:
        captain_marvel = (randint(0, 8), randint(0, 8))
        if hulk != captain_marvel and thor != captain_marvel and not in_von_neumann(thanos, captain_marvel, 2):
            return captain_marvel


def create_shield(
    captain_marvel: Tuple[int, int], hulk: Tuple[int, int], thor: Tuple[int, int], thanos: Tuple[int, int] = (0, 0)
) -> Tuple[int, int]:
    while True:
        shield = (randint(0, 8), randint(0, 8))
        if (
            not in_von_neumann(shield, captain_marvel, 2)
            and not in_von_neumann(shield, hulk, 1)
            and not in_moore(shield, thor)
            and shield != thanos
        ):
            return shield


def create_infinity_stone(
    shield: Tuple[int, int],
    captain_marvel: Tuple[int, int],
    hulk: Tuple[int, int],
    thor: Tuple[int, int],
    thanos: Tuple[int, int] = (0, 0),
) -> Tuple[int, int]:
    while True:
        infinity_stone = (randint(0, 8), randint(0, 8))
        if (
            not in_von_neumann(infinity_stone, captain_marvel, 2)
            and not in_von_neumann(infinity_stone, hulk, 1)
            and not in_moore(infinity_stone, thor)
            and infinity_stone != shield
            and infinity_stone != thanos
        ):
            return infinity_stone


def create_map() -> Map:
    thor = create_thor()
    hulk = create_hulk(thor)
    captain_marvel = create_captain_marvel(hulk, thor)
    shield = create_shield(captain_marvel, hulk, thor)
    infinity_stone = create_infinity_stone(shield, captain_marvel, hulk, thor)

    m = Map()
    m.put(thor, Entity.THOR)
    m.put(hulk, Entity.HULK)
    m.put(captain_marvel, Entity.CAPTAIN_MARVEL)
    m.put(shield, Entity.SHIELD)
    m.put(infinity_stone, Entity.INFINITY_STONE)

    return m


def main():
    parser = ArgumentParser()
    parser.add_argument("-n", "--num", type=int, help="Number of tests to generate", required=True)
    parser.add_argument("-o", "--output", type=str, help="Path to the directory to write test files", required=True)
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    created_maps: Set[str] = set()
    for i in range(args.num):
        while True:
            map_: Map = create_map()
            if str(map_) not in created_maps:
                created_maps.add(str(map_))
                break

        with open(os.path.join(args.output, f"test_{i}.txt"), "w") as fp:
            fp.write(str(map_))


if __name__ == "__main__":
    main()
