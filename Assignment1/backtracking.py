from typing import Tuple, List
from enum import Enum


def in_moore(point: Tuple[int, int], center: Tuple[int, int], r: int = 1) -> bool:
    return abs(point[0] - center[0]) <= r and abs(point[1] - center[1]) <= r


def in_von_neumann(point: Tuple[int, int], center: Tuple[int, int], r: int) -> bool:
    return abs(point[0] - center[0]) + abs(point[1] - center[1]) <= r


def in_moore_with_ears(point: Tuple[int, int], center: Tuple[int, int], r: int = 1) -> bool:
    return in_moore(point, center, r) or (abs(point[0] - center[0]) == r + 1 and abs(point[1] - center[1]) == r + 1)


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


class Map:
    """Map looks like this:
    (0, 0)------(0, n)> +y
      |
      |
      |
    (n, 0)
      V +x
    """

    def __init__(self, n: int = 9):
        """Initialize an unknown map."""
        self.__n = n
        self.__map: List[List[Entity]] = [
            [Entity.EMPTY for _ in range(self.__n)] for _ in range(self.__n)
        ]  # map itself

    def put(self, cell: Tuple[int, int], entity: Entity) -> None:
        assert 0 <= cell[0] <= self.__n and 0 <= cell[1] <= self.__n, f"Cell {cell} is out of the map"
        if entity != Entity.EMPTY and entity != Entity.PERCEPTION and entity != Entity.PATH:
            if self.__map[cell[0]][cell[1]] == entity:
                return
            for row in self.__map:
                assert entity not in row, f"Entity {entity} is present in the map"

        if entity == Entity.PERCEPTION and self.__map[cell[0]][cell[1]] != Entity.EMPTY:
            return

        self.__map[cell[0]][cell[1]] = entity

        if entity in (Entity.HULK, Entity.CAPTAIN_MARVEL, Entity.THOR):
            self.__populate_perception(entity, cell)

    def get(self, cell: Tuple[int, int]) -> Entity:
        assert 0 <= cell[0] <= self.__n and 0 <= cell[1] <= self.__n, f"Cell {cell} is out of the map"
        return self.__map[cell[0]][cell[1]]

    def get_location(self, entity: Entity) -> Tuple[int, int]:
        for i in range(self.__n):
            for j in range(self.__n):
                if self.__map[i][j] == entity:
                    return (i, j)
        raise ValueError(f"Entity {entity} is not found")

    def can_move(self, pos: Tuple[int, int], direction: Direction, shielded: bool) -> Tuple[bool, Tuple[int, int]]:
        possible = False
        if direction == Direction.MINUS_X:
            possible = pos[0] > 0
        elif direction == Direction.PLUS_X:
            possible = pos[0] < self.__n - 1
        elif direction == Direction.MINUS_Y:
            possible = pos[1] > 0
        elif direction == Direction.PLUS_Y:
            possible = pos[1] < self.__n - 1

        new_pos = (pos[0] + direction.value[0], pos[1] + direction.value[1])
        if possible:
            possible = self.__map[new_pos[0]][new_pos[1]] in [Entity.EMPTY, Entity.SHIELD, Entity.INFINITY_STONE] + (
                [Entity.PERCEPTION] if shielded else []
            )

        return (possible, new_pos)

    def __populate_perception(self, entity: Entity, center: Tuple[int, int]):
        for i in range(self.__n):
            for j in range(self.__n):
                if self.__map[i][j] != Entity.EMPTY:
                    continue
                if entity == Entity.HULK:
                    if in_von_neumann((i, j), center, 1):
                        self.__map[i][j] = Entity.PERCEPTION
                elif entity == Entity.CAPTAIN_MARVEL:
                    if in_von_neumann((i, j), center, 2):
                        self.__map[i][j] = Entity.PERCEPTION
                elif entity == Entity.THOR:
                    if in_moore((i, j), center):
                        self.__map[i][j] = Entity.PERCEPTION

    def get_surroundings(self, perception: int, cell: Tuple[int, int]) -> List[Tuple[Tuple[int, int], Entity]]:
        output = []
        for i in range(self.__n):
            for j in range(self.__n):
                if self.__map[i][j] == Entity.EMPTY:
                    continue
                if perception == 1:
                    if in_moore((i, j), cell):
                        output.append(((i, j), self.__map[i][j]))
                elif perception == 2:
                    if in_moore_with_ears((i, j), cell):
                        output.append(((i, j), self.__map[i][j]))
        return output

    def load(self, path: str) -> None:
        with open(path) as fp:
            for i, line in enumerate(fp):
                for j, entity in enumerate(line.split()):
                    if entity != Entity.EMPTY:
                        self.put((i, j), Entity(entity))

    def __str__(self) -> str:
        output = ""
        for row in self.__map:
            output += " ".join(row) + "\n"
        return output


min_path: List[Tuple[int, int]] = []
FOUND = {
    Entity.THOR: False,
    Entity.HULK: False,
}


def backtrack(map_: Map, shielded: bool, path: List[Tuple[int, int]]):
    global min_path
    current = path[-1]
    if map_.get(current) == Entity.INFINITY_STONE:
        if len(min_path) == 0 or len(path) < len(min_path):
            min_path = path
        return
    if len(min_path) > 0 and len(path) >= len(min_path):
        return

    if map_.get(current) == Entity.SHIELD:
        shielded = True

    for direction in Direction.PLUS_X, Direction.MINUS_Y, Direction.MINUS_X, Direction.PLUS_Y:
        can_go, new_cell = map_.can_move(current, direction, shielded)
        if can_go and new_cell not in path:
            print(f"m {new_cell[0]} {new_cell[1]}")
            n = int(input())
            for _ in range(n):
                x, y, e = input().split()
                map_.put((int(x), int(y)), Entity(e))
                if Entity(e) == Entity.HULK:
                    FOUND[Entity.HULK] = True
                if Entity(e) == Entity.THOR:
                    FOUND[Entity.THOR] = True
            backtrack(map_, shielded, path + [new_cell])
            print(f"m {current[0]} {current[1]}")
            n = int(input())
            for _ in range(n):
                x, y, e = input().split()
                map_.put((int(x), int(y)), Entity(e))
                if Entity(e) == Entity.HULK:
                    FOUND[Entity.HULK] = True
                if Entity(e) == Entity.THOR:
                    FOUND[Entity.THOR] = True


def main():
    variant_number = int(input())
    x, y = map(int, input().split())
    infinity_stone = (x, y)
    map_ = Map()
    map_.put(infinity_stone, Entity.INFINITY_STONE)
    print(f"m {0} {0}")
    n = int(input())
    for _ in range(n):
        x, y, e = input().split()
        map_.put((int(x), int(y)), Entity(e))
    backtrack(map_, False, [(0, 0)])
    print(f"e {len(min_path) - 1}")


if __name__ == "__main__":
    main()
