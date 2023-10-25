import os
import glob
import time
import subprocess
from random import randint
from argparse import ArgumentParser, Namespace
from map import Map, Entity


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


DASH_LENGTH = 50


def main():
    args = parse_args()

    fp = open(args.output, "w")
    fp.write("TEST,ANSWER,TIME\n")

    if os.path.isdir(args.tests):
        tests = glob.glob(os.path.join(args.tests, "*.txt"))
    else:
        tests = [args.tests]
    for test in sorted(tests):
        print("-" * (DASH_LENGTH // 2) + test + "-" * (DASH_LENGTH // 2))

        map_ = Map()
        map_.load(test)
        print(map_)

        prev_cell = (0, 0)
        variant_number = args.variant if args.variant in (1, 2) else randint(1, 2)
        infinity_stone = map_.get_location(Entity.INFINITY_STONE)

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
        proc.stdin.write(f"{infinity_stone[0]} {infinity_stone[1]}\n".encode("ASCII"))
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
                move_cell = (int(x), int(y))
                if abs(move_cell[0] - prev_cell[0]) + abs(move_cell[1] - prev_cell[1]) > 1:
                    print(f"[ERROR] Can't teleport:")
                    print("-" * DASH_LENGTH)
                    print("Tried to move to cell:")
                    print(move_cell)
                    print("From cell:")
                    print(prev_cell)
                    print("-" * DASH_LENGTH)
                    fp.close()
                    exit(1)
                elif map_.get(move_cell) in (Entity.CAPTAIN_MARVEL, Entity.HULK, Entity.THOR):
                    print(f"[ERROR] Can't move into a cell with Avengers:")
                    print("-" * DASH_LENGTH)
                    print("Tried to move to cell:")
                    print(move_cell)
                    print("From cell:")
                    print(prev_cell)
                    print("-" * DASH_LENGTH)
                    fp.close()
                    exit(1)
                elif map_.get(move_cell) == Entity.PERCEPTION:
                    print(f"[ERROR] Can't move into perception zone of Avengers:")
                    print("-" * DASH_LENGTH)
                    print("Tried to move to cell:")
                    print(move_cell)
                    print("From cell:")
                    print(prev_cell)
                    print("-" * DASH_LENGTH)
                    fp.close()
                    exit(1)
                else:
                    prev_cell = move_cell
                if map_.get(move_cell) == Entity.SHIELD:
                    map_.remove_perception(Entity.HULK)
                    map_.remove_perception(Entity.THOR)

                surroundings = map_.get_surroundings(variant_number, move_cell)
                proc.stdin.write(f"{len(surroundings)}\n".encode("ASCII"))
                for cell, entity in surroundings:
                    proc.stdin.write(f"{cell[0]} {cell[1]} {entity.value}\n".encode("ASCII"))
                proc.stdin.flush()
            elif output[0] == "e":
                print("[INFO] Output:")
                print(output)
                end_time = time.time()
                fp.write(f"{test},{output.split()[1]},{end_time - start_time}\n")
                break

        print("-" * (DASH_LENGTH + len(test)))

    fp.close()


if __name__ == "__main__":
    main()
