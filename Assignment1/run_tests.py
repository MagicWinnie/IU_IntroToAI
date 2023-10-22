import os
import glob
import time
from random import randint
from argparse import ArgumentParser, Namespace
from map import Map, Entity

try:
    import pexpect
except ModuleNotFoundError:
    print("[ERROR] Install pexpect: pip install pexpect")
    exit(1)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "-t",
        "--tests",
        type=str,
        help="Path to the tests folder",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Path to the program to run",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output csv file",
        default="output.csv",
    )
    parser.add_argument(
        "-c",
        "--cmd",
        type=str,
        help="Command to execute program (e.g. python interpreter: python3 or /usr/bin/python3.8)",
        default="/usr/bin/python3.8",
    )
    return parser.parse_args()


TIMEOUT = 2  # seconds
DASH_LENGTH = 50


def main():
    args = parse_args()

    fp = open(args.output, "w")
    fp.write("TEST,ANSWER,TIME\n")

    tests = glob.glob(os.path.join(args.tests, "*.txt"))
    for test in tests:
        print("-" * (DASH_LENGTH // 2) + test + "-" * (DASH_LENGTH // 2))

        map_ = Map()
        map_.load(test)
        print(map_)

        prev_cell = (0, 0)
        variant_number = randint(1, 2)
        infinity_stone = map_.get_location(Entity.INFINITY_STONE)

        print("Variant number:", variant_number)

        proc = pexpect.spawn(f"{args.cmd} {args.file}", timeout=TIMEOUT)
        proc.delaybeforesend = 0.01

        start_time = time.time()

        proc.sendline(f"{variant_number}")
        proc.sendline(f"{infinity_stone[0]} {infinity_stone[1]}")

        while True:
            ind = proc.expect([pexpect.EOF, pexpect.TIMEOUT, "\nm \\d \\d\r\n", "\ne \\d\r\n"])
            if ind == 0:
                print(f"[ERROR] EOF while running {args.file}:")
                print("-" * DASH_LENGTH)
                print(proc.before.decode("utf-8").strip())
                print("-" * DASH_LENGTH)
                fp.close()
                exit(1)
            elif ind == 1:
                print(f"[ERROR] Did not receive any output while running {args.file} in {TIMEOUT} seconds:")
                print("-" * DASH_LENGTH)
                print(proc.before.decode("utf-8").strip())
                print("-" * DASH_LENGTH)
                fp.close()
                exit(1)
            elif ind == 2:
                output = proc.after.decode("utf-8")
                _, x, y = output.split()
                move_cell = (int(x), int(y))
                if abs(move_cell[0] - prev_cell[0]) + abs(move_cell[1] - prev_cell[1]) > 1:
                    print(f"[ERROR] Can't teleport:")
                    print("-" * DASH_LENGTH)
                    print("Previous output:")
                    print(proc.before.decode("utf-8").strip())
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
                    print("Previous output:")
                    print(proc.before.decode("utf-8").strip())
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
                    print("Previous output:")
                    print(proc.before.decode("utf-8").strip())
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
                proc.sendline(f"{len(surroundings)}")
                for cell, entity in surroundings:
                    proc.sendline(f"{cell[0]} {cell[1]} {entity.value}")
            elif ind == 3:
                output = proc.after.decode("utf-8").strip()
                print("[INFO] Output:")
                print(output)
                end_time = time.time()
                fp.write(f"{test},{output.split()[1]},{end_time - start_time}\n")
                break

        print("-" * (DASH_LENGTH + len(test)))

    fp.close()


if __name__ == "__main__":
    main()
