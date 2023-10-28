import os
import re
import glob
import time
import subprocess
from enum import Enum
from random import randint
from typing import Tuple, List
from dataclasses import dataclass
from argparse import ArgumentParser, Namespace


N = 9  # size of the map (NxN)
DASH_LENGTH = 50
FILE_PATTERN = re.compile(r'.*?(\d+).*?')


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


def in_moore_with_ears(point: Cell, center: Cell, r: int = 1) -> bool:
    return in_moore(point, center, r) or (abs(point.x - center.x) == r + 1 and abs(point.y - center.y) == r + 1)


def in_von_neumann(point: Cell, center: Cell, r: int) -> bool:
    return point.manhattan(center) <= r


def remove_perception(map_: List[List[Entity]]):
    for i in range(N):
        for j in range(N):
            if map_[i][j] == Entity.PERCEPTION:
                map_[i][j] = Entity.EMPTY


def get_surroundings(map_: List[List[Entity]], perception: int, cell: Cell) -> List[Tuple[Cell, Entity]]:
    output: List[Tuple[Cell, Entity]] = []
    for i in range(N):
        for j in range(N):
            if map_[i][j] == Entity.EMPTY:
                continue
            if perception == 1:
                if in_moore(Cell(i, j), cell):
                    output.append((Cell(i, j), map_[i][j]))
            elif perception == 2:
                if in_moore_with_ears(Cell(i, j), cell):
                    output.append((Cell(i, j), map_[i][j]))
    return output


def illegal_move(msg: str, curr: Cell, future: Cell):
    print(f"[ERROR] {msg}:")
    print("-" * DASH_LENGTH)
    print("Tried to move to cell:")
    print(future)
    print("From cell:")
    print(curr)
    print("-" * DASH_LENGTH)


def get_order(file: str):
    match = FILE_PATTERN.match(os.path.splitext(os.path.basename(file))[0])
    if not match:
        return float('inf')
    return int(match.groups()[0])


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "-t",
        "--tests",
        type=str,
        help="Path to the tests folder or a single file",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--cmd",
        type=str,
        help='Command to execute program (e.g. "python3 main.py" or "./main.out")',
        required=True,
    )
    parser.add_argument(
        "-v",
        "--variant",
        type=int,
        help="Which perception variant to use for Thanos (randomly chosen if not 1 or not 2)",
        default=0,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output csv file",
        default="output.csv",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    fp = open(args.output, "w")
    fp.write("TEST,ANSWER,TIME\n")

    if os.path.isdir(args.tests):
        tests = glob.glob(os.path.join(args.tests, "*.txt"))
    else:
        tests = [args.tests]
    for test in sorted(tests, key=get_order):
        print("-" * (DASH_LENGTH // 2) + test + "-" * (DASH_LENGTH // 2))

        map_ = [[Entity.EMPTY for _ in range(N)] for _ in range(N)]
        infinity_stone = Cell(-1, -1)
        captain_marvel = Cell(-1, -1)
        with open(test, "r") as test_fp:
            for i, line in enumerate(test_fp):
                for j, e in enumerate(line.split()):
                    entity = Entity(e)
                    if entity == Entity.INFINITY_STONE:
                        infinity_stone = Cell(i, j)
                    elif entity == Entity.CAPTAIN_MARVEL:
                        captain_marvel = Cell(i, j)
                    map_[i][j] = entity
                print(" ".join(map_[i]))

        prev_cell = Cell(0, 0)
        variant_number = args.variant if args.variant in (1, 2) else randint(1, 2)

        print("Variant number:", variant_number)

        proc = subprocess.Popen(
            args.cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if not proc.stdin or not proc.stdout or not proc.stderr:
            print("[ERROR] stdin, stdout, or stderr in subprocess.Popen is not assigned to subprocess.PIPE")
            fp.close()
            exit(1)

        start_time = time.time()

        proc.stdin.write(f"{variant_number}\n".encode("ASCII"))
        proc.stdin.write(f"{infinity_stone.x} {infinity_stone.y}\n".encode("ASCII"))
        proc.stdin.flush()

        while True:
            output = proc.stdout.readline().decode("ASCII").strip()
            if not output:
                print("[ERROR] An exception was raised while running:")
                print("-" * DASH_LENGTH)
                for line in proc.stderr.readlines():
                    print(line.decode("ASCII").rstrip())
                print("-" * DASH_LENGTH)
                fp.close()
                exit(1)
            elif output[0] == "m":
                _, x, y = output.split()
                move_cell = Cell(int(x), int(y))
                if move_cell.manhattan(prev_cell) > 1:
                    illegal_move("Can't teleport", prev_cell, move_cell)
                    fp.close()
                    exit(1)
                elif map_[move_cell.x][move_cell.y] in (Entity.CAPTAIN_MARVEL, Entity.HULK, Entity.THOR):
                    illegal_move("Can't move into a cell with Avengers", prev_cell, move_cell)
                    fp.close()
                    exit(1)
                elif map_[move_cell.x][move_cell.y] == Entity.PERCEPTION:
                    illegal_move("Can't move into perception zone of Avengers", prev_cell, move_cell)
                    fp.close()
                    exit(1)
                else:
                    prev_cell = move_cell
                if map_[move_cell.x][move_cell.y] == Entity.SHIELD:
                    for i in range(N):
                        for j in range(N):
                            if map_[i][j] == Entity.PERCEPTION:
                                map_[i][j] = Entity.EMPTY
                    for i in range(N):
                        for j in range(N):
                            if map_[i][j] != Entity.EMPTY:
                                continue
                            if in_von_neumann(Cell(i, j), captain_marvel, 2):
                                map_[i][j] = Entity.PERCEPTION

                surroundings = get_surroundings(map_, variant_number, move_cell)
                proc.stdin.write(f"{len(surroundings)}\n".encode("ASCII"))
                for cell, entity in surroundings:
                    proc.stdin.write(f"{cell.x} {cell.y} {entity.value}\n".encode("ASCII"))
                proc.stdin.flush()
            elif output[0] == "e":
                print("Output:", output)
                end_time = time.time()
                fp.write(f"{test},{output.split()[1]},{end_time - start_time}\n")
                break

        print("-" * (DASH_LENGTH + len(test)))

    fp.close()


if __name__ == "__main__":
    main()
