# How to use the hacky version of the pair research algorithm 

_(also known as: two google forms strung together with ~duck~ python tape. report any and all issues to melissa chen)_

## Setup

1. Clone or download the repository at https://github.com/melissachen2000/pair-research-matching-alg
2. Optionally, add some descriptions to the help request signup form. In the "form description" area (right below the title), it might help to put the goals of the activity and your expectations. In the description for the "what would you like help on?" question (to add a description, click on the three dots on the bottom right; please don't edit the question itself since it will definitely break the system), it might be helpful to put some examples of what would be good help requests.


## Running pair research

Note: for all python commands listed below, they might be run using `python3` instead of `python` as the keyword, depending on your system (I don't really get it lol). For example the instructions may say `python hello_world.py` but your system might require you to run it as `python3 hello_world.py`. 

1. Make sure that you have python installed on your computer. Open a terminal and navigate to the directory where you cloned the PR repository. 
    - It may be easier to open the folder in finder / file explorer, then right click and click "open in terminal" or a similar ccommand
    - If you need to do it manually, figure out the path of the folder (it will look something like `C:/user/<your name>/downloads/...`), copy that, and then type into the command line `cd ` then paste in what you copied (with a space between `cd` and your paste)
    - To confirm you are in the right place, type `ls` into your command line, and there should be a file in there called `pair_research.py` and another file called `hacky_generate_form.py`
2. Create a new virtual environment by running `python -m venv pr_venv`, activate it with `source pr_venv/bin/activate` and install the packages with `pip install -r requirements.txt`
3. Send out the pair research help request form to the participants. 
4. Once they are done submitting requests, link the results to a spreadsheet (DO NOT do this beforehand) and download the results as a CSV. Name this file `help_requests.csv` and move it to the root folder of the repository. 
5. Run `python hacky_generate_form.py` from the command line. The output will be `help_requests.txt`. For each group, do the following:
    1. Copy the list of names and help requests under each group heading.
    2. Make a copy of the Pair Requests Rating google form. Edit the last question such that each row is a help request. You should be able to do this by clicking on the filler text ("Row 1"), deleting it, then pasting what you copied from the txt file. The formatting should handle itself such that each row is one help request.
7. Send the rating form to the participants. Tell them that they **_MUST_** use the same email address that they used to fill out the first form. _This system will break if they do not use the same email address. It doesn't have to be their Northwestern email, but it has to be the same spelling (different capitalization is ok)._
8. Once they are done rating requests, link the results to a spreadsheet (DO NOT do this beforehand) and download the results as a CSV. Name this file `ratings.csv` and move it to the root folder of the repository. 
9. Run the command `python hacky_compute_affinities.py` from the command line. The output will be `pairings.txt`. 
    - Honestly, this is pretty fragile, and it might break for any sort of reason. If there is an error or the script outputs "Oh no...", you could either debug on the fly or just do random pairings. Sorry in advance if this happens.

## Quick note

This is running the same pair research algorithm as the website, but with one major difference: the original algorithm does not assign trios. If there is an odd number of participants, it will pair someone with "looking at pictures of Stella." I changed this so that it will (naively) put that person in a trio with the pair that they have the highest combined affinity score with. This is far from optimal, but will do for now.