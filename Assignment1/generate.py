import time
from random import randint, seed
from typing import Tuple
from map import Map, Actors
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


def create_shield(captain_marvel: Tuple[int, int], hulk: Tuple[int, int], thor: Tuple[int, int]) -> Tuple[int, int]:
    while True:
        shield = (randint(0, 8), randint(0, 8))
        if (
            not in_von_neumann(shield, captain_marvel, 2)
            and not in_von_neumann(shield, hulk, 1)
            and not in_moore(shield, thor)
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

    m = Map(infinity_stone)
    m.put(thor, Actors.THOR)
    m.put(hulk, Actors.HULK)
    m.put(captain_marvel, Actors.CAPTAIN_MARVEL)
    m.put(shield, Actors.SHIELD)

    return m


def main():
    m = create_map()
    print(m)


if __name__ == "__main__":
    main()
