import random
from copy import deepcopy


def stable_roommates(preferences):
    """
    Runs complete algorithm returns a stable matching, if exists.

    Input:
        preferences (matrix, list of lists): n-by-m preference matrix containing preferences for each person.
            m = n - 1, so each person has rated all other people.

    Return:
        (list of tuples): stable matching, if exists. Otherwise, None.
    """
    # create a preference lookup table
    # person_number : [list of preferences]
    preferences_dict = {str(x + 1): [str(y) for y in preferences[x]] for x in xrange(len(preferences))}

    # create a dict of dicts holding index of each person ranked
    # person number : {person : rank_index }
    ranks = {index: dict(zip(value, xrange(len(value)))) for index, value in preferences_dict.iteritems()}

    # phase 1: initial proposal
    p1_holds = phase_1(preferences_dict, ranks)

    # if anyone does not have a hold, stable matching is not possible
    for hold in p1_holds:
        if p1_holds[hold] is None:
            print 'Stable matching is not possible. Failed at Phase 1: not everyone was proposed to.'
            return None

    # phase 1: reduction
    p1_reduced_preferences = phase_1_reduce(preferences_dict, ranks, p1_holds)

    # phase 2: find an all-or-nothing cycle
    cycle = find_all_or_nothing_cycle(p1_reduced_preferences, ranks, p1_holds)

    # if cycle with more than size 3 does not exist, no stable matching exists
    if cycle is None:
        print 'Stable matching is not possible. Failed at Phase 2: could not find an all-or-nothing cycle.'
        return None
    elif cycle is not None and len(cycle) == 3:
        print 'Stable matching is not possible. Failed at Phase 2: could not find an all-or-nothing cycle len > 3.'
        return None

    # phase 2: reduction
    final_holds = phase_2_reduce(p1_reduced_preferences, ranks, cycle)

    # check if holds are not empty
    if final_holds is not None:
        return final_holds
    else:
        print 'Stable matching is not possible. Failed at Phase 2 reduction.'
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
                break

            # if proposee is proposed to, reject proposee_hold and continue proposal with them
            proposer = proposee_hold

        # successful proposal
        proposed_set.add(proposee)

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
        (list): cycle of users
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
