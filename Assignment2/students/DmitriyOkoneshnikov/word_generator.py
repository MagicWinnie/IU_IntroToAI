import random
import requests

response = requests.get("https://www.mit.edu/~ecprice/wordlist.10000")
words = response.content.splitlines()
words = [word.decode("utf-8") for word in words]


def generate_random_word():
    return random.choice(words)


def normalize_word(word):
    """Convert the word to lowercase and remove non-alphabetic characters"""
    return "".join(char.lower() for char in word if char.isalpha())


def calculate_similarity(word1, word2):
    # Normalize the words
    normalized_word1 = normalize_word(word1)
    normalized_word2 = normalize_word(word2)

    # Ensure that the lengths of the normalized words are equal
    length = max(len(normalized_word1), len(normalized_word2))
    normalized_word1 = normalized_word1.ljust(length, " ")
    normalized_word2 = normalized_word2.ljust(length, " ")

    # Calculate the similarity based on the number of similar characters
    similar_chars = sum(c1 == c2 for c1, c2 in zip(normalized_word1, normalized_word2))
    similarity = similar_chars / length

    return similarity


def generate_random_words(no_of_words):
    words = []

    # Take long words
    for _ in range(no_of_words // 3):
        new_word = generate_random_word()
        while len(new_word) <= 8 or new_word in words:
            new_word = generate_random_word()
        words.append(new_word)

    # Take normal words
    for _ in range(no_of_words // 3 + no_of_words % 3):
            new_word = generate_random_word()
            while not (5 <= len(new_word) <= 8) or new_word in words:
                new_word = generate_random_word()
            words.append(new_word)

    # Take short words
    for _ in range(no_of_words // 3):
        new_word = generate_random_word()
        while len(new_word) < 3 or len(new_word) > 5 or new_word in words:
            new_word = generate_random_word()
        words.append(new_word)

    # Ensure similarity factor
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            while calculate_similarity(words[i], words[j]) < 0.25:
                new_word = generate_random_word()
                if len(new_word) < 3 or new_word in words:
                    continue
                words[j] = new_word

    return sorted(words, key=len)


if __name__ == "__main__":
    A = 3
    B = 10
    t = 1
    for j in range(A, B + 1):
        for i in range(100 // (B - A + 1)):
            random_words = generate_random_words(j)
            with open(f"inputs/input{t}.txt", "w") as f:
                for word in random_words:
                    f.write(word + "\n")
            t += 1
