import pandas as pd

help_requests = pd.read_csv("help_requests.csv")

output = ""

for _, row in help_requests.iterrows():
  output += row["Name"] + ": " + row["What would you like help on during today\'s session?"].replace("\n", " ") + "\n"

with open("help_requests.txt", "w+") as f:
  f.write(output)