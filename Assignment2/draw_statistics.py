import os
import pandas as pd
import matplotlib.pyplot as plt


os.makedirs("figures", exist_ok=True)


df = pd.read_csv("statistics.csv")

time_mean = []
time_max = []
generation_mean = []
generation_max = []
fitness_mean = []
fitness_max = []

word_nums = sorted(df["words"].unique())
for word_num in word_nums:
    filtered = df.loc[df["words"] == word_num]

    time_mean.append(filtered["time"].mean())
    time_max.append(filtered["time"].max())

    generation_mean.append(filtered["generation"].mean())
    generation_max.append(filtered["generation"].max())

    fitness_mean.append(filtered["fitness"].mean())
    fitness_max.append(filtered["fitness"].max())

titles = iter(
    [
        "Time (mean), s",
        "Time (max), s",
        "Generation (mean), #",
        "Generation (max), #",
        "Fitness (mean), #",
        "Fitness (max), #",
    ]
)
for y in time_mean, time_max, generation_mean, generation_max, fitness_mean, fitness_max:
    title = next(titles)
    plt.plot(word_nums, y, marker='o')
    plt.title(title)
    plt.savefig(f"figures/{title}.png")
    plt.show()
