import os
import glob
import time

try:
    import pexpect
except ModuleNotFoundError:
    print("[ERROR] Install pexpect: pip install pexpect")
    exit(1)
from typing import Set
from random import randint
from argparse import ArgumentParser
from map import Map
from map import Entity
from generator import create_map


TIMEOUT = 2


def main():
    parser = ArgumentParser()
    parser.add_argument("-t", type=str, help="Path to the tests folder", required=True)
    parser.add_argument("-i", type=str, help="Path to the input python script", required=True)
    parser.add_argument("-o", type=str, help="Path to the output csv file", default="output.csv")
    parser.add_argument("-p", type=str, help="Python interpreter", default="/usr/bin/python3.8")
    args = parser.parse_args()

    fp = open(args.o, "w")
    fp.write("TEST,ANSWER,TIME\n")

    tests = glob.glob(os.path.join(args.t, "*.txt"))
    for test in tests:
        print("-" * 20 + test + "-" * 20)

        map_ = Map()
        map_.load(test)
        print(map_)

        prev_cell = (0, 0)
        shielded = False
        variant_number = randint(1, 2)

        start_time = time.time()

        proc = pexpect.spawn(f"{args.p} {args.i}", timeout=TIMEOUT)
        proc.sendline(f"{variant_number}")
        proc.sendline(f"{map_.get_location(Entity.INFINITY_STONE)[0]} {map_.get_location(Entity.INFINITY_STONE)[1]}")

        while True:
            ind = proc.expect([pexpect.EOF, pexpect.TIMEOUT, "\nm \\d \\d", "\ne \\d"])
            if ind == 0:
                print(f"[ERROR] EOF while running {args.i}:")
                print("-" * 50)
                print(proc.before.decode("utf-8"))
                print("-" * 50)
                break
            elif ind == 1:
                print(f"[ERROR] Did not receive any output while running {args.i} in {TIMEOUT} seconds:")
                print("-" * 50)
                print(proc.before.decode("utf-8"))
                print("-" * 50)
                break
            elif ind == 2:
                output = proc.after.decode("utf-8")
                _, x, y = output.split()
                move_cell = (int(x), int(y))
                if abs(move_cell[0] - prev_cell[0]) + abs(move_cell[1] - prev_cell[1]) != 1:
                    print(f"[ERROR] Can't teleport:")
                    print("-" * 50)
                    print("Previous output:")
                    print(proc.before.decode("utf-8").strip())
                    print("Tried to move to cell:")
                    print(move_cell)
                    print("From cell:")
                    print(prev_cell)
                    print("-" * 50)
                    break
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
                    break
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
                    break
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
