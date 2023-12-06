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

titles = [
    "Time (mean), s",
    "Time (max), s",
    "Generation (mean), #",
    "Generation (max), #",
    "Fitness (mean), #",
    "Fitness (max), #",
]
ys = time_mean, time_max, generation_mean, generation_max, fitness_mean, fitness_max
for i in range(0, len(ys), 2):
    for j in 0, 1:
        plt.plot(word_nums, ys[i + j], marker='o', label=titles[i + j])
        plt.title(titles[i + j].split(", ")[0])
        plt.xlabel("# of words")
        plt.ylabel(", ".join(titles[i + j].split()[::2]))
    plt.subplots_adjust(right=0.7)
    plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0)
    plt.savefig(f"figures/{titles[i].split()[0]}.png")
    plt.show()
