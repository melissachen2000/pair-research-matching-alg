# pair-research-matching-alg
Computes maximal weighted matching on a graph. Used for pair research.


**Instructions**: python pairedresearch.py weights-test.txt


Example:

Input: [(0, 1, 93), (0, 2, -20), (0, 3, 2), (1, 2, -13), (1, 3, 10), (2, 3, 80)]
* Matching person 0 and person 1 gives a score of 93
* Matching person 0 and person 2 gives a score of -20
* Matching person 0 and person 3 gives a score of 2
* Matching person 1 and person 2 gives a score of -13
* Matching person 1 and person 3 gives a score of 10
* Matching person 2 and person 3 gives a score of 80


Output: [1, 0, 3, 2]
* Person 0 is matched with person 1
* Person 1 is matched with person 0
* Person 2 is matched with person 3
* Person 3 is matched with person 2