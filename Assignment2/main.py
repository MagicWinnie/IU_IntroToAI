from __future__ import annotations
import os
import random
from enum import Enum
from copy import deepcopy
from typing import Callable
from dataclasses import dataclass
from matplotlib import pyplot as plt


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

        if locations is None:
            self.locations = [
                Location(
                    random.randint(0, N - 1),
                    random.randint(0, N - 1),
                    random.choice((Direction.HORIZONTAL, Direction.VERTICAL)),
                )
                for _ in range(len(words))
            ]
        else:
            assert len(words) == len(locations), "Length of `words` should be equal to length of `locations"
            self.locations = locations

    def get_grid(self) -> list[list[str]]:
        grid = [["." for _ in range(self.N)] for _ in range(self.N)]
        for word, location in zip(self.words, self.locations):
            for i, char in enumerate(word):
                if location.direction == Direction.HORIZONTAL:
                    if 0 <= location.x < self.N and 0 <= location.y + i < self.N:
                        grid[location.x][location.y + i] = char
                elif location.direction == Direction.VERTICAL:
                    if 0 <= location.x + i < self.N and 0 <= location.y < self.N:
                        grid[location.x + i][location.y] = char
        return grid

    def __str__(self) -> str:
        grid = self.get_grid()
        string = ""
        for row in grid:
            string += " ".join(row) + "\n"
        return string[:-1]


def dfs(grid: list[list[str]], start: tuple[int, int], visited: list[list[bool]]):
    visited[start[0]][start[1]] = True
    if start[0] > 0 and grid[start[0] - 1][start[1]] != "." and not visited[start[0] - 1][start[1]]:
        dfs(grid, (start[0] - 1, start[1]), visited)
    if start[0] < len(grid) - 1 and grid[start[0] + 1][start[1]] != "." and not visited[start[0] + 1][start[1]]:
        dfs(grid, (start[0] + 1, start[1]), visited)
    if start[1] > 0 and grid[start[0]][start[1] - 1] != "." and not visited[start[0]][start[1] - 1]:
        dfs(grid, (start[0], start[1] - 1), visited)
    if start[1] < len(grid) - 1 and grid[start[0]][start[1] + 1] != "." and not visited[start[0]][start[1] + 1]:
        dfs(grid, (start[0], start[1] + 1), visited)


def fitness(individual: Crossword) -> float:
    penalty = 0
    grid = individual.get_grid()

    # check if connected
    visited = [[False for _ in range(len(grid))] for _ in range(len(grid))]
    dfs(grid, (individual.locations[0].x, individual.locations[0].y), visited)

    for i in range(len(individual.words)):
        word, location = individual.words[i], individual.locations[i]

        if not visited[location.x][location.y]:
            penalty += 1
        if location.direction == Direction.HORIZONTAL:
            # words are out of grid
            if location.y + len(word) - 1 >= individual.N:
                penalty += 1
            # words are not surrounded by another word
            if location.y > 0 and grid[location.x][location.y - 1] != ".":
                penalty += 1
            # words are not surrounded by another word
            if location.y + len(word) < individual.N and grid[location.x][location.y + len(word)] != ".":
                penalty += 1
        elif location.direction == Direction.VERTICAL:
            # words are out of grid
            if location.x + len(word) - 1 >= individual.N:
                penalty += 1
            # words are not surrounded by another word
            if location.x > 0 and grid[location.x - 1][location.y] != ".":
                penalty += 1
            # words are not surrounded by another word
            if location.x + len(word) < individual.N and grid[location.x + len(word)][location.y] != ".":
                penalty += 1

        for j in range(i + 1, len(individual.words)):
            word_, location_ = individual.words[j], individual.locations[j]
            if location.direction == Direction.HORIZONTAL and location_.direction == Direction.HORIZONTAL:
                # check if two are located next to each other
                if abs(location.x - location_.x) <= 1:
                    if (
                        location.y <= location_.y <= location.y + len(word) - 1
                        or location_.y <= location.y <= location_.y + len(word_) - 1
                    ):
                        penalty += 1
            elif location.direction == Direction.VERTICAL and location_.direction == Direction.VERTICAL:
                # check if two are located next to each other
                if abs(location.y - location_.y) <= 1:
                    if (
                        location.x <= location_.x <= location.x + len(word) - 1
                        or location_.x <= location.x <= location_.x + len(word_) - 1
                    ):
                        penalty += 1
            elif location.direction == Direction.HORIZONTAL and location_.direction == Direction.VERTICAL:
                # check if intersection is same character
                if location.y <= location_.y <= location.y + len(word) - 1:
                    if location_.x <= location.x <= location_.x + len(word_) - 1:
                        if word[location_.y - location.y] != word_[location.x - location_.x]:
                            penalty += 1
            elif location.direction == Direction.VERTICAL and location_.direction == Direction.HORIZONTAL:
                # check if intersection is same character
                if location.x <= location_.x <= location.x + len(word) - 1:
                    if location_.y <= location.y <= location_.y + len(word_) - 1:
                        if word[location_.x - location.x] != word_[location.y - location_.y]:
                            penalty += 1

    if penalty == 0:
        return float("inf")
    return 1 / penalty


def initial_population(
    words: list[str],
    population_size: int,
    fitness: Callable[[Crossword], float],
) -> list[Crossword]:
    population = [Crossword(words) for _ in range(population_size)]
    population.sort(key=fitness)
    return population


def replace_population(
    population: list[Crossword],
    new_individuals: list[Crossword],
    fitness: Callable[[Crossword], float],
) -> list[Crossword]:
    size = len(population)
    population.extend(new_individuals)
    population.sort(key=lambda x: fitness(x))
    return population[-size:]


def get_parents(
    population: list[Crossword],
    offsprings_size: int,
) -> tuple[list[Crossword], list[Crossword]]:
    mothers = population[-2 * offsprings_size :: 2]
    fathers = population[-2 * offsprings_size + 1 :: 2]
    return mothers, fathers


def cross(mother: Crossword, father: Crossword) -> Crossword:
    locations = []
    for mother_location, father_location in zip(mother.locations, father.locations):
        locations.append(random.choice((mother_location, father_location)))
    return Crossword(mother.words.copy(), locations)


def mutate(offspring: Crossword) -> Crossword:
    offspring = deepcopy(offspring)
    i = random.randint(0, len(offspring.locations) - 1)
    offspring.locations[i] = Location(
        random.randint(0, offspring.N - 1),
        random.randint(0, offspring.N - 1),
        random.choice((Direction.HORIZONTAL, Direction.VERTICAL)),
    )
    return offspring


def evolution_step(
    population: list[Crossword],
    fitness: Callable[[Crossword], float],
    offsprings_size: int,
):
    mothers, fathers = get_parents(population, offsprings_size)
    offsprings = []

    for mother, father in zip(mothers, fathers):
        offspring = mutate(cross(mother, father))
        offsprings.append(offspring)

    new_population = replace_population(population, offsprings, fitness)
    return new_population


def solution(
    words: list[str],
    fitness: Callable[[Crossword], float],
    population_size: int = 400,
    offsprings_size: int = 100,
    generations: int = 200,
) -> Crossword:
    population = initial_population(words, population_size, fitness)
    best_individual = population[0]
    fitness_change: list[float] = []
    # for generation in range(generations):
    generation = 0
    while True:
        population = evolution_step(population, fitness, offsprings_size)
        best_individual = population[-1]
        best_fitness = fitness(best_individual)
        fitness_change.append(best_fitness)

        if generation % 100 == 0:
            print("-" * 20)
            print(f"Generation #{generation}")
            print(f"Fitness: {best_fitness}")
            print(best_individual)
            print()

        if best_fitness == float("inf"):
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

    return best_individual


def get_number_input(path: str, prefix: str = "input") -> str:
    new_path = path.split("/")[-1]
    new_path = path.split(".")[0]
    new_path = new_path.replace(prefix, "")
    return new_path


def get_inputs(directory: str = "inputs") -> list[str]:
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist!")
    files = os.listdir(directory)
    files = list(filter(lambda x: get_number_input(x).isdigit(), files))
    files.sort(key=lambda x: int(get_number_input(x)))
    return files


def prepare_outputs(directory: str = "outputs") -> None:
    if not os.path.isdir(directory):
        os.mkdir(directory)


def read_words(path: str) -> list[str]:
    with open(path, "r") as fp:
        words = fp.readlines()
    words = list(map(str.strip, words))
    return words


def main(inputs: str = "inputs", outputs: str = "outputs") -> None:
    files = get_inputs()
    prepare_outputs()

    for file in files:
        words = read_words(os.path.join(inputs, file))
        crossword = solution(words, fitness)
        with open(os.path.join(outputs, file.replace("input", "output")), "w") as fp:
            for location in crossword.locations:
                fp.write(str(location) + "\n")


if __name__ == "__main__":
    main()
