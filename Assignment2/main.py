from __future__ import annotations
import time
import os
import random
from enum import Enum
from dataclasses import dataclass
from matplotlib import pyplot as plt


STATISTICS = True


class Direction(int, Enum):
    HORIZONTAL = 0
    VERTICAL = 1


@dataclass(unsafe_hash=True)
class Location:
    x: int
    y: int
    direction: Direction

    def __str__(self) -> str:
        return f"{self.x} {self.y} {self.direction.value}"


class Crossword:
    def __init__(self, words: list[str], locations: list[Location] | None = None, N: int = 20):
        self.words = words
        self.N = N
        self.grid_printable: list[list[str]] | None = None
        self.grid_numbers: list[list[int]] | None = None
        self.letters: dict[str, list[tuple[int, int]]] = {}
        self.fitness: float | None = None

        if locations is None:
            self.locations = []
            for word in words:
                direction = random.choice((Direction.HORIZONTAL, Direction.VERTICAL))
                self.locations.append(
                    Location(
                        random.randint(0, N - 1 - (len(word) if direction == Direction.VERTICAL else 0)),
                        random.randint(0, N - 1 - (len(word) if direction == Direction.HORIZONTAL else 0)),
                        direction,
                    )
                )
        else:
            assert len(words) == len(locations), "Length of `words` should be equal to length of `locations"
            self.locations = locations

    def get_grid_printable(self) -> list[list[str]]:
        self.grid_printable = [["." for _ in range(self.N)] for _ in range(self.N)]
        for word, location in zip(self.words, self.locations):
            for i, char in enumerate(word):
                if location.direction == Direction.HORIZONTAL:
                    if 0 <= location.x < self.N and 0 <= location.y + i < self.N:
                        self.grid_printable[location.x][location.y + i] = char
                elif location.direction == Direction.VERTICAL:
                    if 0 <= location.x + i < self.N and 0 <= location.y < self.N:
                        self.grid_printable[location.x + i][location.y] = char
        return self.grid_printable

    def get_grid_numbers(self) -> list[list[int]]:
        if self.grid_numbers is not None:
            return self.grid_numbers

        self.letters = {}
        self.grid_numbers = [[0 for _ in range(self.N)] for _ in range(self.N)]
        for word, location in zip(self.words, self.locations):
            for i, _ in enumerate(word):
                if word[i] not in self.letters:
                    self.letters[word[i]] = []
                if location.direction == Direction.HORIZONTAL:
                    self.letters[word[i]].append((location.x, location.y + i))
                    if 0 <= location.x < self.N and 0 <= location.y + i < self.N:
                        if self.grid_numbers[location.x][location.y + i] == 0:
                            self.grid_numbers[location.x][location.y + i] = 1
                        else:
                            self.grid_numbers[location.x][location.y + i] = 3
                elif location.direction == Direction.VERTICAL:
                    self.letters[word[i]].append((location.x + i, location.y))
                    if 0 <= location.x + i < self.N and 0 <= location.y < self.N:
                        if self.grid_numbers[location.x + i][location.y] == 0:
                            self.grid_numbers[location.x + i][location.y] = 2
                        else:
                            self.grid_numbers[location.x + i][location.y] = 3

        return self.grid_numbers

    def get_fitness(self) -> float:
        if self.fitness is not None:
            return self.fitness

        penalty = 0
        grid = self.get_grid_printable()
        grid_numbers = self.get_grid_numbers()

        # check if connected
        visited = [[False for _ in range(len(grid))] for _ in range(len(grid))]
        dfs(grid, (self.locations[0].x, self.locations[0].y), visited)

        penalty += len(self.locations) - len(set(self.locations))

        for _, (word, location) in enumerate(zip(self.words, self.locations)):
            if not visited[location.x][location.y]:
                min_dist = float("inf")
                for i in range(len(visited)):
                    for j in range(len(visited)):
                        if visited[i][j]:
                            dist = abs(i - location.x) + abs(j - location.y)
                            if dist < min_dist:
                                min_dist = dist
                penalty += min_dist
            if location.direction == Direction.HORIZONTAL:
                # words are out of grid
                if location.y + len(word) - 1 >= self.N:
                    penalty += 1  # location.y + len(word) - 1 - individual.N
                # words are surrounded by another word
                if location.y > 0 and grid[location.x][location.y - 1] != ".":
                    penalty += 1
                # words are surrounded by another word
                if location.y + len(word) < self.N and grid[location.x][location.y + len(word)] != ".":
                    penalty += 1
                if (
                    location.x > 0
                    and grid[location.x - 1][location.y] != "."
                    and grid_numbers[location.x - 1][location.y] == 1
                ):
                    penalty += 1
                if (
                    location.x < self.N - 1
                    and grid[location.x + 1][location.y] != "."
                    and grid_numbers[location.x + 1][location.y] == 1
                ):
                    penalty += 1
                if (
                    location.x > 0
                    and location.y + len(word) - 1 < self.N
                    and grid[location.x - 1][location.y + len(word) - 1] != "."
                    and grid_numbers[location.x - 1][location.y + len(word) - 1] == 1
                ):
                    penalty += 1
                if (
                    location.x < self.N - 1
                    and location.y + len(word) - 1 < self.N
                    and grid[location.x + 1][location.y + len(word) - 1] != "."
                    and grid_numbers[location.x + 1][location.y + len(word) - 1] == 1
                ):
                    penalty += 1
                count_surrounded = 0
                for i in range(len(word)):
                    if word[i] != grid[location.x][location.y + i]:
                        min_dist = float("inf")
                        for pt in self.letters[word[i]]:
                            if pt[0] == location.x and pt[1] >= location.y and pt[1] <= location.y + len(word) - 1:
                                continue
                            dist = abs(location.x - pt[0]) + abs(location.y + i - pt[1])
                            if dist < min_dist:
                                min_dist = dist
                        penalty += min_dist
                    if i < len(word) - 1:
                        if location.x > 0:
                            if (
                                grid[location.x - 1][location.y + i] != "."
                                and grid[location.x - 1][location.y + i + 1] != "."
                            ):
                                penalty += 1
                            if grid[location.x - 1][location.y + i] != ".":
                                count_surrounded += 1
                        if location.x < self.N - 1:
                            if (
                                grid[location.x + 1][location.y + i] != "."
                                and grid[location.x + 1][location.y + i + 1] != "."
                            ):
                                penalty += 1
                            if grid[location.x + 1][location.y + i] != ".":
                                count_surrounded += 1
                    else:
                        if location.x > 0 and grid[location.x - 1][location.y + i] != ".":
                            count_surrounded += 1
                        if location.x < self.N - 1 and grid[location.x + 1][location.y + i] != ".":
                            count_surrounded += 1
                if count_surrounded == 0:
                    penalty += 1
            elif location.direction == Direction.VERTICAL:
                # words are out of grid
                if location.x + len(word) - 1 >= self.N:
                    penalty += 1  # location.x + len(word) - 1 - individual.N
                # words are surrounded by another word
                if location.x > 0 and grid[location.x - 1][location.y] != ".":
                    penalty += 1
                # words are surrounded by another word
                if location.x + len(word) < self.N and grid[location.x + len(word)][location.y] != ".":
                    penalty += 1
                if (
                    location.y > 0
                    and grid[location.x][location.y - 1] != "."
                    and grid_numbers[location.x][location.y - 1] == 2
                ):
                    penalty += 1
                if (
                    location.y < self.N - 1
                    and grid[location.x][location.y + 1] != "."
                    and grid_numbers[location.x][location.y + 1] == 2
                ):
                    penalty += 1
                if (
                    location.y > 0
                    and location.x + len(word) - 1 < self.N
                    and grid[location.x + len(word) - 1][location.y - 1] != "."
                    and grid_numbers[location.x + len(word) - 1][location.y - 1] == 1
                ):
                    penalty += 1
                if (
                    location.y < self.N - 1
                    and location.x + len(word) - 1 < self.N
                    and grid[location.x + len(word) - 1][location.y + 1] != "."
                    and grid_numbers[location.x + len(word) - 1][location.y + 1] == 1
                ):
                    penalty += 1
                count_surrounded = 0
                for i in range(len(word)):
                    if word[i] != grid[location.x + i][location.y]:
                        min_dist = float("inf")
                        for pt in self.letters[word[i]]:
                            if pt[1] == location.y and pt[0] >= location.x and pt[0] <= location.x + len(word) - 1:
                                continue
                            dist = abs(location.x + i - pt[0]) + abs(location.y - pt[1])
                            if dist < min_dist:
                                min_dist = dist
                        penalty += min_dist
                    if i < len(word) - 1:
                        if location.y > 0:
                            if (
                                grid[location.x + i][location.y - 1] != "."
                                and grid[location.x + i + 1][location.y - 1] != "."
                            ):
                                penalty += 1
                            if grid[location.x + i][location.y - 1] != ".":
                                count_surrounded += 1
                        if location.y < self.N - 1:
                            if (
                                grid[location.x + i][location.y + 1] != "."
                                and grid[location.x + i + 1][location.y + 1] != "."
                            ):
                                penalty += 1
                            if grid[location.x + i][location.y + 1] != ".":
                                count_surrounded += 1
                    else:
                        if location.y > 0 and grid[location.x + i][location.y - 1] != ".":
                            count_surrounded += 1
                        if location.y < self.N - 1 and grid[location.x + i][location.y - 1] != ".":
                            count_surrounded += 1
                if count_surrounded == 0:
                    penalty += 1

        return -penalty

    def __str__(self) -> str:
        grid = self.get_grid_printable()
        string = ""
        for row in grid:
            string += " ".join(row) + "\n"
        return string[:-1]


def dfs(grid: list[list[str]], start: tuple[int, int], visited: list[list[bool]]) -> None:
    def neighbours(point):
        candidates = [
            (point[0] - 1, point[1]),
            (point[0] + 1, point[1]),
            (point[0], point[1] - 1),
            (point[0], point[1] + 1),
        ]
        return [
            c
            for c in candidates
            if c[0] >= 0 and c[0] < len(grid) and c[1] >= 0 and c[1] < len(grid) and grid[c[0]][c[1]] != "."
        ]

    frontier = [start]

    while not len(frontier) == 0:
        element = frontier.pop()
        visited[element[0]][element[1]] = True
        frontier.extend([n for n in neighbours(element) if visited[n[0]][n[1]] is False])


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
    locations = []
    for i in range(len(mother.locations)):
        locations.append(random.choice((mother.locations[i], father.locations[i])))
    return Crossword(mother.words, locations)


def mutate(offspring: Crossword) -> Crossword:
    indices = random.sample(range(len(offspring.locations)), len(offspring.locations) // 3)
    for i in indices:
        direction = random.choice((Direction.HORIZONTAL, Direction.VERTICAL))
        offspring.locations[i] = Location(
            random.randint(0, offspring.N - 1 - (len(offspring.words[i]) if direction == Direction.VERTICAL else 0)),
            random.randint(0, offspring.N - 1 - (len(offspring.words[i]) if direction == Direction.HORIZONTAL else 0)),
            direction,
        )
    offspring.grid_printable = None
    offspring.grid_numbers = None
    return offspring


def evolution_step(population: list[Crossword], offsprings_size: int) -> list[Crossword]:
    mothers, fathers = get_parents(population, offsprings_size)
    offsprings = []

    for mother, father in zip(mothers, fathers):
        offsprings.append(mutate(cross(mother, father)))

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

    while True:
        population = evolution_step(population, offsprings_size)
        best_individual = population[-1]
        best_fitness = best_individual.get_fitness()
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


def main(inputs_dir: str = "inputs", outputs_dir: str = "outputs") -> None:
    files = get_inputs(inputs_dir)
    prepare_outputs(outputs_dir)

    stat = None
    if STATISTICS:
        stat = open("statistics.csv", "w")
        stat.write("test,time,generation,fitness\n")
    for file in files:
        words = read_words(os.path.join(inputs_dir, file))

        start_time = time.time()
        try:
            crossword, generation, best_fitness = solution(words)
        except KeyboardInterrupt:
            break
        except Exception:
            continue
        end_time = time.time()

        with open(os.path.join(outputs_dir, file.replace("input", "output")), "w") as fp:
            for location in crossword.locations:
                fp.write(str(location) + "\n")

        if STATISTICS and stat:
            stat.write(f"{file},{end_time-start_time},{generation},{best_fitness}\n")
    if STATISTICS and stat:
        stat.close()


if __name__ == "__main__":
    main()
