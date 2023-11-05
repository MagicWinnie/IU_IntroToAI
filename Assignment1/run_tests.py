import os
import re
import glob
import time
import subprocess
from random import randint
from typing import Tuple, List
from argparse import ArgumentParser, Namespace


N = 9  # size of the map (NxN)
DASH_LENGTH = 50
FILE_PATTERN = re.compile(r".*?(\d+).*?")


def m_dist(this, other) -> int:
    return abs(this[0] - other[0]) + abs(this[1] - other[1])


def moore_perception_zone(point, center, r=1) -> bool:
    return abs(point[0] - center[0]) <= r and abs(point[1] - center[1]) <= r


def moore_corner_perception_zone(point, center, r=1) -> bool:
    return moore_perception_zone(point, center, r) or (
        abs(point[0] - center[0]) == r + 1 and abs(point[1] - center[1]) == r + 1
    )


def vonneumann_perception_zone(point, center, r) -> bool:
    return m_dist(point, center) <= r


def remove_perception(map_):
    for i in range(N):
        for j in range(N):
            if map_[i][j] == "P":
                map_[i][j] = "."


def get_surroundings(map_, perception, cell) -> List[Tuple[Tuple[int, int], str]]:
    output = []
    for i in range(N):
        for j in range(N):
            if map_[i][j] == ".":
                continue
            if perception == 1:
                if moore_perception_zone((i, j), cell):
                    output.append(((i, j), map_[i][j]))
            elif perception == 2:
                if moore_corner_perception_zone((i, j), cell):
                    output.append(((i, j), map_[i][j]))
    return output


def illegal_move(msg, curr, future):
    print(f"[ERROR] {msg}:")
    print("-" * DASH_LENGTH)
    print("Tried to move to cell:")
    print(future)
    print("From cell:")
    print(curr)
    print("-" * DASH_LENGTH)


def get_order(file):
    match = FILE_PATTERN.match(os.path.splitext(os.path.basename(file))[0])
    if not match:
        return float("inf")
    return int(match.groups()[0])


def kill(process):
    if os.name == "nt":  # Windows
        subprocess.Popen(
            "TASKKILL /F /PID {pid} /T".format(pid=process.pid),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        import signal

        os.kill(process.pid, signal.SIGTERM)


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

    if os.path.isdir(args.tests):
        tests = glob.glob(os.path.join(args.tests, "*.txt"))
    else:
        tests = [args.tests]

    with open(args.output, "w") as fp:
        fp.write("TEST,ANSWER,TIME\n")

        for test in sorted(tests, key=get_order):
            print("-" * (DASH_LENGTH // 2) + test + "-" * (DASH_LENGTH // 2))

            print("[INFO] Current map:")
            map_ = [["." for _ in range(N)] for _ in range(N)]
            infinity_stone = (-1, -1)
            captain_marvel = (-1, -1)
            with open(test, "r") as test_fp:
                for i, line in enumerate(test_fp):
                    for j, entity in enumerate(line.split()):
                        if entity not in ".PSIHTM":
                            print("[ERROR] Incorrect entity in the map")
                            exit(1)
                        if entity == "I":
                            infinity_stone = (i, j)
                        elif entity == "M":
                            captain_marvel = (i, j)
                        map_[i][j] = entity
                    print(" ".join(map_[i]))

            prev_cell = (0, 0)
            variant_number = args.variant if args.variant in (1, 2) else randint(1, 2)

            print("[INFO] Variant number:", variant_number)
            print("[INFO] Program output:")

            proc = subprocess.Popen(
                args.cmd.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if not proc.stdin or not proc.stdout or not proc.stderr:
                print("[ERROR] stdin, stdout, or stderr in subprocess.Popen is not assigned to subprocess.PIPE")
                kill(proc)
                exit(1)

            start_time = time.time()

            proc.stdin.write(f"{variant_number}\n".encode("ASCII"))
            proc.stdin.write(f"{infinity_stone[0]} {infinity_stone[1]}\n".encode("ASCII"))
            proc.stdin.flush()

            while True:
                try:
                    output = proc.stdout.readline().decode("UTF-8").strip()
                    if not output:
                        print("[ERROR] An exception was raised while running:")
                        print("-" * DASH_LENGTH)
                        lines = proc.stderr.readlines()
                        for line in lines:
                            print(line.decode("UTF-8").rstrip())
                        print("-" * DASH_LENGTH)

                        kill(proc)
                        exit(1)
                    output_splitted = output.split()
                    if (
                        len(output_splitted) == 3
                        and output_splitted[0] == "m"
                        and output_splitted[1].isdigit()
                        and output_splitted[2].isdigit()
                    ):
                        _, x, y = output.split()
                        move_cell = (int(x), int(y))
                        if m_dist(move_cell, prev_cell) > 1:
                            illegal_move("Can't teleport", prev_cell, move_cell)

                            kill(proc)
                            exit(1)
                        elif map_[move_cell[0]][move_cell[1]] in ("M", "H", "T"):
                            illegal_move("Can't move into a cell with Avengers", prev_cell, move_cell)

                            kill(proc)
                            exit(1)
                        elif map_[move_cell[0]][move_cell[1]] == "P":
                            illegal_move("Can't move into perception zone of Avengers", prev_cell, move_cell)

                            kill(proc)
                            exit(1)
                        else:
                            prev_cell = move_cell
                        if map_[move_cell[0]][move_cell[1]] == "S":
                            for i in range(N):
                                for j in range(N):
                                    if map_[i][j] == "P":
                                        map_[i][j] = "."
                            for i in range(N):
                                for j in range(N):
                                    if map_[i][j] != ".":
                                        continue
                                    if vonneumann_perception_zone((i, j), captain_marvel, 2):
                                        map_[i][j] = "P"

                        surroundings = get_surroundings(map_, variant_number, move_cell)
                        proc.stdin.write(f"{len(surroundings)}\n".encode("ASCII"))
                        for cell, entity in surroundings:
                            proc.stdin.write(f"{cell[0]} {cell[1]} {entity}\n".encode("ASCII"))
                        proc.stdin.flush()
                    elif (
                        len(output_splitted) == 2
                        and output_splitted[0] == "e"
                        and output_splitted[1].replace("-", "", 1).isdigit()
                    ):
                        print("[INFO] Answer:", output)
                        end_time = time.time()
                        fp.write(f"{test},{output.split()[1]},{end_time - start_time}\n")

                        kill(proc)
                        break
                    else:
                        print(output)
                except KeyboardInterrupt:
                    kill(proc)
                    exit(1)

            print("-" * (DASH_LENGTH + len(test)))


if __name__ == "__main__":
    main()
