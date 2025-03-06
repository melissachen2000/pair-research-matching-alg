# How to use the hacky version of the pair research algorithm 

_(also known as: two google forms strung together with ~duck~ python tape. report any and all issues to melissa chen)_

## Setup

1. Clone or download the repository at https://github.com/melissachen2000/pair-research-matching-alg
2. Optionally, add some descriptions to the help request signup form. In the "form description" area (right below the title), it might help to put the goals of the activity and your expectations. In the description for the "what would you like help on?" question (to add a description, click on the three dots on the bottom right; please don't edit the question itself since it will definitely break the system), it might be helpful to put some examples of what would be good help requests.

## Run
1. Follow the instructions on the Google Apps Script
2. Run `python hacky_compute_affinities.py --ratings_folder <NAME OF FOLDER WHERE YOU PUT THE RATINGS CSVs>`
3. Output will be in `pairings.txt`

## Quick note

This is running the same pair research algorithm as the website, but with one major difference: the original algorithm does not assign trios. If there is an odd number of participants, it will pair someone with "looking at pictures of Stella." I changed this so that it will (naively) put that person in a trio with the pair that they have the highest combined affinity score with. This is far from optimal, but will do for now.