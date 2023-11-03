import os
import glob
import collections
from argparse import ArgumentParser


N = 9  # size of the map (NxN)


def bfs(grid, start, goal):
    queue = collections.deque([[start]])
    seen = set([start])
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        if (x, y) == goal:
            return len(path) - 1
        for x2, y2 in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= x2 < N and 0 <= y2 < N and grid[x2][y2] in ".SI" and (x2, y2) not in seen:
                queue.append(path + [(x2, y2)])
                seen.add((x2, y2))
    return -1


def m_dist(this, other) -> int:
    return abs(this[0] - other[0]) + abs(this[1] - other[1])


def vonneumann_perception_zone(point, center, r) -> bool:
    return m_dist(point, center) <= r


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-t",
        "--tests",
        type=str,
        help="Path to the directory where test files are located",
        required=True,
    )
    args = parser.parse_args()

    os.makedirs(os.path.join(args.tests, "answers"), exist_ok=True)

    tests = glob.glob(os.path.join(args.tests, "*.txt"))
    for test in tests:
        map_ = []
        with open(test, "r") as ip:
            for row in ip:
                map_.append(row.strip().split())

        stone = None
        shield = None
        for i in range(N):
            for j in range(N):
                if map_[i][j] == "I":
                    stone = (i, j)
                if map_[i][j] == "S":
                    shield = (i, j)

        if not stone or not shield or len(map_) != N or len(map_[0]) != N:
            print(f"[ERROR] Incorrect map: {test}")
            exit(0)

        min_dist_wo_s = bfs(map_, (0, 0), stone)
        min_dist = -1
        if min_dist_wo_s > 0:
            min_dist = min_dist_wo_s

        min_dist_t_s = bfs(map_, (0, 0), shield)
        if min_dist_t_s > 0:
            marvel = (-1, -1)
            for i in range(N):
                for j in range(N):
                    if map_[i][j] == "P":
                        map_[i][j] = "."
                    if map_[i][j] == "M":
                        marvel = (i, j)
            for i in range(N):
                for j in range(N):
                    if map_[i][j] != ".":
                        continue
                    if vonneumann_perception_zone((i, j), marvel, 2):
                        map_[i][j] = "P"
            min_dist_t_g = bfs(map_, shield, stone)

            if min_dist_t_s > 0 and min_dist_t_g > 0:
                if min_dist < 0 or min_dist_t_s + min_dist_t_g < min_dist:
                    min_dist = min_dist_t_s + min_dist_t_g

        with open(os.path.join(args.tests, "answers", test.replace("\\", "/").split("/")[-1]), "w") as op:
            op.write(str(min_dist))


if __name__ == "__main__":
    main()
