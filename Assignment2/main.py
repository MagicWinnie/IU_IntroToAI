from __future__ import annotations
import time
import os
import random
from enum import Enum
from copy import deepcopy
from dataclasses import dataclass
from matplotlib import pyplot as plt


WRITE_STATISTICS = True


class Direction(int, Enum):
    HORIZONTAL = 0
    VERTICAL = 1


@dataclass(unsafe_hash=True, order=True)
class Point:
    x: int
    y: int

    def __str__(self) -> str:
        return f"{self.x} {self.y}"


@dataclass(unsafe_hash=True)
class Word:
    word: str
    point: Point
    direction: Direction
    component: int

    def get_ith_point(self, index: int) -> Point:
        if index < 0:
            index = len(self.word) + index
        if self.direction == Direction.HORIZONTAL:
            return Point(self.point.x, self.point.y + index)
        else:
            return Point(self.point.x + index, self.point.y)

    def intersects(self, other: Word) -> tuple[int, int] | None:
        if self.direction == other.direction:
            return None
        if self.direction == Direction.HORIZONTAL:
            if (
                other.point.x <= self.point.x <= other.point.x + len(other.word) - 1
                and self.point.y <= other.point.y <= self.point.y + len(self.word) - 1
            ):
                return other.point.y - self.point.y, self.point.x - other.point.x
        else:
            if (
                self.point.x <= other.point.x <= self.point.x + len(self.word) - 1
                and other.point.y <= self.point.y <= other.point.y + len(other.word) - 1
            ):
                return other.point.x - self.point.x, self.point.y - other.point.y
        return None

    def parallel_close(self, other: Word) -> int:
        if self.direction != other.direction:
            return 0
        if self.direction == Direction.HORIZONTAL:
            if abs(self.point.x - other.point.x) > 1:
                return 0
            if (
                self.point.y <= other.point.y <= self.point.y + len(self.word) - 1
                or other.point.y <= self.point.y <= other.point.y + len(other.word) - 1
            ):
                return min(self.point.y + len(self.word) - 1, other.point.y + len(other.word) - 1) - max(
                    self.point.y, other.point.y
                )  # + 1
        else:
            if abs(self.point.y - other.point.y) > 1:
                return 0
            if (
                self.point.x <= other.point.x <= self.point.x + len(self.word) - 1
                or other.point.x <= self.point.x <= other.point.x + len(other.word) - 1
            ):
                return min(self.point.x + len(self.word) - 1, other.point.x + len(other.word) - 1) - max(
                    self.point.x, other.point.x
                )  # + 1
        return 0

    def intersect_close(self, other: Word) -> bool:
        if self.direction == other.direction:
            return False
        if self.direction == Direction.HORIZONTAL:
            if other.point.x <= self.point.x <= other.point.x + len(other.word) - 1 and (
                self.point.y - 1 == other.point.y or other.point.y == self.point.y + len(self.word)
            ):
                return True
            if (other.point.x - 1 == self.point.x or other.point.x + len(other.word) == self.point.x) and (
                self.point.y <= other.point.y <= self.point.y + len(self.word) - 1
                or other.point.y <= self.point.y <= other.point.y + len(other.word) - 1
            ):
                return True
        else:
            if self.point.x <= other.point.x <= self.point.x + len(self.word) - 1 and (
                other.point.y - 1 == self.point.y or self.point.y == other.point.y + len(other.word)
            ):
                return True
            if (self.point.x - 1 == other.point.x or self.point.x + len(self.word) == other.point.x) and (
                other.point.y <= self.point.y <= other.point.y + len(other.word) - 1
                or self.point.y <= other.point.y <= self.point.y + len(self.word) - 1
            ):
                return True
        return False

    def __str__(self) -> str:
        return f"{self.point} {self.direction.value}"


class Crossword:
    def __init__(self, words: list[str], N: int = 20):
        self.N = N
        self.grid_printable: list[list[str]] | None = None
        self.fitness: float | None = None
        self.components: set[int] = set()

        self.words: list[Word] = []
        for i, word in enumerate(words):
            direction = Direction.HORIZONTAL if random.random() < 0.5 else Direction.VERTICAL
            dx = len(word) if direction == Direction.VERTICAL else 0
            dy = len(word) if direction == Direction.HORIZONTAL else 0
            x0, y0 = random.randint(0, N - 1 - dx), random.randint(0, N - 1 - dy)
            self.words.append(Word(word, Point(x0, y0), direction, -1))
            self.components.add(i)

    def get_grid_printable(self) -> list[list[str]]:
        if self.grid_printable is None:
            self.grid_printable = [["." for _ in range(self.N)] for _ in range(self.N)]
            for word in self.words:
                for i in range(len(word.word)):
                    point = word.get_ith_point(i)
                    self.grid_printable[point.x][point.y] = word.word[i]
        return self.grid_printable

    def get_fitness(self) -> float:
        if self.fitness is not None:
            return self.fitness

        penalty = 0
        intersections = [False for _ in range(len(self.words))]
        for i in range(len(self.words)):
            word1 = self.words[i]
            for j in range(i + 1, len(self.words)):
                word2 = self.words[j]

                intersection = word1.intersects(word2)
                if intersection:
                    intersections[i] = True
                    intersections[j] = True
                    intersection1, intersection2 = intersection
                    if word1.word[intersection1] != word2.word[intersection2]:
                        penalty += 2

                    # if word1.component == word2.component:
                    #     if word1.component == -1:
                    #         pass
                    # elif word1.component == -1:
                    #     word1.component = word2.component
                    # elif word2.component == -1:
                    #     word2.component = word1.component

                penalty += word1.parallel_close(word2)

                intersection_close = word1.intersect_close(word2)
                if intersection_close:
                    penalty += 1
        for intersection in intersections:
            if not intersection:
                penalty += 1
        return -penalty

    def __str__(self) -> str:
        grid = self.get_grid_printable()
        string = ""
        for row in grid:
            string += " ".join(row) + "\n"
        return string[:-1]


def initial_population(words: list[str], population_size: int) -> list[Crossword]:
    population = [Crossword(words) for _ in range(population_size)]
    population.sort(key=lambda x: x.get_fitness())
    return population


def replace_population(population: list[Crossword], new_individuals: list[Crossword]) -> list[Crossword]:
    size = len(population)
    population.extend(new_individuals)
    population.sort(key=lambda x: x.get_fitness())
    return population[-size:]


def get_parents(population: list[Crossword], offsprings_size: int) -> tuple[list[Crossword], list[Crossword]]:
    mothers = population[-2 * offsprings_size :: 2]
    fathers = population[-2 * offsprings_size + 1 :: 2]
    return mothers, fathers


def cross(mother: Crossword, father: Crossword) -> Crossword:
    crossword = deepcopy(mother)
    # ind = random.randint(0, len(mother.locations) - 1)
    # for i in range(ind):
    #     locations.append(mother.locations[i])
    # for i in range(ind, len(mother.locations)):
    #     locations.append(father.locations[i])

    for i in range(len(mother.words)):
        if random.random() < 0.5:
            crossword.words[i].point = mother.words[i].point
            crossword.words[i].direction = mother.words[i].direction
            crossword.words[i].component = mother.words[i].component
        else:
            crossword.words[i].point = father.words[i].point
            crossword.words[i].direction = father.words[i].direction
            crossword.words[i].component = father.words[i].component
    return crossword


def mutate(offspring: Crossword, probability) -> Crossword:
    for i in range(len(offspring.words)):
        if random.random() < probability:
            direction = Direction.HORIZONTAL if random.random() < 0.5 else Direction.VERTICAL
            dx = len(offspring.words[i].word) if direction == Direction.VERTICAL else 0
            dy = len(offspring.words[i].word) if direction == Direction.HORIZONTAL else 0
            x0, y0 = random.randint(0, offspring.N - 1 - dx), random.randint(0, offspring.N - 1 - dy)

            offspring.words[i].point = Point(x0, y0)
            offspring.words[i].direction = direction
            offspring.words[i].component = -1
    offspring.grid_printable = None
    offspring.fitness = None
    return offspring


def evolution_step(population: list[Crossword], offsprings_size: int, mutation_rate: float = 0.4) -> list[Crossword]:
    mothers, fathers = get_parents(population, offsprings_size)
    offsprings = []

    for mother, father in zip(mothers, fathers):
        offsprings.append(mutate(cross(mother, father), mutation_rate))

    new_population = replace_population(population, offsprings)
    return new_population


def solution(words: list[str], population_size: int = 100, offsprings_size: int = 30) -> tuple[Crossword, int, float]:
    population = []
    best_fitness = -float("inf")
    for _ in range(5):
        population_ = initial_population(words, population_size)
        best_fitness_ = population_[-1].get_fitness()
        if best_fitness_ > best_fitness:
            population = population_
            best_fitness = best_fitness_

    best_individual = population[-1]
    fitness_change: list[float] = []
    generation = 0

    # same_fitness = 0
    # same_threshold = 800
    # last_fitness = float("inf")
    while True:
        population = evolution_step(population, offsprings_size)
        best_individual = population[-1]
        best_fitness = best_individual.get_fitness()
        # if last_fitness != float("inf"):
        #     if best_fitness == last_fitness:
        #         same_fitness += 1
        #     else:
        #         same_fitness = 0
        # if same_fitness >= same_threshold:
        #     population = initial_population(words, population_size)
        #     same_fitness = 0
        # last_fitness = best_fitness

        fitness_change.append(best_fitness)

        if generation % 100 == 0:
            print("-" * 20)
            print(f"Generation #{generation}")
            print(f"Fitness: {best_fitness}")
            print(best_individual)
            print()

        if best_fitness == 0:
            break
        generation += 1

    print("-" * 20)
    print(f"Generation #{generation}")
    print(f"Fitness: {best_fitness}")
    print(best_individual)
    print()
    plt.plot(fitness_change)
    plt.title("Change of a fitness score")
    plt.xlabel("Generation")
    plt.ylabel("Fitness score")
    plt.show()

    return best_individual, generation, best_fitness


def get_number_input(path: str, prefix: str = "input") -> str:
    file_name = os.path.basename(path)
    file_name = os.path.splitext(file_name)[0]
    file_name = file_name.replace(prefix, "")
    return file_name


def get_inputs(directory: str = "inputs") -> list[str]:
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist!")

    files = os.listdir(directory)

    # sort by number of lines
    lines = []
    for file in files:
        with open(os.path.join(directory, file), "r") as fp:
            lines.append(sum(1 for _ in fp))

    return [file for _, file in sorted(zip(lines, files))]


def prepare_outputs(directory: str = "outputs") -> None:
    if not os.path.isdir(directory):
        os.mkdir(directory)


def read_words(path: str) -> list[str]:
    with open(path, "r") as fp:
        words = fp.readlines()
    words = list(map(str.strip, words))
    return words


def main(inputs_dir: str = "__inputs", outputs_dir: str = "outputs") -> None:
    files = get_inputs(inputs_dir)
    prepare_outputs(outputs_dir)

    stat = None
    if WRITE_STATISTICS:
        stat = open("statistics.csv", "w")
        stat.write("test,time,generation,fitness,words\n")
    for file in files:
        words = read_words(os.path.join(inputs_dir, file))

        start_time = time.time()
        try:
            crossword, generation, best_fitness = solution(words)
        except KeyboardInterrupt:
            break
        end_time = time.time()

        with open(os.path.join(outputs_dir, file.replace("input", "output")), "w") as fp:
            for word in crossword.words:
                fp.write(str(word) + "\n")

        if WRITE_STATISTICS and stat:
            stat.write(f"{file},{end_time-start_time},{generation},{best_fitness},{len(words)}\n")
    if WRITE_STATISTICS and stat:
        stat.close()


if __name__ == "__main__":
    main()
