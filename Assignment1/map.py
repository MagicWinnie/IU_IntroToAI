from typing import Tuple, List
from enum import Enum
from neighbourhoods import in_moore, in_von_neumann, in_moore_with_ears


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
    (0, 0)——————(0, n)> +y
      |
      |
      |
    (n, 0)
      V +x
    """

    def __init__(self, n: int = 9):
        """Initialize an unknown map."""
        self.__n = n
        self.__map: List[List[Entity]] = [[Entity.EMPTY for _ in range(self.__n)] for _ in range(self.__n)]

    def put(self, cell: Tuple[int, int], entity: Entity) -> None:
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
            possible = self.__map[new_pos[0]][new_pos[1]] in (Entity.EMPTY, Entity.SHIELD, Entity.INFINITY_STONE)

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

    def remove_perception(self, entity: Entity):
        center = self.get_location(entity)
        for i in range(self.__n):
            for j in range(self.__n):
                if self.__map[i][j] != Entity.PERCEPTION:
                    continue
                if entity == Entity.HULK:
                    if in_von_neumann((i, j), center, 1):
                        self.__map[i][j] = Entity.EMPTY
                elif entity == Entity.CAPTAIN_MARVEL:
                    if in_von_neumann((i, j), center, 2):
                        self.__map[i][j] = Entity.EMPTY
                elif entity == Entity.THOR:
                    if in_moore((i, j), center):
                        self.__map[i][j] = Entity.EMPTY

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
        return output[:-1]


def main():
    m = Map()
    m.put((2, 3), Entity.INFINITY_STONE)
    m.put((1, 2), Entity.HULK)
    print(m)


if __name__ == "__main__":
    main()
