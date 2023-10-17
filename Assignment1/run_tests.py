import os
import glob
import time
from random import randint
from argparse import ArgumentParser
from map import Map, Entity

try:
    import pexpect
except ModuleNotFoundError:
    print("[ERROR] Install pexpect: pip install pexpect")
    exit(1)

TIMEOUT = 2


def main():
    parser = ArgumentParser()
    parser.add_argument("-t", "--tests", type=str, help="Path to the tests folder", required=True)
    parser.add_argument("-f", "--file", type=str, help="Path to the program to run", required=True)
    parser.add_argument("-o", "--output", type=str, help="Path to the output csv file", default="output.csv")
    parser.add_argument(
        "-c",
        "--cmd",
        type=str,
        help="Command to execute program (e.g. python interpreter: python3 or /usr/bin/python3.8)",
        default="/usr/bin/python3.8",
    )
    args = parser.parse_args()

    fp = open(args.output, "w")
    fp.write("TEST,ANSWER,TIME\n")

    tests = glob.glob(os.path.join(args.tests, "*.txt"))
    for test in tests:
        print("-" * 20 + test + "-" * 20)

        map_ = Map()
        map_.load(test)
        print(map_)

        prev_cell = (0, 0)
        shielded = False
        variant_number = randint(1, 2)

        start_time = time.time()

        proc = pexpect.spawn(f"{args.cmd} {args.file}", timeout=TIMEOUT)
        proc.sendline(f"{variant_number}")
        proc.sendline(f"{map_.get_location(Entity.INFINITY_STONE)[0]} {map_.get_location(Entity.INFINITY_STONE)[1]}")

        while True:
            ind = proc.expect([pexpect.EOF, pexpect.TIMEOUT, "\nm \\d \\d", "\ne \\d"])
            if ind == 0:
                print(f"[ERROR] EOF while running {args.i}:")
                print("-" * 50)
                print(proc.before.decode("utf-8"))
                print("-" * 50)
                fp.close()
                exit(1)
            elif ind == 1:
                print(f"[ERROR] Did not receive any output while running {args.i} in {TIMEOUT} seconds:")
                print("-" * 50)
                print(proc.before.decode("utf-8"))
                print("-" * 50)
                fp.close()
                exit(1)
            elif ind == 2:
                output = proc.after.decode("utf-8")
                _, x, y = output.split()
                move_cell = (int(x), int(y))
                if abs(move_cell[0] - prev_cell[0]) + abs(move_cell[1] - prev_cell[1]) > 1:
                    print(f"[ERROR] Can't teleport:")
                    print("-" * 50)
                    print("Previous output:")
                    print(proc.before.decode("utf-8").strip())
                    print("Tried to move to cell:")
                    print(move_cell)
                    print("From cell:")
                    print(prev_cell)
                    print("-" * 50)
                    fp.close()
                    exit(1)
                elif map_.get(move_cell) in (Entity.CAPTAIN_MARVEL, Entity.HULK, Entity.THOR):
                    print(f"[ERROR] Can't move to a cell with Avengers:")
                    print("-" * 50)
                    print("Previous output:")
                    print(proc.before.decode("utf-8").strip())
                    print("Tried to move to cell:")
                    print(move_cell)
                    print("From cell:")
                    print(prev_cell)
                    print("-" * 50)
                    fp.close()
                    exit(1)
                elif map_.get(move_cell) == Entity.PERCEPTION and not shielded:
                    print(f"[ERROR] Can't move to a cell with perception without a shield:")
                    print("-" * 50)
                    print("Previous output:")
                    print(proc.before.decode("utf-8").strip())
                    print("Tried to move to cell:")
                    print(move_cell)
                    print("From cell:")
                    print(prev_cell)
                    print("-" * 50)
                    fp.close()
                    exit(1)
                else:
                    prev_cell = move_cell
                if map_.get(move_cell) == Entity.SHIELD:
                    shielded = True

                surroundings = map_.get_surroundings(variant_number, move_cell)
                proc.sendline(f"{len(surroundings)}")
                for cell, entity in surroundings:
                    proc.sendline(f"{cell[0]} {cell[1]} {entity.value}")
            elif ind == 3:
                output = proc.after.decode("utf-8")
                print(output)
                break

        end_time = time.time()

        fp.write(f"{test},{0},{end_time - start_time}\n")
        print("-" * (40 + len(test)))

    fp.close()


if __name__ == "__main__":
    main()
