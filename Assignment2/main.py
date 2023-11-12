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


def fitness(individual: Crossword) -> float:
    penalty = 0

    intersections: set[Location] = set()
    for i in range(len(individual.words)):
        word, location = individual.words[i], individual.locations[i]

        # words are out of grid
        if location.direction == Direction.HORIZONTAL:
            if location.y + len(word) - 1 >= individual.N:
                penalty += 1
        elif location.direction == Direction.VERTICAL:
            if location.x + len(word) - 1 >= individual.N:
                penalty += 1

        for j in range(i + 1, len(individual.words)):
            word_, location_ = individual.words[j], individual.locations[j]
            if location == location_:
                continue
            if location.direction == Direction.HORIZONTAL and location_.direction == Direction.HORIZONTAL:
                # check if two are located next to each other
                if abs(location.x - location_.x) <= 1:
                    if (
                        location.y <= location_.y < location.y + len(word) - 1
                        or location_.y <= location.y < location_.y + len(word_) - 1
                    ):
                        penalty += 1
            elif location.direction == Direction.VERTICAL and location_.direction == Direction.VERTICAL:
                # check if two are located next to each other
                if abs(location.y - location_.y) <= 1:
                    if (
                        location.x <= location_.x < location.x + len(word) - 1
                        or location_.x <= location.x < location_.x + len(word_) - 1
                    ):
                        penalty += 1
            elif location.direction == Direction.HORIZONTAL and location_.direction == Direction.VERTICAL:
                # check if intersection is same character
                if (
                    location.y <= location_.y <= location.y + len(word) - 1
                    and location_.x <= location.x <= location_.x + len(word_) - 1
                ):
                    intersections.add(Location(location.x, location_.y, Direction.HORIZONTAL))
                    if word[location_.y - location.y] != word_[location.x - location_.x]:
                        penalty += 1
            elif location.direction == Direction.VERTICAL and location_.direction == Direction.HORIZONTAL:
                # check if intersection is same character
                if (
                    location.x <= location_.x <= location.x + len(word) - 1
                    and location_.y <= location.y <= location_.y + len(word_) - 1
                ):
                    intersections.add(Location(location_.x, location.y, Direction.HORIZONTAL))
                    if word[location_.x - location.x] != word_[location.y - location_.y]:
                        penalty += 1
    # check if connected
    penalty += max(len(individual.words) - 1 - len(intersections), 0)

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
    # cross two parents together
    # mother_head = mother[: int(len(mother) * 0.5)].copy()
    # mother_tail = mother[int(len(mother) * 0.5) :].copy()
    # father_tail = father[int(len(father) * 0.5) :].copy()

    # mapping = {father_tail[i]: mother_tail[i] for i in range(len(mother_tail))}

    # for i in range(len(mother_head)):
    #     while mother_head[i] in father_tail:
    #         mother_head[i] = mapping[mother_head[i]]

    # return np.hstack([mother_head, father_tail])
    return mother


def mutate(offspring: Crossword) -> Crossword:
    offspring = deepcopy(offspring)
    i, j = random.sample(range(len(offspring.locations)), 2)
    offspring.locations[i], offspring.locations[j] = offspring.locations[j], offspring.locations[i]
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
    population_size: int = 100,
    offsprings_size: int = 30,
    generations: int = 100,
) -> Crossword:
    population = initial_population(words, population_size, fitness)
    best_individual = population[0]
    fitness_change: list[float] = []
    for generation in range(generations):
        population = evolution_step(population, fitness, offsprings_size)
        best_individual = population[-1]
        best_fitness = fitness(best_individual)
        fitness_change.append(best_fitness)

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
