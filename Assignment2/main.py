from __future__ import annotations
import time
import os
import random
from enum import Enum
from dataclasses import dataclass


# whether to print and write to file info related to statistics:
#     * printing info about generation
#     * plotting the fitness change
#     * write execution time to file
WRITE_STATISTICS = True
# we need matplotlib to plot
if WRITE_STATISTICS:
    from matplotlib import pyplot as plt

# get path to our script, so it could find `inputs` wherever it was launched
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def randint(a: int, b: int) -> int:
    """Returns a random integer in a range.
    Works faster than the `random.randint`.

    Args:
        a (int): lower bound of the range
        b (int): upper bound of the range

    Returns:
        int: a random integer in range [a; b]
    """
    return a + int(b * random.random())


class Direction(int, Enum):
    """Enumerator for storing the direction of a word."""

    HORIZONTAL = 0
    VERTICAL = 1


@dataclass(unsafe_hash=True, order=True)
class Point:
    """Dataclass to store coordinates of a word."""

    x: int
    y: int

    def __str__(self) -> str:
        """Returns string representation for output file.

        Returns:
            str: String in format: <x> <y>
        """
        return f"{self.x} {self.y}"


@dataclass(unsafe_hash=True)
class Word:
    """Dataclass to store information about a word:
    * word itself
    * its location of the first letter
    * words' direction
    * which component of a graph it belongs to
    """

    word: str
    point: Point
    direction: Direction
    component: int

    def get_ith_point(self, index: int) -> Point:
        """Returns the location of i-th character of the word.
        If index is negative, the location is returned from the back.

        Args:
            index (int): index of the character

        Returns:
            Point: Location of this character
        """
        if index < 0:
            index = len(self.word) + index
        if self.direction == Direction.HORIZONTAL:
            return Point(self.point.x, self.point.y + index)
        else:
            return Point(self.point.x + index, self.point.y)

    def intersects(self, other: Word) -> tuple[int, int] | None:
        """If two words intersect, it returns the indicies of characters, where they intersect.
        Otherwise None is returned.

        Args:
            other (Word): Another word to check with

        Returns:
            tuple[int, int] | None: None if words do not intersect, otherwise indices of there intersection
        """
        # here we check only words that are perpendicular
        if self.direction == other.direction:
            return None
        if self.direction == Direction.HORIZONTAL:
            # check that x coordinate of the first word (horizontal) is located between
            # the x coordinates of the second word (vertical)
            # And that y coordinate of the second word (vertical) is located between
            # the y coordinates of the first word (horizontal)
            if (
                other.point.x <= self.point.x <= other.point.x + len(other.word) - 1
                and self.point.y <= other.point.y <= self.point.y + len(self.word) - 1
            ):
                return other.point.y - self.point.y, self.point.x - other.point.x
        else:
            # we check the same thing as in the first condition, but the first and
            # the second words are swapped, due to the first word being vertical
            if (
                self.point.x <= other.point.x <= self.point.x + len(self.word) - 1
                and other.point.y <= self.point.y <= other.point.y + len(other.word) - 1
            ):
                return other.point.x - self.point.x, self.point.y - other.point.y
        # two words are perpendicular but do not intersect
        return None

    def parallel_close(self, other: Word) -> int:
        if self.direction != other.direction:
            return 0
        if self.direction == Direction.HORIZONTAL:
            if abs(self.point.x - other.point.x) > 1:
                return 0
            if self.point.x == other.point.x and (
                self.point.y + len(self.word) - 1 >= other.point.y + len(other.word) - 1 >= self.point.y - 1
                or other.point.y + len(other.word) - 1 >= self.point.y + len(self.word) - 1 >= other.point.y - 1
            ):
                delta = abs(
                    min(self.point.y + len(self.word) - 1, other.point.y + len(other.word) - 1)
                    - max(self.point.y, other.point.y)
                )
                return delta
            elif (
                self.point.y <= other.point.y <= self.point.y + len(self.word) - 1
                or other.point.y <= self.point.y <= other.point.y + len(other.word) - 1
            ):
                delta = min(self.point.y + len(self.word) - 1, other.point.y + len(other.word) - 1) - max(
                    self.point.y, other.point.y
                )
                return delta
        else:
            if abs(self.point.y - other.point.y) > 1:
                return 0
            if self.point.y == other.point.y and (
                self.point.x + len(self.word) - 1 >= other.point.x + len(other.word) - 1 >= self.point.x - 1
                or other.point.x + len(other.word) - 1 >= self.point.x + len(self.word) - 1 >= other.point.x - 1
            ):
                delta = abs(
                    min(self.point.x + len(self.word) - 1, other.point.x + len(other.word) - 1)
                    - max(self.point.x, other.point.x)
                )
                return delta
            elif (
                self.point.x <= other.point.x <= self.point.x + len(self.word) - 1
                or other.point.x <= self.point.x <= other.point.x + len(other.word) - 1
            ):
                delta = min(self.point.x + len(self.word) - 1, other.point.x + len(other.word) - 1) - max(
                    self.point.x, other.point.x
                )
                return delta
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
        self.fitness: float | None = None
        self.components: list[bool] = [False] * len(words)

        self.words: list[Word] = []
        for i, word in enumerate(words):
            direction = Direction.HORIZONTAL if random.random() < 0.5 else Direction.VERTICAL
            dx = len(word) if direction == Direction.VERTICAL else 0
            dy = len(word) if direction == Direction.HORIZONTAL else 0
            x0, y0 = randint(0, N - 1 - dx), randint(0, N - 1 - dy)
            self.words.append(Word(word, Point(x0, y0), direction, i))
            self.components[i] = True

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
                        penalty += abs(ord(word1.word[intersection1]) - ord(word2.word[intersection2]))  # 3

                    if word1.component != word2.component:
                        if self.components[word1.component] and self.components[word2.component]:
                            self.components[word1.component] = False
                            word1.component = word2.component
                        elif self.components[word1.component] and not self.components[word2.component]:
                            word2.component = word1.component
                        else:
                            word1.component = word2.component

                penalty += word1.parallel_close(word2) * 8

                if word1.intersect_close(word2):
                    penalty += 30
        penalty += (sum(self.components) - 1) * 12
        return -penalty

    def __str__(self) -> str:
        """Returns a string (grid-like) representation of the crossword.

        Returns:
            str: Grid-like representation of the crossword.
        """

        grid = [["." for _ in range(self.N)] for _ in range(self.N)]
        for word in self.words:
            for i in range(len(word.word)):
                point = word.get_ith_point(i)
                grid[point.x][point.y] = word.word[i]

        string = ""
        for row in grid:
            string += " ".join(row) + "\n"

        # remove the last new-line symbol
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
    crossword = Crossword([])
    crossword.fitness = None
    crossword.components = [False] * len(mother.words)

    index = randint(0, len(mother.words) - 1)
    for i in range(0, index):
        word = Word(
            mother.words[i].word,
            mother.words[i].point,
            mother.words[i].direction,
            mother.words[i].component,
        )
        crossword.words.append(word)
        crossword.components[i] = True
    for i in range(index, len(mother.words)):
        word = Word(
            father.words[i].word,
            father.words[i].point,
            father.words[i].direction,
            father.words[i].component,
        )
        crossword.words.append(word)
        crossword.components[i] = True

    # for i in range(len(mother.words)):
    #     if random.random() < 0.5:
    #         word = Word(
    #             mother.words[i].word,
    #             mother.words[i].point,
    #             mother.words[i].direction,
    #             mother.words[i].component,
    #         )
    #     else:
    #         word = Word(
    #             father.words[i].word,
    #             father.words[i].point,
    #             father.words[i].direction,
    #             father.words[i].component,
    #         )
    #     crossword.words.append(word)
    #     crossword.components[i] = True

    return crossword


def mutate(offspring: Crossword, probability) -> Crossword:
    offspring.components = [False] * len(offspring.words)
    for i in range(len(offspring.words)):
        if random.random() < probability:
            direction = Direction.HORIZONTAL if random.random() < 0.5 else Direction.VERTICAL
            dx = len(offspring.words[i].word) if direction == Direction.VERTICAL else 0
            dy = len(offspring.words[i].word) if direction == Direction.HORIZONTAL else 0
            x0, y0 = randint(0, offspring.N - 1 - dx), randint(0, offspring.N - 1 - dy)

            offspring.words[i].point = Point(x0, y0)
            offspring.words[i].direction = direction
        offspring.words[i].component = i
        offspring.components[i] = True

    offspring.fitness = None
    return offspring


def evolution_step(population: list[Crossword], offsprings_size: int, mutation_rate: float = 0.4) -> list[Crossword]:
    mothers, fathers = get_parents(population, offsprings_size)
    offsprings = []

    for mother, father in zip(mothers, fathers):
        offsprings.append(mutate(cross(mother, father), mutation_rate))

    new_population = replace_population(population, offsprings)
    return new_population


def solution(words: list[str], population_size: int = 100, offsprings_size: int = 40) -> tuple[Crossword, int, float]:
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

    same_fitness = 0
    same_threshold = 300  # 1000 * len(words)
    last_fitness = float("inf")
    while True:
        population = evolution_step(population, offsprings_size)
        best_individual = population[-1]
        best_fitness = best_individual.get_fitness()
        if last_fitness != float("inf"):
            if best_fitness == last_fitness:
                same_fitness += 1
            else:
                same_fitness = 0
        if same_fitness >= same_threshold:
            population = initial_population(words, population_size)
            same_fitness = 0
        last_fitness = best_fitness

        if WRITE_STATISTICS:
            fitness_change.append(best_fitness)

        if WRITE_STATISTICS and generation % 100 == 0:
            print("-" * 20)
            print(f"Generation #{generation}")
            print(f"Fitness: {best_fitness}")
            print(best_individual)
            print()

        if best_fitness == 0:
            break
        generation += 1

    if WRITE_STATISTICS:
        print("-" * 20)
        print(f"Generation #{generation}")
        print(f"Fitness: {best_fitness}")
        print(best_individual)
        print()
        if plt:
            plt.plot(fitness_change)
            plt.title("Change of a fitness score")
            plt.xlabel("Generation")
            plt.ylabel("Fitness score")
            plt.show()

    return best_individual, generation, best_fitness


def get_number_input(path: str, prefix: str = "input") -> str:
    """Get the number of the test from the file name.
    If the input file is not named in the following way: <prefix>N.txt,
    the function will return whatever is between prefix and file type.

    Args:
        path (str): Path to input file
        prefix (str, optional): What prefix is used in file names. Defaults to "input".

    Returns:
        str: Number of the test from the file name
    """
    file_name = os.path.basename(path)
    file_name = os.path.splitext(file_name)[0]
    file_name = file_name.replace(prefix, "")
    return file_name


def get_inputs(directory: str = "inputs") -> list[str]:
    """Return list of input file names sorted by number of lines in them.

    Args:
        directory (str, optional): Path to the input directory. Defaults to "inputs".

    Raises:
        FileNotFoundError: The directory does not exist

    Returns:
        list[str]: File names
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist!")

    files = os.listdir(directory)

    # count number of lines
    lines = []
    for file in files:
        with open(os.path.join(directory, file), "r") as fp:
            lines.append(sum(1 for _ in fp))

    # sort by number of lines
    return [file for _, file in sorted(zip(lines, files))]


def prepare_outputs(directory: str = "outputs") -> None:
    """Create output directory if it does not exist.

    Args:
        directory (str, optional): Path to the output directory. Defaults to "outputs".
    """
    if not os.path.isdir(directory):
        os.mkdir(directory)


def read_words(path: str) -> list[str]:
    """Read words from a file.

    Args:
        path (str): Path to the file

    Returns:
        list[str]: List of the words from the file
    """
    with open(path, "r") as fp:
        words = fp.readlines()
    words = list(map(str.strip, words))
    return words


def main(inputs_dir: str = "gleb", outputs_dir: str = "outputs") -> None:
    """The main function of the solution that reads the input files from `inputs_dir`
    runs the solution on a test, and writes the output with solution to `outputs_dir`.

    Args:
        inputs_dir (str, optional): Name of the input directory. Defaults to "inputs".
        outputs_dir (str, optional): Name of the output directory. Defaults to "outputs".
    """
    # prepend the path to the directory with our script
    inputs_dir = os.path.join(__location__, inputs_dir)
    outputs_dir = os.path.join(__location__, outputs_dir)

    # get input files (sorted by number of words in it)
    files = get_inputs(inputs_dir)
    # create the output folder
    prepare_outputs(outputs_dir)

    # open the statistics file if needed
    stat = None
    if WRITE_STATISTICS:
        stat = open("statistics.csv", "w")
        stat.write("test,time,generation,fitness,words\n")

    for file in files:
        # read the words from the file
        words = read_words(os.path.join(inputs_dir, file))

        # check the start time and execute the solution
        start_time = time.time()
        try:
            crossword, generation, best_fitness = solution(words)
        except KeyboardInterrupt:
            break
        end_time = time.time()

        # write to output file
        with open(os.path.join(outputs_dir, file.replace("input", "output")), "w") as fp:
            for word in crossword.words:
                fp.write(str(word) + "\n")

        # write to statistics file if needed
        if WRITE_STATISTICS and stat:
            stat.write(f"{file},{round(end_time-start_time, 3)},{generation},{best_fitness},{len(words)}\n")
            stat.flush()

    # close the statistics file if needed
    if WRITE_STATISTICS and stat:
        stat.close()


if __name__ == "__main__":
    main()
