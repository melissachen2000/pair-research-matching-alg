import pandas as pd
import random

NUM_GROUPS = 8

help_requests = pd.read_csv("help_requests.csv")

num_subgroups = len(help_requests) // NUM_GROUPS

lab_encoding = help_requests["Which SESP research lab(s) are you affiliated with or do you interact with often?"].unique()
random.shuffle(lab_encoding)

lab_encoding = list(lab_encoding)

shuffled_requests = help_requests.sample(frac=1, random_state=random.randint(0,100)).reset_index(drop=True)
shuffled_requests["Which SESP research lab(s) are you affiliated with or do you interact with often?"] = help_requests["Which SESP research lab(s) are you affiliated with or do you interact with often?"].apply(lambda x: lab_encoding.index(x))
shuffled_requests = shuffled_requests.sort_values(by="Which SESP research lab(s) are you affiliated with or do you interact with often?").reset_index(drop=True)

subgroups = [[] for i in range(num_subgroups)]

for i, row in shuffled_requests.iterrows():
  subgroups[i % num_subgroups].append(row["Name"] + ": " + row["What would you like help on during today\'s session?"].replace("\n", " ") + "\n")


with open("help_requests.txt", "w+") as f:
  for i, subgroup in enumerate(subgroups):
    f.write(f"Group {i + 1}:\n")
    for request in subgroup:
        f.write(request)
    f.write("\n")
