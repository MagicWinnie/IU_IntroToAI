import csv
import argparse
from math import sqrt


def eval_mean(sequence) -> float:
    return sum(sequence) / len(sequence)


def eval_median(sequence) -> float:
    if len(sequence) % 2 == 1:
        return sequence[len(sequence) // 2]
    else:
        return (sequence[len(sequence) // 2 - 1] + sequence[len(sequence) // 2]) / 2


def eval_standard_deviation(sequence) -> float:
    dev = 0
    seq_mean = eval_mean(sequence)
    for seq in sequence:
        dev += (seq - seq_mean) * (seq - seq_mean)
    dev /= len(sequence) - 1
    return sqrt(dev)


def eval_mode(sequence) -> float:
    count = dict()
    for seq in sequence:
        if prettify(seq) in count:
            count[prettify(seq)] += 1
        else:
            count[prettify(seq)] = 1
    max_count, max_count_item = 0, 0
    for key in count:
        value = count[key]
        if value > max_count:
            max_count = value
            max_count_item = key
    return max_count_item


def prettify(num: float) -> float:
    return round(num, precision)


parser = argparse.ArgumentParser()
parser.add_argument("--csv", type=str, help="path to .csv file with tests' results", required=True)
parser.add_argument("--precision", type=int, default=3, help="precision for output time", required=False)

args = parser.parse_args()
csv_file_path = args.csv
precision = args.precision

with open(csv_file_path, "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader, None)

    test_count = 0
    win_count, lose_count = 0, 0
    execution_times = list()

    for row in csv_reader:
        execution_times.append(float(row[2]))
        test_count += 1
        if int(row[1]) >= 0:
            win_count += 1
        else:
            lose_count += 1

    mean = eval_mean(execution_times)
    median = eval_median(execution_times)
    deviation = eval_standard_deviation(execution_times)
    mode = eval_mode(execution_times)

    print(f'Analysis of file "{csv_file.name}"')
    print(f"Tests count = {test_count}, count of wins = {win_count}, count of losses = {lose_count}")
    print(
        f"Percentage of wins = {prettify((win_count / test_count) * 100)}%, "
        f"percentage of losses = {prettify((lose_count / test_count) * 100)}%"
    )
    print(
        f"Time: mean = {prettify(mean)}s, mode = {prettify(mode)}s, median = {prettify(median)}s, "
        f"sample standard deviation = {prettify(deviation)}s"
    )
