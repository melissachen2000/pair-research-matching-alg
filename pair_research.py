from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import json
from copy import deepcopy
from mwmatching import *
from stable_roommates import create_preference_matrix
from stable_roommates import stable_matching_wrapper as sr_matching


def adjust_undirected_graph(graph, matching):
    """
    Takes an undirected graph and negatively weights edges for those who have a valid partner in matching.

    Input:
        graph (list of tuples): each tuple represents an edge
            ex. (0, 1, 93) means an edge from 0 to 1 with a weight of 93.
        matching (list): list of numbers where unmatched people are given -1.

    Output:
        (list of tuples): graph where edges containing people with valid matchings having high negative weight.
            ex. if 0, 1 are matched then [(0, 1, 93), (0, 2, -20), (0, 3, 2), (1, 2, -13), (1, 3, 10), (2, 3, 80)]
                would become [(0, 1, -1000), (0, 2, -1000), (0, 3, -1000), (1, 2, -1000), (1, 3, -1000), (2, 3, 80)]
    """
    output_graph = deepcopy(graph)

    for edge_index in range(len(output_graph)):
        # check if from or to person has a valid match in matching
        from_person = output_graph[edge_index][0]
        to_person = output_graph[edge_index][1]

        if matching[from_person] != -1 or matching[to_person] != -1:
            output_graph[edge_index][2] = -10000

    return output_graph


if __name__ == "__main__":
    # get input from pair research meteor app
    input_pair_research = eval(sys.stdin.readlines()[0])

    # compute a stable roommates matching
    preference_matrix = create_preference_matrix(input_pair_research['directed_graph'])
    stable_result, is_fully_stable, stable_debug = sr_matching(preference_matrix, handle_odd_method='remove',
                                                               remove_all=True)

    # prepare output dict
    output_dict = {
        'matching': stable_result,
        'fully_stable': is_fully_stable,
        'stable_debug': stable_debug,
        'stable_result': stable_result,
        'mwm_result_original': maxWeightMatching(input_pair_research['undirected_graph']),
        'mwm_result_processed': []
    }

    # if not fully stable, adjust the undirected graph and run MWM
    if not is_fully_stable:
        # get mwm result with adjusted graph
        unpaired_undirected_graph = adjust_undirected_graph(input_pair_research['undirected_graph'], stable_result)
        mwm_result = maxWeightMatching(unpaired_undirected_graph)

        # combine results from stable roommates and mwm
        output_matching = deepcopy(stable_result)
        for matching_index in range(len(output_matching)):
            if output_matching[matching_index] == -1:
                output_matching[matching_index] = mwm_result[matching_index]

        # add to output dict
        output_dict['matching'] = output_matching
        output_dict['mwm_result_processed'] = mwm_result

    # print data out so meteor app can retrieve it
    print(json.dumps(output_dict))