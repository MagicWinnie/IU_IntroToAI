import os
from typing import Set
from argparse import ArgumentParser
from map import Map
from generator import create_map


def main():
    parser = ArgumentParser()
    parser.add_argument("-n", "--num", type=int, help="Number of tests to generate", required=True)
    parser.add_argument("-o", "--output", type=str, help="Path to the directory to write test files", required=True)
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    created_maps: Set[str] = set()
    for i in range(args.num):
        while True:
            map_: Map = create_map()
            if str(map_) not in created_maps:
                created_maps.add(str(map_))
                break

        with open(os.path.join(args.o, f"test_{i}.txt"), "w") as fp:
            fp.write(str(map_))


if __name__ == "__main__":
    main()
