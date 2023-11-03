import pandas as pd


a_star_1 = pd.read_csv("a_star_variant_1.csv")
a_star_2 = pd.read_csv("a_star_variant_2.csv")
backtracking_1 = pd.read_csv("backtracking_variant_1.csv")
backtracking_2 = pd.read_csv("backtracking_variant_2.csv")

tests = a_star_1["TEST"]

answers_a_star_1 = a_star_1["ANSWER"].tolist()
answers_a_star_2 = a_star_2["ANSWER"].tolist()
answers_backtracking_1 = backtracking_1["ANSWER"].tolist()
answers_backtracking_2 = backtracking_2["ANSWER"].tolist()

times_a_star_1 = a_star_1["TIME"].tolist()
times_a_star_2 = a_star_2["TIME"].tolist()
times_backtracking_1 = backtracking_1["TIME"].tolist()
times_backtracking_2 = backtracking_2["TIME"].tolist()


print("MAX TIME:")
print("\tA* V1:", max(times_a_star_1))
print("\tA* V2:", max(times_a_star_2))
print("\tB V1:", max(times_backtracking_1))
print("\tB V2:", max(times_backtracking_2))

for test, time in zip(tests, times_backtracking_1):
    if time >= 3:
        print(test, time)

print("A* variant 1:")
for t, a in zip(tests, answers_a_star_1):
    ans = -1
    with open(f"{'/'.join(t.split('/')[:-1]) + '/answers/' + t.split('/')[-1]}", "r") as fp:
        ans = int(fp.readline())
    if ans != a:
        print(f"\t{t}\t{a}\t{ans}")
print()

print("A* variant 2:")
for t, a in zip(tests, answers_a_star_2):
    ans = -1
    with open(f"{'/'.join(t.split('/')[:-1]) + '/answers/' + t.split('/')[-1]}", "r") as fp:
        ans = int(fp.readline())
    if ans != a:
        print(f"\t{t}\t{a}\t{ans}")
print()

print("Backtracking variant 1:")
for t, a in zip(tests, answers_backtracking_1):
    ans = -1
    with open(f"{'/'.join(t.split('/')[:-1]) + '/answers/' + t.split('/')[-1]}", "r") as fp:
        ans = int(fp.readline())
    if ans != a:
        print(f"\t{t}\t{a}\t{ans}")
print()

print("Backtracking variant 2:")
for t, a in zip(tests, answers_backtracking_2):
    ans = -1
    with open(f"{'/'.join(t.split('/')[:-1]) + '/answers/' + t.split('/')[-1]}", "r") as fp:
        ans = int(fp.readline())
    if ans != a:
        print(f"\t{t}\t{a}\t{ans}")
print()
