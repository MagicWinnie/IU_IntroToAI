import os
import time
from enum import Enum
from typing import List, Set
from random import randint, seed
from argparse import ArgumentParser
from dataclasses import dataclass


N = 9  # size of the map (NxN)
seed(time.time())


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


@dataclass
class Cell:
    x: int
    y: int

    def __add__(self, other: "Cell") -> "Cell":
        return Cell(self.x + other.x, self.y + other.y)

    def manhattan(self, other: "Cell") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)


def in_moore(point: Cell, center: Cell, r: int = 1) -> bool:
    return abs(point.x - center.x) <= r and abs(point.y - center.y) <= r


def in_von_neumann(point: Cell, center: Cell, r: int) -> bool:
    return point.manhattan(center) <= r


def create_thor(thanos: Cell = Cell(0, 0)) -> Cell:
    while True:
        thor = Cell(randint(0, N - 1), randint(0, N - 1))
        if not in_moore(thanos, thor):
            return thor


def create_hulk(thor: Cell, thanos: Cell = Cell(0, 0)) -> Cell:
    while True:
        hulk = Cell(randint(0, N - 1), randint(0, N - 1))
        if thor != hulk and not in_von_neumann(thanos, hulk, 1):
            return hulk


def create_captain_marvel(hulk: Cell, thor: Cell, thanos: Cell = Cell(0, 0)) -> Cell:
    while True:
        captain_marvel = Cell(randint(0, N - 1), randint(0, N - 1))
        if hulk != captain_marvel and thor != captain_marvel and not in_von_neumann(thanos, captain_marvel, 2):
            return captain_marvel


def create_shield(captain_marvel: Cell, hulk: Cell, thor: Cell, thanos: Cell = Cell(0, 0)) -> Cell:
    while True:
        shield = Cell(randint(0, N - 1), randint(0, N - 1))
        if (
            not in_von_neumann(shield, captain_marvel, 2)
            and not in_von_neumann(shield, hulk, 1)
            and not in_moore(shield, thor)
            and shield != thanos
        ):
            return shield


def create_infinity_stone(
    shield: Cell,
    captain_marvel: Cell,
    hulk: Cell,
    thor: Cell,
    thanos: Cell = Cell(0, 0),
) -> Cell:
    while True:
        infinity_stone = Cell(randint(0, N - 1), randint(0, N - 1))
        if (
            not in_von_neumann(infinity_stone, captain_marvel, 2)
            and not in_von_neumann(infinity_stone, hulk, 1)
            and not in_moore(infinity_stone, thor)
            and infinity_stone != shield
            and infinity_stone != thanos
        ):
            return infinity_stone


def populate_perception(map_: List[List[Entity]], entity: Entity, center: Cell):
    for i in range(N):
        for j in range(N):
            if map_[i][j] != Entity.EMPTY:
                continue
            if entity == Entity.HULK:
                if in_von_neumann(Cell(i, j), center, 1):
                    map_[i][j] = Entity.PERCEPTION
            elif entity == Entity.CAPTAIN_MARVEL:
                if in_von_neumann(Cell(i, j), center, 2):
                    map_[i][j] = Entity.PERCEPTION
            elif entity == Entity.THOR:
                if in_moore(Cell(i, j), center):
                    map_[i][j] = Entity.PERCEPTION


def create_map() -> List[List[Entity]]:
    thor = create_thor()
    hulk = create_hulk(thor)
    captain_marvel = create_captain_marvel(hulk, thor)
    shield = create_shield(captain_marvel, hulk, thor)
    infinity_stone = create_infinity_stone(shield, captain_marvel, hulk, thor)

    map_ = [[Entity.EMPTY for _ in range(N)] for _ in range(N)]

    map_[thor.x][thor.y] = Entity.THOR
    populate_perception(map_, Entity.THOR, thor)

    map_[hulk.x][hulk.y] = Entity.HULK
    populate_perception(map_, Entity.HULK, hulk)

    map_[captain_marvel.x][captain_marvel.y] = Entity.CAPTAIN_MARVEL
    populate_perception(map_, Entity.CAPTAIN_MARVEL, captain_marvel)

    map_[shield.x][shield.y] = Entity.SHIELD
    map_[infinity_stone.x][infinity_stone.y] = Entity.INFINITY_STONE

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

        with open(os.path.join(args.output, f"test_{i}.txt"), "w") as fp:
            for row in map_:
                fp.write(" ".join(row) + "\n")


if __name__ == "__main__":
    main()
