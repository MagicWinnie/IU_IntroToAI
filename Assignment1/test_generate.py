import time
import subprocess
from typing import Set
from random import randint
from argparse import ArgumentParser
from map import Map
from generator import create_map


def main():
    parser = ArgumentParser()
    parser.add_argument("-n", type=int, help="Number of tests to run on", required=True)
    parser.add_argument("-i", type=str, help="Path to the input python script", required=True)
    parser.add_argument("-o", type=str, help="Path to the output csv file", default="output.csv")
    parser.add_argument("-p", type=str, help="Python interpreter", default="/usr/bin/python3.8")
    args = parser.parse_args()

    fp = open(args.o, "w")
    fp.write("TEST,ANSWER,TIME\n")

    created_maps: Set[str] = set()
    for i in range(args.n):
        while True:
            map_: Map = create_map()
            if str(map_) not in created_maps:
                created_maps.add(str(map_))
                break

        variant_number = randint(1, 2)
        start_time = time.time()
        proc = subprocess.Popen(
            [args.p, args.i], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        end_time = time.time()
        fp.write(f"{i + 1},{0},{end_time - start_time}\n")

    fp.close()


if __name__ == "__main__":
    main()
