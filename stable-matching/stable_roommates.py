"""Stable Roommate Matching

Implementation of Robert Irving's Stable Roommates Algorithm.
http://www.dcs.gla.ac.uk/~pat/jchoco/roommates/papers/Comp_sdarticle.pdf
"""

from __future__ import print_function

import random
import unittest
from copy import deepcopy


def stable_roommates(preferences, debug=False):
    """
    Runs complete algorithm and returns a stable matching, if exists.

    Input:
        preferences (matrix, list of lists of numbers): n-by-m preference matrix containing preferences for each person.
            m = n - 1, so each person has rated all other people.
            Each row is a 1-indexed ordered ranking of others in the pool.
            Therefore max(preferences[person]) <= number people and min(preferences[person]) = 1.
        debug (boolean): including print statements

    Return:
        (list): stable matching, if exists. Otherwise, None.
            If a matching exists, -1 for a person indicates no partner.
            ex: [2, 1, -1] (Person 0 matched with 2, 1 matched with 0, 2 not matched)
    """
    # validate input
    is_valid, person_added, valid_preferences = validate_input(preferences, debug)

    if not is_valid:
        if debug:
            print('Invalid input. Must be n-by-m (where m = n - 1) list of lists of numbers.')
        return None

    # create a preference lookup table
    # person_number : [list of preferences]
    preferences_dict = {str(x + 1): [str(y) for y in valid_preferences[x]] for x in range(len(valid_preferences))}

    # create a dict of dicts holding index of each person ranked
    # person number : {person : rank_index }
    ranks = {index: dict(zip(value, range(len(value)))) for index, value in preferences_dict.iteritems()}

    # phase 1: initial proposal
    p1_holds = phase_1(preferences_dict, ranks)

    # if anyone does not have a hold, stable matching is not possible
    for hold in p1_holds:
        if p1_holds[hold] is None:
            if debug:
                print('Stable matching is not possible. Failed at Phase 1: not everyone was proposed to.')
            return None

    # phase 1: reduction
    p1_reduced_preferences = phase_1_reduce(preferences_dict, ranks, p1_holds)

    # phase 1: stable match halting condition
    # if p1_reduced_preferences has only one preference per person, matching should be stable (lemma 2)
    p1_halt = True
    for person in p1_reduced_preferences:
        if len(p1_reduced_preferences[person]) > 1:
            p1_halt = False
            break

    if p1_halt:
        # verification before returning
        if verify_matching(p1_holds):
            if verify_stability(p1_holds, ranks):
                if debug:
                    print('Stable matching found. Returning person : partner dictionary.')

                # check if person was added. if so, delete added person (n + 1) and set their match to -1
                if person_added:
                    person_str = str(len(p1_holds))
                    person_added_match = p1_holds[person_str]

                    del p1_holds[person_str]
                    p1_holds[person_added_match] = '-1'

                if debug:
                    print(p1_holds)

                return format_output(p1_holds)
            else:
                if debug:
                    print('Stable matching is not possible. Failed at Verification: matching computed, but not stable.')
                return None
        else:
            if debug:
                print('Stable matching is not possible. Failed at Verification: matching computed, but not valid.')
            return None

    # phase 2: find an all-or-nothing cycle
    cycle = find_all_or_nothing_cycle(p1_reduced_preferences, ranks, p1_holds)

    # if cycle with more than size 3 does not exist, no stable matching exists
    if cycle is None:
        if debug:
            print('Stable matching is not possible. Failed at Phase 2: could not find an all-or-nothing cycle.')
        return None
    elif cycle is not None and len(cycle) == 3:
        if debug:
            print('Stable matching is not possible. Failed at Phase 2: could not find an all-or-nothing cycle len > 3.')
        return None

    # phase 2: reduction
    final_holds = phase_2_reduce(p1_reduced_preferences, ranks, cycle)

    # check if holds are not empty
    if final_holds is not None:
        # verification
        if verify_matching(final_holds):
            if verify_stability(final_holds, ranks):
                if debug:
                    print('Stable matching found. Returning person : partner dictionary.')

                # check if person was added. if so, delete added person (n + 1) and set their match to -1
                if person_added:
                    person_str = str(len(final_holds))
                    person_added_match = final_holds[person_str]

                    del final_holds[person_str]
                    final_holds[person_added_match] = '-1'

                if debug:
                    print(final_holds)

                return format_output(final_holds)
            else:
                if debug:
                    print('Stable matching is not possible. Failed at Verification: matching computed, but not stable.')
                return None
        else:
            if debug:
                print('Stable matching is not possible. Failed at Verification: matching computed, but not valid.')
            return None
    else:
        if debug:
            print('Stable matching is not possible. Failed at Phase 2 reduction.')
        return None


def phase_1(preferences, ranks, curr_holds=None):
    """
    Performs first phase of matching by doing round robin proposals until stopping condition (i) or (ii) is met:
         (i) each person is holding a proposal
        (ii) one person is rejected by everyone

    Input:
        preferences (dict of list of strings): dict of ordered preference lists {person : [ordered list]}
        ranks (dict of dict of ranking index): dict of persons with dicts indicating rank of each other person
        curr_holds (dict, optional): dict of persons with current holds

    Return:
        (dict): holds after condition (i) or (ii) is met.
    """
    people = preferences.keys()

    # placeholder for holds
    holds = {person: None for person in people}

    # during phase 1, no holds exist. initialize curr_holds to 0 (all people are > 0)
    if curr_holds is None:
        curr_holds = {person: 0 for person in people}

    # randomize ordering of proposal
    random.shuffle(people)

    # track people who are already proposed to
    proposed_set = set()

    # begin proposing
    for person in people:
        proposer = person

        # proposal step
        while True:
            # find proposer someone to propose to, in order of proposer's preference list
            while curr_holds[proposer] < len(preferences[proposer]):
                # find proposee given proposer's preferences
                proposee = preferences[proposer][curr_holds[proposer]]
                curr_holds[proposer] += 1

                # find who proposee is holding, if any
                proposee_hold = holds[proposee]

                # stop searching if proposee doesn't hold anyone or ranks proposer higher than curr hold
                if proposee_hold is None or ranks[proposee][proposer] < ranks[proposee][proposee_hold]:
                    # proposee holds proposer's choice
                    holds[proposee] = proposer
                    break

            # check if proposee has already been proposed to
            if proposee not in proposed_set:
                # successful proposal
                proposed_set.add(proposee)
                break

            # if all preferences are exhausted and proposee does not have anyone, stop
            if curr_holds[proposer] >= len(preferences[proposer]):
                break

            # if proposee is proposed to, reject proposee_hold and continue proposal with them
            proposer = proposee_hold

    # final holds from phase 1
    return holds


def phase_1_reduce(preferences, ranks, holds):
    """
    Performs a reduction on preferences based on phase 1 proposals, and the following:
        Preference list for y who holds proposal x can be reduced by deleting
             (i) all those to whom y prefers x
            (ii) all those who hold a proposal from a person they prefer to y

    Input:
        preferences (dict of list of strings): dict of ordered preference lists {person : [ordered list]}
        ranks (dict of dict of ranking index): dict of persons with dicts indicating rank of each other person
        holds (dict): dict of persons with current holds

    Return:
        (dict of list of strings): reduced preference list such that:
            (iii) y is the first on x's list and last on y's
             (iv) b appears on a's list iff a appears on b's
    """
    # create output preferences
    reduced_preferences = deepcopy(preferences)

    # loop though each hold
    for proposee in holds:
        proposer = holds[proposee]

        # loop though all of person's preferences
        i = 0
        while i < len(reduced_preferences[proposee]):
            # fetch proposee's preferences
            curr_proposee_preference = reduced_preferences[proposee][i]

            # proposee should only hold preferences equal and higher to proposer (i)
            if curr_proposee_preference == proposer:
                reduced_preferences[proposee] = reduced_preferences[proposee][:(i + 1)]
            # delete all people who hold a proposal from someone they prefer to the proposee (ii)
            elif ranks[curr_proposee_preference][holds[curr_proposee_preference]] < \
                    ranks[curr_proposee_preference][proposee]:
                reduced_preferences[proposee].pop(i)
                continue

            # continue to preference list
            i += 1

    return reduced_preferences


def find_all_or_nothing_cycle(preferences, ranks, holds):
    """
    Finds an all-or-nothing cycle in reduced preferences, if exists.

    Input:
        preferences (dict of list of strings): dict of ordered preference lists {person : [ordered list]}
        ranks (dict of dict of ranking index): dict of persons with dicts indicating rank of each other person
        holds (dict): dict of persons with current holds

    Return:
        (list): cycle of persons
    """
    # start with two individuals, p and q
    p = []
    q = []

    # find a person with > 1 preference left
    curr = None
    for person in preferences:
        if len(preferences[person]) > 1:
            curr = person
            break

    # if no person can be found, no cycle exists
    if curr is None:
        return None

    # create cycle
    while curr not in p:
        # q_i = second person in p_i's list
        q += [preferences[curr][1]]

        # p_{i + 1} = q_i's last person
        p += [curr]
        curr = preferences[q[-1]][-1]

    cycle = p[p.index(curr):]

    return cycle


def phase_2_reduce(preferences, ranks, cycle):
    """
    Performs a reduction on found all-or-nothing cycles.

    Input:
        preferences (dict of list of strings): dict of ordered preference lists {person : [ordered list]}
        ranks (dict of dict of ranking index): dict of persons with dicts indicating rank of each other person
        cycle (list): all-or-nothing cycle

    Return:
        (dict): holds after sequential reductions, or None if no matching can be found.
    """
    # continue while a cycle exists
    curr_cycle = deepcopy(cycle)
    curr_holds = None
    p2_preferences = deepcopy(preferences)

    while curr_cycle is not None:
        curr_preferences = {}

        for person in preferences:
            if person in curr_cycle:
                curr_preferences[person] = 1
            else:
                curr_preferences[person] = 0

        curr_holds = phase_1(p2_preferences, ranks, curr_preferences)
        p2_preferences = phase_1_reduce(p2_preferences, ranks, curr_holds)

        curr_cycle = find_all_or_nothing_cycle(p2_preferences, ranks, curr_holds)

    return curr_holds


def validate_input(preference_matrix, debug=False):
    """
    Makes sure a preference matrix is n-by-m and m = n - 1.
        If each isn't full, fill the list with the remaining people.
        If n is odd, add in a n + 1 person to allow matching to run.


    Input:
        preferences (matrix, list of lists of numbers): n-by-m preference matrix containing preferences for each person.
            m = n - 1, so each person has rated all other people.
            Each row is a 1-indexed ordered ranking of others in the pool.
            Therefore max(preferences[person]) <= number people and min(preferences[person]) = 1.

    Return:
        (boolean): if matrix is valid
        (boolean): if n + 1 person was added
        (matrix, list of lists numbers): filled and validated preference list
    """
    is_valid = False
    person_added = False
    output_matrix = deepcopy(preference_matrix)

    n = len(output_matrix)
    m = n - 1

    matrix_iterator = range(n)

    # validate list of lists of numbers
    if type(output_matrix) is not list:
        if debug:
            print('Input validation failed: preference_matrix is not a list.')
        return False, person_added, None

    # validate size
    if n <= 1:  # empty matrix or only 1 person (no point in matching)
        if debug:
            print('Input validation failed: preference_matrix must have size > 1')
        return False, person_added, None

    # validate content of matrix
    for i in matrix_iterator:
        sublist = output_matrix[i]

        #  each sublist is a list
        if type(sublist) is not list:
            if debug:
                print('Input validation failed: each list in preference_list should be a list.')
            return False, person_added, None

        # each preference list can only be of length m
        if len(sublist) > m:
            if debug:
                print('Input validation failed: each list in preference_list cannot have length greater than m.')
            return False, person_added, None

        # each value is an int
        for j in sublist:
            if type(j) is not int:
                if debug:
                    print('Input validation failed: all values should be integers')
                return False, person_added, None

            # number should be between 1 and n and should be the person index
            if j < 1 or j > n or j == (i + 1):
                if debug:
                    print('Input validation failed: each value in each row should be between \
                          1 and n (number of people) and cannot be the person themselves')
                return False, person_added, None

    if debug:
        print('Input validation passed.')
    is_valid = True

    # add n + 1 person if n is odd
    if n % 2 != 0:
        person_added = True
        output_matrix += [range(1, n + 1)]

    # fill any rows that are not of length m
    full_set = set(range(1, n + 1))
    for i in matrix_iterator:
        if len(output_matrix[i]) != m:
            to_add = full_set - set(output_matrix[i]) - {i + 1}
            output_matrix[i] += list(to_add)

        if person_added:
            output_matrix[i] += [n + 1]

    # returns is_valid (list of list of numbers), person_added (if n is odd), output_matrix (filled preference_matrix)
    return is_valid, person_added, output_matrix


def verify_matching(matching):
    """
    Checks if a matching is valid.
        Valid matchings have all people matched to one and only one person.

    Input:
        matching (dict): dict containing person:matching pairs

    Return:
        (boolean)): matching is valid
    """
    # validate matching
    person_set = {person for person in matching.keys()}
    matching_set = {match for match in matching.values()}

    # equal cardinality and content
    if person_set != matching_set:
        return False

    # check for a:b, then b:a
    for person in matching:
        if person != matching[matching[person]]:
            return False

    # matching is valid
    return True


def verify_stability(matching, ranks):
    """
    Checks if a valid matching (all people matched to one and only one person) is stable.
        Stable iff no two unmatched members both prefer each other to their current partners in the matching.

    Input:
        matching (dict): dict containing person:matching pairs
        ranks (dict of dict of ranking index): dict of persons with dicts indicating rank of each other person

    Output:
        (boolean): matching is stable
    """
    for x in matching:
        for y in matching:
            # ignore if x, y are the same or x, y are matched
            if x == y or y == matching[x]:
                continue

            # get partner under matching for x, y and corresponding ranks of matched partners
            x_partner = matching[x]
            y_partner = matching[y]

            x_partner_rank = ranks[x][x_partner]
            y_partner_rank = ranks[y][y_partner]

            # get ranking of x -> y, y -> x
            x_y_rank = ranks[x][y]
            y_x_rank = ranks[y][x]

            # if x prefers y to current partner AND y prefers x to current partner, unstable
            # prefer = lower ranking index since ranking is highest -> lowest preference
            if x_y_rank < x_partner_rank and y_x_rank < y_partner_rank:
                return False

    return True


def format_output(matching):
    """
    Formats holds into output that matches maximum weighted matching output.
        ex: [2, 1, -1] (Person 0 matched with 2, 1 matched with 0, 2 not matched)

    Input:
        matching (dict): dict of persons who they are matched to (-1 if unmatched)

    Return:
        (list): stable matching, if exists. Otherwise, None.
            If a matching exists, -1 for a person indicates no partner.
    """
    n = len(matching)
    output = [0 for i in range(n)]

    # convert dict to output list
    for key, value in matching.iteritems():
        int_key = int(key) - 1
        int_value = int(value)

        output[int_key] = int_value

    return output


# unit tests
if __name__ == '__main__':
    # from http://www.dcs.gla.ac.uk/~pat/jchoco/roommates/papers/Comp_sdarticle.pdf
    paper_matching_6 = [
        [4, 6, 2, 5, 3],
        [6, 3, 5, 1, 4],
        [4, 5, 1, 6, 2],
        [2, 6, 5, 1, 3],
        [4, 2, 3, 6, 1],
        [5, 1, 4, 2, 3]
    ]

    paper_matching_8 = [
        [2, 5, 4, 6, 7, 8, 3],
        [3, 6, 1, 7, 8, 5, 4],
        [4, 7, 2, 8, 5, 6, 1],
        [1, 8, 3, 5, 6, 7, 2],
        [6, 1, 8, 2, 3, 4, 7],
        [7, 2, 5, 3, 4, 1, 8],
        [8, 3, 6, 4, 1, 2, 5],
        [5, 4, 7, 1, 2, 3, 6]
    ]

    paper_no_matching_4 = [
        [2, 3, 4],
        [3, 1, 4],
        [1, 2, 4],
        [1, 2, 3]
    ]

    paper_no_matching_6 = [
        [2, 6, 4, 3, 5],
        [3, 5, 1, 6, 4],
        [1, 6, 2, 5, 4],
        [5, 2, 3, 6, 1],
        [6, 1, 3, 4, 2],
        [4, 2, 5, 1, 3]
    ]

    # from https://en.wikipedia.org/wiki/Stable_roommates_problem#Algorithm
    wiki_matching_6 = [
        [3, 4, 2, 6, 5],
        [6, 5, 4, 1, 3],
        [2, 4, 5, 1, 6],
        [5, 2, 3, 6, 1],
        [3, 1, 2, 4, 6],
        [5, 1, 3, 4, 2]
    ]

    # from http://www.dcs.gla.ac.uk/~pat/roommates/distribution/data/
    external_matching_8 = [
        [2, 5, 4, 6, 7, 8, 3],
        [3, 6, 1, 7, 8, 5, 4],
        [4, 7, 2, 8, 5, 6, 1],
        [1, 8, 3, 5, 6, 7, 2],
        [6, 1, 8, 2, 3, 4, 7],
        [7, 2, 5, 3, 4, 1, 8],
        [8, 3, 6, 4, 1, 2, 5],
        [5, 4, 7, 1, 2, 3, 6]
    ]

    external_matching_10 = [
        [8, 2, 9, 3, 6, 4, 5, 7, 10],
        [4, 3, 8, 9, 5, 1, 10, 6, 7],
        [5, 6, 8, 2, 1, 7, 10, 4, 9],
        [10, 7, 9, 3, 1, 6, 2, 5, 8],
        [7, 4, 10, 8, 2, 6, 3, 1, 9],
        [2, 8, 7, 3, 4, 10, 1, 5, 9],
        [2, 1, 8, 3, 5, 10, 4, 6, 9],
        [10, 4, 2, 5, 6, 7, 1, 3, 9],
        [6, 7, 2, 5, 10, 3, 4, 8, 1],
        [3, 1, 6, 5, 2, 9, 8, 4, 7]
    ]

    external_matching_20 = [
        [13, 12, 20, 17, 11, 6, 8, 2, 3, 14, 4, 16, 5, 10, 18, 19, 9, 15, 7],
        [13, 6, 8, 17, 18, 19, 1, 11, 7, 4, 15, 16, 5, 9, 3, 20, 12, 10, 14],
        [6, 16, 4, 9, 14, 13, 17, 19, 8, 2, 1, 12, 20, 5, 18, 15, 7, 11, 10],
        [11, 7, 8, 2, 17, 3, 15, 6, 19, 10, 9, 5, 1, 16, 13, 20, 18, 14, 12],
        [8, 17, 14, 16, 4, 13, 15, 6, 19, 9, 12, 7, 2, 3, 11, 18, 20, 10, 1],
        [8, 13, 10, 14, 18, 15, 2, 7, 4, 16, 19, 5, 9, 17, 20, 3, 11, 12, 1],
        [13, 1, 4, 9, 19, 18, 11, 14, 10, 2, 17, 6, 15, 16, 5, 3, 12, 8, 20],
        [1, 6, 20, 7, 5, 15, 19, 4, 12, 3, 17, 9, 10, 14, 16, 2, 18, 11, 13],
        [17, 13, 3, 5, 7, 4, 12, 2, 18, 20, 15, 8, 10, 1, 6, 11, 19, 14, 16],
        [9, 4, 16, 14, 18, 17, 15, 11, 20, 13, 3, 12, 2, 1, 19, 7, 5, 8, 6],
        [6, 15, 4, 1, 18, 14, 5, 3, 9, 2, 17, 13, 8, 7, 12, 20, 19, 10, 16],
        [5, 18, 7, 16, 6, 20, 19, 14, 9, 17, 3, 1, 8, 10, 11, 13, 2, 15, 4],
        [3, 10, 7, 18, 14, 15, 1, 6, 12, 4, 8, 19, 16, 17, 5, 20, 9, 11, 2],
        [2, 5, 10, 13, 19, 17, 6, 3, 18, 7, 20, 9, 1, 4, 16, 12, 15, 8, 11],
        [12, 13, 5, 11, 2, 16, 18, 14, 1, 6, 17, 8, 19, 4, 10, 7, 20, 3, 9],
        [1, 7, 6, 5, 14, 18, 12, 17, 20, 11, 15, 10, 2, 13, 3, 8, 19, 9, 4],
        [5, 8, 15, 9, 7, 18, 11, 10, 19, 2, 1, 12, 3, 14, 20, 13, 6, 16, 4],
        [14, 3, 8, 10, 13, 5, 9, 15, 12, 1, 17, 6, 16, 11, 2, 7, 4, 19, 20],
        [9, 15, 20, 12, 18, 1, 11, 5, 3, 2, 13, 14, 10, 7, 6, 16, 8, 17, 4],
        [5, 6, 18, 19, 16, 7, 4, 9, 2, 17, 8, 15, 1, 12, 13, 10, 14, 3, 11]
    ]

    # matching exists if algorithm leaves 7 unmatched
    external_matching_7 = [
        [3, 4, 2, 6, 5, 7],
        [6, 5, 4, 1, 3, 7],
        [2, 4, 5, 1, 6, 7],
        [5, 2, 3, 6, 1, 7],
        [3, 1, 2, 4, 6, 7],
        [5, 1, 3, 4, 2, 7],
        [1, 2, 3, 4, 5, 6]
    ]

    # custom test cases
    # empty matrix
    custom_no_matching_empty = []

    # one person (no matching should be possible)
    custom_no_matching_1 = [[]]

    # two people
    custom_matching_2 = [[2], [1]]

    # three people (odd: should add person and find a matching)
    custom_matching_3 = [
        [3, 2],
        [3, 1],
        [1, 2]
    ]

    # build and execute test cases
    class StableRoommatesTests(unittest.TestCase):
        def test_paper_matching(self):
            print('Running test cases from Irving\'s paper where matching is possible...')
            self.assertNotEqual(stable_roommates(paper_matching_6), None)
            self.assertNotEqual(stable_roommates(paper_matching_8), None)

        def test_paper_no_matching(self):
            print('Running test cases from Irving\'s paper where no matching is possible....')
            self.assertEqual(stable_roommates(paper_no_matching_4), None)
            self.assertEqual(stable_roommates(paper_no_matching_6), None)

        def test_wiki_matching(self):
            print('Running test cases from Stable Roommates Wikipedia article where no matching is possible....')
            self.assertNotEqual(stable_roommates(wiki_matching_6), None)

        def test_external_matching(self):
            print('Running test cases from another implementation where matching is possible....')
            self.assertNotEqual(stable_roommates(external_matching_8), None)
            self.assertNotEqual(stable_roommates(external_matching_10), None)
            self.assertNotEqual(stable_roommates(external_matching_20), None)
            self.assertNotEqual(stable_roommates(external_matching_7), None)

        def test_custom_matching(self):
            print('Running custom test cases where matching is possible....')
            self.assertNotEqual(stable_roommates(custom_matching_2), None)
            self.assertNotEqual(stable_roommates(custom_matching_3), None)

        def test_custom_no_matching(self):
            print('Running custom test cases where matching is possible....')
            self.assertEqual(stable_roommates(custom_no_matching_empty), None)
            self.assertEqual(stable_roommates(custom_no_matching_1), None)

    unittest.main()
