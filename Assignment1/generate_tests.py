import os
import time
from typing import List, Set
from random import randint, seed
from argparse import ArgumentParser


N = 9  # size of the map (NxN)
seed(time.time())


def m_dist(this, other) -> int:
    return abs(this[0] - other[0]) + abs(this[1] - other[1])


def moore_perception_zone(point, center, r=1) -> bool:
    return abs(point[0] - center[0]) <= r and abs(point[1] - center[1]) <= r


def vonneumann_perception_zone(point, center, r) -> bool:
    return m_dist(point, center) <= r


def create_thor(thanos=(0, 0)):
    while True:
        thor = (randint(0, N - 1), randint(0, N - 1))
        if not moore_perception_zone(thanos, thor):
            return thor


def create_hulk(thor, thanos=(0, 0)):
    while True:
        hulk = (randint(0, N - 1), randint(0, N - 1))
        if thor != hulk and not vonneumann_perception_zone(thanos, hulk, 1):
            return hulk


def create_captain_marvel(hulk, thor, thanos=(0, 0)):
    while True:
        captain_marvel = (randint(0, N - 1), randint(0, N - 1))
        if (
            hulk != captain_marvel
            and thor != captain_marvel
            and not vonneumann_perception_zone(thanos, captain_marvel, 2)
        ):
            return captain_marvel


def create_shield(captain_marvel, hulk, thor, thanos=(0, 0)):
    while True:
        shield = (randint(0, N - 1), randint(0, N - 1))
        if (
            not vonneumann_perception_zone(shield, captain_marvel, 2)
            and not vonneumann_perception_zone(shield, hulk, 1)
            and not moore_perception_zone(shield, thor)
            and shield != thanos
        ):
            return shield


def create_infinity_stone(shield, captain_marvel, hulk, thor, thanos=(0, 0)):
    while True:
        infinity_stone = (randint(0, N - 1), randint(0, N - 1))
        if (
            not vonneumann_perception_zone(infinity_stone, captain_marvel, 2)
            and not vonneumann_perception_zone(infinity_stone, hulk, 1)
            and not moore_perception_zone(infinity_stone, thor)
            and infinity_stone != shield
            and infinity_stone != thanos
        ):
            return infinity_stone


def populate_perception(map_, entity, center):
    for i in range(N):
        for j in range(N):
            if map_[i][j] != ".":
                continue
            if entity == "H":
                if vonneumann_perception_zone((i, j), center, 1):
                    map_[i][j] = "P"
            elif entity == "M":
                if vonneumann_perception_zone((i, j), center, 2):
                    map_[i][j] = "P"
            elif entity == "T":
                if moore_perception_zone((i, j), center):
                    map_[i][j] = "P"


def create_map() -> List[List[str]]:
    thor = create_thor()
    hulk = create_hulk(thor)
    captain_marvel = create_captain_marvel(hulk, thor)
    shield = create_shield(captain_marvel, hulk, thor)
    infinity_stone = create_infinity_stone(shield, captain_marvel, hulk, thor)

    map_ = [["." for _ in range(N)] for _ in range(N)]

    map_[thor[0]][thor[1]] = "T"
    populate_perception(map_, "T", thor)

    map_[hulk[0]][hulk[1]] = "H"
    populate_perception(map_, "H", hulk)

    map_[captain_marvel[0]][captain_marvel[1]] = "M"
    populate_perception(map_, "M", captain_marvel)

    map_[shield[0]][shield[1]] = "S"
    map_[infinity_stone[0]][infinity_stone[1]] = "I"

    return map_


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        help="Number of tests to generate",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the directory where to write test files",
        required=True,
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    created_maps: Set[str] = set()
    for i in range(args.num):
        while True:
            map_ = create_map()
            if str(map_) not in created_maps:
                created_maps.add(str(map_))
                break

        with open(os.path.join(args.output, f"{i}.txt"), "w") as fp:
            for row in map_:
                fp.write(" ".join(row) + "\n")


if __name__ == "__main__":
    main()
