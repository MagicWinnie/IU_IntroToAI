from typing import Tuple


def in_moore(point: Tuple[int, int], center: Tuple[int, int], r: int = 1) -> bool:
    return abs(point[0] - center[0]) <= r and abs(point[1] - center[1]) <= r


def in_von_neumann(point: Tuple[int, int], center: Tuple[int, int], r: int) -> bool:
    return abs(point[0] - center[0]) + abs(point[1] - center[1]) <= r
