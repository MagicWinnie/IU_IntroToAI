import sys
import pandas as pd


if len(sys.argv) != 3:
    print("Usage: python test_one.py PATH_TO_CSV PATH_TO_ANSWERS")
    exit(1)


df = pd.read_csv(sys.argv[1])

tests = df["TEST"]
answers = df["ANSWER"].tolist()
times = df["TIME"].tolist()

print("MAX TIME:", max(times))

for test, time in zip(tests, times):
    if time >= 3:
        print(test, time)

print("ANSWERS:")
for t, a in zip(tests, answers):
    ans = -1
    with open(sys.argv[2] + t.split('/')[-1], "r") as fp:
        ans = int(fp.readline())
    if ans != a:
        print(f"\t{t}\t{a}\t{ans}")
print()
