from typing import Tuple, List
from enum import Enum


class Actors(str, Enum):
    HULK = "H"
    INFINITY_STONE = "I"
    THOR = "T"
    CAPTAIN_MARVEL = "M"
    SHIELD = "S"
    THANOS = "A"
    EMPTY = "."


# class Direction(Enum):
#     PLUS_Y = (0, 1)
#     MINUS_Y = (0, -1)
#     PLUS_X = (1, 0)
#     MINUS_X = (-1, 0)


class Map:
    """Map looks like this:
    (0, 0)------(n, 0)> +x
      |
      |
      |
    (0, n)
      V +y
    """

    __n = 9  # size of the map

    def __init__(self, infinity_stone: Tuple[int, int]):
        """Initialize an unknown map with an infinity stone.

        Args:
            infinity_stone (Tuple[int, int]): Coordinates of infinity stone (x, y)
        """
        assert 0 <= infinity_stone[0] <= 8 and 0 <= infinity_stone[1] <= 8, "Infinity stone is out of the map"

        self.__map: List[List[Actors]] = [
            [Actors.EMPTY for _ in range(self.__n)] for _ in range(self.__n)
        ]  # map itself
        self.__thanos = [0, 0]
        self.__map[self.__thanos[1]][self.__thanos[0]] = Actors.THANOS
        self.__map[infinity_stone[1]][infinity_stone[0]] = Actors.INFINITY_STONE

    def put(self, cell: Tuple[int, int], actor: Actors) -> None:
        assert 0 <= cell[0] <= 8 and 0 <= cell[1] <= 8, f"Cell {cell} is out of the map"
        if actor != Actors.EMPTY:
            for row in self.__map:
                assert actor not in row, f"Actor {actor} is present in the map"
        assert self.__map[cell[1]][cell[0]] == Actors.EMPTY, f"Cell {cell} is occupied by another actor"

        self.__map[cell[1]][cell[0]] = actor

    # def moveThanos(self, direction: Direction):
    #     if direction == Direction.MINUS_X:
    #         assert self.__thanos[0] > 0, "Thanos will be out of the map"
    #     if direction == Direction.PLUS_X:
    #         assert self.__thanos[0] < self.__n, "Thanos will be out of the map"
    #     if direction == Direction.MINUS_Y:
    #         assert self.__thanos[1] > 0, "Thanos will be out of the map"
    #     if direction == Direction.PLUS_Y:
    #         assert self.__thanos[1] < self.__n, "Thanos will be out of the map"

    #     self.__map[self.__thanos[1]][self.__thanos[0]] = Actors.EMPTY
    #     self.__thanos[0] += direction.value[0]
    #     self.__thanos[1] += direction.value[1]

    #     assert self.__map[self.__thanos[1]][self.__thanos[0]] == Actors.EMPTY, "Cell is occupied by another actor"

    #     self.__map[self.__thanos[1]][self.__thanos[0]] = Actors.THANOS

    def __str__(self) -> str:
        output = ""
        for row in self.__map:
            output += " ".join(row) + "\n"
        return output


def main():
    m = Map((2, 3))
    m.put((1, 2), Actors.HULK)
    print(m)
    # for _ in range(7):
    #     m.moveThanos(Direction.PLUS_X)
    # print(m)
    # for _ in range(7):
    #     m.moveThanos(Direction.PLUS_Y)
    # print(m)
    # for _ in range(7):
    #     m.moveThanos(Direction.MINUS_X)
    # print(m)
    # for _ in range(7):
    #     m.moveThanos(Direction.MINUS_Y)
    # print(m)


if __name__ == "__main__":
    main()
