
import pandas as pd
from pair_research import create_matching_output
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--ratings_filename", required=True)

args = argparser.parse_args()

ratings = pd.read_csv(f'{args.ratings_filename}.csv')
requests = pd.read_csv('help_requests.csv')

request_to_uuid = {
    row["Name"] + ": " + row["What would you like help on during today's session?"]:
    row["NU email"].lower().strip()
    for _, row in requests.iterrows()
}

# clean up the column names a bit so that the title of each column is a help request (that can be used to query request to uuid)

new_col_names = {}

for col in ratings.columns:
    if "Rate your interest level" not in col:
        new_col_names[col] = col.strip()
    else:
        open_index = col.index("[") + 1
        close_index = col.index("]")

        new_col_names[col] = request_to_uuid[col[open_index:close_index]]

ratings = ratings.rename(new_col_names, axis=1)

# clean up some of the data within the ratings matrix, super hacky

ratings = ratings.replace({
    "1 (not interested)": 1,
    "5 (very interested)": 5,
    "This is my help request": 0,
    "This person is in my lab or I interact with them often":-100
})

matrix = []

# computing a directed graph of ratings. rows are one person's ratings of everyone else's help requests
# going in order of the ratings columns so that we re-order the rows so that it's a proper matrix (diagonals are 0)
for col in ratings.columns:
    if "@" not in col:
        continue

    ratings[col] = ratings[col].astype(int)

    row = ratings[ratings["NU email"].str.lower().str.strip() == col]
    
    add_to_matrix = []
    for item in row.columns:
        if "@" in item:
            add_to_matrix.append(row[item].values.astype(int)[0])

    matrix.append(add_to_matrix)

for i in range(len(matrix)):
    if (matrix[i][i] != 0):
        j = matrix[i].index(0)
        print(f"Oh no, the matrix seems to be out of order! We expected a 0 in position {i} but it's actually in position {j}")
        
undirected_graph = []

# making the undirected graph version by just adding the generated affinities
# not sure this is true to the original implementation but it works
for i in range(len(matrix)):
    for j in range(len(matrix[0])):
        if i == j:
            continue
        
        undirected_graph.append([i, j, int(matrix[i][j] + matrix[j][i])])

result = create_matching_output({"directed_graph": matrix, "undirected_graph": undirected_graph}, debug=True)

pairs = set()
odd_uuid = None
odd_name = None

for i in range(len(result['matching'])):
    index_uuid = ratings.columns[i + 3]
    index_name = ratings[ratings["NU email"].str.lower().str.strip() == index_uuid]["Name"].values[0]

    if result['matching'][i] == -1:
        odd_uuid = index_uuid
        odd_name = index_name
        continue
    else:
        pair_uuid = ratings.columns[result["matching"][i] + 3]
        pair_name = ratings[ratings["NU email"].str.lower().str.strip() == pair_uuid]["Name"].values[0]

    if (index_name, index_uuid, pair_name, pair_uuid) not in pairs and (pair_name, pair_uuid, index_name, index_uuid) not in pairs:
        pairs.add((index_name, index_uuid, pair_name, pair_uuid))

# if there was an odd number of people, find the odd one out and add them to an existing pair
output = ""

if odd_uuid:
    max_pair = None
    max_affinity = -10000000000

    for p1_name, p1_uuid, p2_name, p2_uuid in pairs:
        p1_affinity = ratings[ratings["NU email"].str.lower().str.strip() == p1_uuid][odd_uuid].values[0] \
                    + ratings[ratings["NU email"].str.lower().str.strip() == odd_uuid][p1_uuid].values[0]
        p2_affinity = ratings[ratings["NU email"].str.lower().str.strip() == p2_uuid][odd_uuid].values[0] \
                    + ratings[ratings["NU email"].str.lower().str.strip() == odd_uuid][p2_uuid].values[0]

        if p1_affinity + p2_affinity > max_affinity:
            max_affinity = p1_affinity + p2_affinity
            max_pair = (p1_name, p1_uuid, p2_name, p2_uuid)

    output += f'{max_pair[0]}, {max_pair[2]}, and {odd_name} will form a group of 3\n'

    pairs.remove(max_pair)

for p1_name, _, p2_name, _ in pairs:
    output += f'{p1_name} and {p2_name} will pair\n'


with open("pairings.txt", "w+") as f:
    f.write(output)
