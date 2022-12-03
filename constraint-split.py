from ortools.sat.python import cp_model
from utils import *

def write_excel(results, division, rows, num):
  matches = []
  for result in results:
    ground = result[0]
    home_team = result[1]
    away_team = result[2]
    the_date  = result[3]
    division = get_division(rows, home_team)
    matches.append({"Division":division, "Home":home_team, "Away":away_team, "Ground":ground, "Date": the_date})
  save_result_to_file(matches,rf"result-restri-{num}.xlsx")
  
  pass

def remove_invalids(results):
  valid_results = []
  bValid = True
  # is ground on the date played by two teams?
  for the_result in results:
    for a_result in results:
      if the_result == a_result:
        continue
      if the_result["Ground"] == a_result["Ground"]:
        if the_result["Date"] == a_result["Date"]:
          bValid = False
          break
    if bValid:
      valid_results.append(the_result)

  print (len(valid_results))    
  import time
  time.sleep(60)

  # no two teams playing on same date
  # for the_result in results:
  #   for a_result in results:
  #     if the_result == a_result:
  #       continue
  #     if the_result["Home"] == a_result["Home"] and the_result["Away"] == a_result["Away"]:
  #       assert False

def test_results(rows, results):
  # all teams in a division is playing against each other
  # for division in get_all_divisions(rows):
  #   for team_name in get_all_teams(rows, division):
  #     for a_match in results:
  #       home_team = match[1]
  #       away_team = match[2]
  #       for the_match in results:
  #         if a_match == the_match:
  #           continue
  #         if home_team == the_match[1]:
  #   pass

  #   for team in get_all_teams(rows, division):
  #     # find all matches for the team
  #     team_row = team_name(row)
  #     matches = []
  #     for match in results:
  #       home_team = match[1]
  #       away_team = match[2]
  #       if team_name in [home_team, away_team]:
  #         pass

  
  # a team has equal number of home m

  # no two teams are playing on the same ground

  # no two teams playing on same date
  for result in results:
    ground, fixture_home, fixture_opposition, fixture_date = result[0], result[1], result[2], result[3]
    for a_result in results:
      if result == a_result:
        continue
      if fixture_date == a_result[3]:
        assert fixture_home not in [a_result[1], a_result[2]]
        assert fixture_opposition not in [a_result[1], a_result[2]]


  # check No Home/No Play condition
  for result in results:
    ground, home, opposition, the_date = result[0], result[1], result[2], result[3]
    home_team_row = get_row_for_team(rows, home)
    away_team_row = get_row_for_team(rows, home)
    assert home_team_row[the_date] not in ["No Home", "No Play"]
    assert away_team_row[the_date] not in ["No Play"]

  # check Home condition
  for row in rows:
    for the_date in get_all_dates(rows):
      if row[the_date] == "Home":
        home_team_row = get_row_for_team(rows, home)
        # team_name(home_team_row)
        ground = home_team_row["Ground"]
        pass
        # results[g,h,o,d]


def get_valid_states(rows):
  must_states = get_must_have_states(rows)
  states = []
  for row in rows:
    ground = row["Ground"]
    division = row["Division"]
    home_team = team_name(row)
    for the_date in get_all_dates(rows):
      if row[the_date] in ["No Home", "No Play"]:
        continue
      for opposition in get_all_teams(rows, division):
        is_valid = True
        oppositions_row = get_row_for_team(rows,opposition)
        if oppositions_row[the_date] in ["No Play"]:
          continue
        if opposition == home_team:
           continue
        # if this home vs opposition combo in any of the must_states
        # take only state which matches the date
        for must_state in must_states:
          if must_state[0][1] == home_team and must_state[0][2] == opposition:
            if must_state[0][3] != the_date:
              is_valid = False
              break
        if is_valid:
          states.append([ground, home_team, opposition, the_date])
  return states

def must_home_matches(rows):
  states = []
  # must  - Home 
  for row in rows:
    ground = row["Ground"]
    home_team = team_name(row)
    division = row["Division"]
    states_for_oppositions = []
    for the_date in get_all_dates(rows):
      if row[the_date] not in ["Home"]:
        continue
      for opposition in get_all_teams(rows, division):
        if opposition == home_team:
            continue
        states_for_oppositions.append([ground, home_team, opposition, the_date])
    if states_for_oppositions != []:
      states.append(states_for_oppositions)
  return states

def get_must_have_states(rows):
  states = []
  # # match - pre-allocates
  # matches = read_data("result-partial.xlsx")
  # for match in matches:
  #   states.append([[match["Ground"], match["Home"], match["Away"], match["Date"]]])
  return states
   
def main():
    all_rows = read_data("fix-3.xlsx")
    # all_matches = read_data("result-partial-3.xlsx")
    # print (len(all_matches))
    # all_matches = remove_invalids(all_matches)
    division = get_all_divisions(all_rows)
    rows= []
    for row in all_rows:
      # if row["Division"] in ["CCA Senior League Division 1"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Senior League Division 2"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Senior League Division 3"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 1 South"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 1 North"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 2 South"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 2 North"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 3 South"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 3 North"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 3 West"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 4 South"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 4 North"]:
      #   division = row["Division"]
      #   pass
      # elif row["Division"] in ["CCA Junior League 4 West"]:
      #   division = row["Division"]
      #   pass
      if row["Division"] in ["CCA Junior League 5 South"]:
        division = row["Division"]
        pass
      elif row["Division"] in ["CCA Junior League 5 North"]:
        division = row["Division"]
        pass
      else:
        continue
      rows.append(row)
    # Data.
    num_teams = len(get_all_teams(rows))
    # num_grounds = len(get_all_grounds(rows))
    num_days = len(get_all_dates(rows))
    all_teams = get_all_teams(rows)
    all_days = get_all_dates(rows)
    all_grounds = get_all_grounds(rows)
    
    print ("Start making states")
    valid_states = get_valid_states(rows)
    print (f"Valid states: {len(valid_states)}")
    # must_have_states = get_must_have_states(rows)
  
    
    # Creates the model.
    model = cp_model.CpModel()

    matches = {}
    print ("Start making variables")

    for state in valid_states:
      g,h,o,d = state[0],state[1],state[2],state[3]
      matches[g,h,o,d] = model.NewBoolVar(f'match_g{g}_h{h}_o{o}d_{d}')

    # respect must have; typically Home condition or matches already allocated
    for states in must_home_matches(rows):
      constraints=[]
      for a_state in states:
        if a_state not in valid_states:
          # print (a_state)
          continue
          # assert False

        g,h,o,d = a_state[0],a_state[1],a_state[2],a_state[3]
        # print (f"{g}_{h}_{o}_{d}")
        constraints.append(matches[g,h,o,d])
      model.AddExactlyOne(constraints)

    
    print ("setting constraints home-opposition constraint")
    # all teams play exactly one match against all oppositions
    # regardless of ground or days
    constraints = {}
    for state in valid_states:
      g,h,o,d = state[0],state[1],state[2],state[3]
      try:
        constraints[f"{h}_{o}"].append(matches[g,h,o,d])
      except KeyError:
        constraints[f"{h}_{o}"] = []
        constraints[f"{h}_{o}"].append(matches[g,h,o,d])
    for constraint in constraints.values():
      model.AddExactlyOne(constraint)

    # team plays atmost one match in a day
    # regardless of ground or opposition 
    print ("setting constraints home-opposition constraint")
    constraints = {}
    for state in valid_states:
      g,h,o,d = state[0],state[1],state[2],state[3]
      try:
        constraints[f"{h}_{d}"].append(matches[g,h,o,d])
      except KeyError:
        constraints[f"{h}_{d}"] = []
        constraints[f"{h}_{d}"].append(matches[g,h,o,d])

      try:
        constraints[f"{o}_{d}"].append(matches[g,h,o,d])
      except KeyError:
        constraints[f"{o}_{d}"] = []
        constraints[f"{o}_{d}"].append(matches[g,h,o,d])

    for constraint in constraints.values():
      model.AddAtMostOne(constraint)
  
    # at most one match on a ground on a day
    # regardless of team or opposition
    print ("setting ground constraint")
    constraints = {}
    for state in valid_states:
      g,h,o,d = state[0],state[1],state[2],state[3]
      try:
        constraints[f"{g}_{d}"].append(matches[g,h,o,d])
      except KeyError:
        constraints[f"{g}_{d}"] = []
        constraints[f"{g}_{d}"].append(matches[g,h,o,d])
    for constraint in constraints.values():
      model.AddAtMostOne(constraint)       

    print ("solve")
    # Creates the model.
    solver = cp_model.CpSolver()
    # solver.parameters.log_search_progress = True
    solver.parameters.num_search_workers = 8
    solver.parameters.linearization_level = 0

    # Display the first five solutions.
    solution_limit = 1000
    solution_printer = SolutionPrinter(rows, division, valid_states, matches, all_grounds, all_teams, all_days, solution_limit)

    # Enumerate all solutions.
    # solver.parameters.enumerate_all_solutions = True
    print ("Start solving")
    solver.Solve(model, solution_printer)

    # Statistics.y 
    print('\nStatistics')
    print('  - conflicts      : %i' % solver.NumConflicts())
    print('  - branches       : %i' % solver.NumBranches())
    print('  - wall time      : %f s' % solver.WallTime())
    print('  - solutions found: %i' % solution_printer.solution_count())

if __name__ == '__main__':
    main()
