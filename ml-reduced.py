import six
import sys
sys.modules['sklearn.externals.six'] = six
import mlrose
import numpy as np
from utils_simple import *
import mlrose
import numpy as np

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics import accuracy_score

# Define decay schedule
schedule = mlrose.ExpDecay()

rows = read_data("test.xlsx")
dates = get_all_dates(rows)
# grounds = init_ground_availability(rows)
matches = init_matches(rows)

def init_match_states():
    match_states = []
    for i in range(len(matches)):
        match_states.append(1)
    return [0, 1, 2, 3, 4, 5, 6, 7, 8, 2, 8, 1, 3, 4, 5, 6, 7, 5, 8, 0, 3, 4, 13, 14, 14, 7, 10, 13, 0, 3, 5, 6, 0, 4, 11, 15, 1, 8, 2, 8, 2, 0, 3, 12, 5, 9, 10, 11, 12, 13, 14, 15, 16, 17, 16, 12, 17, 11, 13, 14, 15, 10, 6, 9, 12, 11, 7, 17, 15, 15, 9, 16, 17, 1, 4, 16, 7, 2, 10, 13, 17, 10, 14, 6, 9, 12, 1, 11, 16, 9]
    return match_states

def is_match_okay(a_match):
    fixture_home_team = a_match["Home"]
    fixture_away_team = a_match["Away"]
    fixture_match_date = a_match["Date"]
    not_satisfied = False
    for the_match in matches:
        if a_match == the_match:
            continue
        if fixture_match_date == the_match["Date"]:
            if fixture_home_team in [the_match["Home"], the_match["Away"]]:
                not_satisfied = True
            elif fixture_away_team in [the_match["Home"], the_match["Away"]]:
                not_satisfied = True

    home_team_row = get_row_for_team(rows, a_match["Home"])
    away_team_row = get_row_for_team(rows, a_match["Away"])
    if home_team_row[a_match["Date"]] == "No Play":
        not_satisfied = True
    if away_team_row[a_match["Date"]] == "No Play":
        not_satisfied = True

    if home_team_row[a_match["Date"]] == "Home":
        not_satisfied = False
    if home_team_row[a_match["Date"]] == "No Home":
        not_satisfied = True
    if not_satisfied:
        return False
    return True

# Define alternative N-Queens fitness function for maximization problem
def match_fitness(match_states):
    # print (match_states)
    fitness = 0
    not_satisfied = False
    # for all dates
    for i in range(len(match_states)):
        matches[i]["Date"] = dates[match_states[i]]

    for a_match in matches:
        if not is_match_okay(a_match):
            fitness += 1

    print (fitness)
    if fitness == 0:
        print (match_states)
        sys.exit(0)

    # print (fitness)
    return fitness 

# Check function is working correctly
state = np.array(init_match_states())

# The fitness of this state should be 22
match_fitness(state)

# Initialize custom fitness function object
fitness_cust = mlrose.CustomFitness(match_fitness)

print (len(matches))
print (len(dates))
# Define optimization problem object
problem_cust = mlrose.DiscreteOpt(length = len(matches), fitness_fn = fitness_cust, maximize = False, max_val = len(dates))


# Define initial state
init_state = np.array(init_match_states())

# Solve using simulated annealing - attempt 2
best_state, best_fitness = mlrose.simulated_annealing(problem_cust, schedule = schedule, 
                                                      max_attempts = 1000000, max_iters = 100000000, 
                                                      init_state = init_state, random_state = 7)
# for date in dates:


print(best_state)

print(best_fitness)


for i in range(len(best_state)):
    matches[i]["Date"] = dates[best_state[i]]
    if not is_match_okay(matches[i]):
        print (matches[i])

