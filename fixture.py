from ortools.sat.python import cp_model
from utils import *
import shutil
from test import test_results_indexes
import logging

def write_excel(results, result_file, rows, num):
  matches = []
  for result in results:
    ground = result[0]
    home_team = result[1]
    away_team = result[2]
    the_date  = result[3]
    division = get_division(rows, home_team)
    matches.append({"Division":division, "Home":home_team, "Away":away_team, "Ground":ground, "Date": the_date})
  save_result_to_file(matches,result_file)
  
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

  logging.debug (len(valid_results))    
  import time
  time.sleep(60)

  # no two teams playing on same date
  # for the_result in results:
  #   for a_result in results:
  #     if the_result == a_result:
  #       continue
  #     if the_result["Home"] == a_result["Home"] and the_result["Away"] == a_result["Away"]:
  #       assert False

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
  """Print intermediate solutions."""

  def __init__(self, rows, result_file, valid_states, matches, grounds, teams, dates, limit):
      cp_model.CpSolverSolutionCallback.__init__(self)
      self._result_file = result_file
      self._rows = rows
      self._valid_states = valid_states
      self._matches = matches
      self._teams = teams
      self._dates = dates
      self._grounds =grounds
      self._solution_count = 0
      self._solution_limit = limit

  def on_solution_callback(self):
      self._solution_count += 1
      # print ("Solution found")
      # return
      
      match_count = 0
      result = []
      for state in self._valid_states:
        g=state[0]
        h=state[1]
        o=state[2]
        d=state[3]
        if self.Value(self._matches[(g,h,o,d)]):
          match_count +=1
          result.append([g,h,o,d])
                # print(f'Team-{h} playing against Team-{o} on {d} at {g}')

      logging.debug('Match Count: %i' % match_count)
      write_excel(result, self._result_file, self._rows, self._solution_count)
      test_results_indexes(self._rows, result)
      if self._solution_count >= self._solution_limit:
          logging.debug('Stop search after %i solutions' % self._solution_limit)
          self.StopSearch()

  def solution_count(self):
      return self._solution_count

# def get_valid_states(rows):
#   states = []
#   for row in rows:
#     ground = row["Ground"]
#     division = row["Division"]
#     home_team = team_name(row)
#     for the_date in get_all_dates(rows):
#       if row[the_date] in ["No Home", "No Play", "Off Request"]:
#         continue
#       for opposition in get_all_teams(rows, division):
#         is_valid = True
#         oppositions_row = get_row_for_team(rows,opposition)
#         if oppositions_row[the_date] in ["No Play", "Off Request"]:
#           continue
#         if opposition == home_team:
#            continue
#         states.append([ground, home_team, opposition, the_date])
#   return states

def get_valid_states(rows, partial_results):
  must_states = get_must_have_states(rows, partial_results)
  states = []
  for row in rows:
    ground = row["Ground"]
    division = row["Division"]
    home_team = team_name(row)
    for the_date in get_all_dates(rows):
      if row[the_date] in ["No Home", "No Play", "Off Request"]:
        continue
      for opposition in get_all_teams(rows, division):
        is_valid = True
        oppositions_row = get_row_for_team(rows,opposition)
        if oppositions_row[the_date] in ["No Play", "Off Request"]:
          continue
        if opposition == home_team:
          continue
        # if this home vs opposition combo in any of the must_states
        # take only state which matches the date
        for must_state in must_states:
          if must_state[1] == home_team:
            if must_state[2] == opposition and must_state[3] == the_date:
              is_valid = True
              break
            else:
              is_valid = False
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

def get_must_have_states(rows, partial_results):
  states = []
  for match in partial_results:
    states.append([match["Ground"], match["Home"], match["Away"], match["Date"]])
  return states

def must_constraint(model, rows, matches, partial_results):
  must_states = get_must_have_states(rows, partial_results)
  for state in must_states:
    g,h,o,d = state[0],state[1],state[2],state[3]
    model.AddExactlyOne(matches[g,h,o,d])

def make_variables(model, valid_states):
  matches = {}
  for state in valid_states:
    g,h,o,d = state[0],state[1],state[2],state[3]
    matches[g,h,o,d] = model.NewBoolVar(f'match_g{g}_h{h}_o{o}d_{d}')
  return matches

def set_consecutive_date_constraint(model, rows, valid_states, matches):
  all_dates = get_all_dates(rows)
  for division in get_all_divisions(rows):
    for team in get_all_teams(rows, division):
      team_row = get_row_for_team(rows, team)
      states={}
      for state in valid_states:
        g,h,o,d = state[0],state[1],state[2],state[3]
        if team != h:
          continue
        # get maximum consecutive for this team
        # add 1 because we are building windows that are not allowed
        for a_window in window(all_dates, team_row["Max Consecutive"]+1):
          if d in a_window:
            window_id = get_text(a_window)
            try:
              states[window_id].append(matches[g,h,o,d])
            except:
              states[window_id] = []
              states[window_id].append(matches[g,h,o,d])

      for state in states.values():
        model.Add(sum(state) <= team_row["Max Consecutive"])

def number_of_matches_constraint(model, rows, valid_states, matches):
  for division in get_all_divisions(rows):
    num_home_matches = len(get_all_teams(rows, division)) - 1
    num_all_matches = num_home_matches * 2
    num_away_matches = num_home_matches
    for team in get_all_teams(rows, division):
      home_team_states = []
      away_team_states = []
      home_way_team_states = []
      for a_state in valid_states:
        g,h,o,d = a_state[0],a_state[1],a_state[2],a_state[3]
        if team == h:
          home_team_states.append(matches[g,h,o,d])
          home_way_team_states.append(matches[g,h,o,d])
        if team == o:
          away_team_states.append(matches[g,h,o,d])
          home_way_team_states.append(matches[g,h,o,d])
      model.Add(sum(home_team_states) == num_home_matches)
      model.Add(sum(away_team_states) == num_away_matches)
      model.Add(sum(home_way_team_states) == num_all_matches)

def must_home_match_constraint(model, rows, valid_states, matches):
  # Home condition
  for states in must_home_matches(rows):
    constraints=[]
    for a_state in states:
      if a_state not in valid_states:
        # print (a_state)
        # While partial results are processed, 
        # invalid "Home" match entries are also removed
        # That's why we are here
        continue
        # assert False

      g,h,o,d = a_state[0],a_state[1],a_state[2],a_state[3]
      # print (f"{g}_{h}_{o}_{d}")
      constraints.append(matches[g,h,o,d])
    model.AddExactlyOne(constraints)

def teams_on_a_day_constraint(model, rows, valid_states, matches):
  # team plays atmost one match in a day
  # regardless of ground or opposition 
  logging.debug ("setting constraints home-opposition constraint")
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

def ground_constraint(model, rows, valid_states, matches):
  logging.debug ("setting ground constraint")
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

def add_consecutive_matches(rows, result_file):
  results = read_data(result_file)
  dates = get_all_dates(rows)
  
  for team in get_all_teams(rows):
    # matches are ordered by date
    matches = get_all_matches(team, results, type="Home")
    max_consecutive = 0
    prev_match = None
    consecutive = 1
    for match in matches:
      if prev_match == None:
        consecutive = 1
      else:
        match_date = datetime.strptime(match["Date"], "%Y/%m/%d")
        prev_match_date = datetime.strptime(prev_match["Date"], "%Y/%m/%d")
        difference = abs((match_date - prev_match_date).days)
        if difference <= 7:
          consecutive += 1
        else:
          consecutive = 1
      if consecutive > max_consecutive:
        max_consecutive = consecutive
      prev_match = match
    team_row = get_row_for_team(rows, team)
    team_row["max_consecutive"] = max_consecutive
  save_result_to_file(rows, "results/result_with_consecutive.xlsx")
      





def main():
  data_file = "data.xlsx"
  all_rows = read_data(data_file)

  
  attempt = 1
  while True:
    processed_divisions = []
    # create an empty partial file
    partial_file = "results/result-partial.xlsx"
    save_result_to_file({},partial_file)
    solution_found = False
    print (f"Attempt: {attempt}")
    for division in get_all_divisions(all_rows):
      print (f"Solving: {division}")
      partial_results = read_data(partial_file)
      if division not in processed_divisions:
        processed_divisions.append(division)
      rows = []
      for row in all_rows:
        if row["Division"] in processed_divisions:
          result_file = f"tmp/{division}.xlsx"
          rows.append(row)

      if process(rows, result_file, partial_results) == 0:
        print(f"No solution for {division}")
        # start from beginning
        attempt += 1
        solution_found = False
        break
      else:
        solution_found = True
        shutil.copyfile(result_file, partial_file)
        # copy result_file to partial_file
    if solution_found == True:
      break
    elif attempt > 100:
      print(f"No solution found in {attempt} attempts")
      sys.exit()

  shutil.copyfile(partial_file, "results/result.xlsx")
  results = read_data("results/result.xlsx")
  add_consecutive_matches(rows, results)

def home_opposition_constraint(model, valid_states, matches):
    logging.debug ("setting constraints home-opposition constraint")
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

def process(rows, result_file, partial_results=[]):
    all_teams = get_all_teams(rows)
    all_days = get_all_dates(rows)
    all_grounds = get_all_grounds(rows)
    
    logging.debug ("Start making states")
    # # match - pre-allocates
    # matches = read_data("results/result-partial.xlsx")

    valid_states = get_valid_states(rows, partial_results)
    logging.debug (f"Valid states: {len(valid_states)}")
    
    # Creates the model.
    model = cp_model.CpModel()

    logging.debug ("Start making variables")
    matches = make_variables(model, valid_states)

    logging.debug ("Set Home vs Opposition - Play exactly once") 
    home_opposition_constraint(model, valid_states, matches)

    logging.debug ("Set Consecutive dates constraint")    
    set_consecutive_date_constraint(model, rows, valid_states, matches)

    # Number of matches - same as Home vs Opposition - so no need
    # print ("Set Number of Matches Constraint")  
    # number_of_matches_constraint(model, rows, valid_states, matches)

    logging.debug ("Set Must constraint")  
    must_constraint(model, rows, matches, partial_results)   

    logging.debug ("Set Home Match constraint")  
    must_home_match_constraint(model, rows, valid_states, matches)

    logging.debug ("Set Home Opposition constraint")  
    teams_on_a_day_constraint(model, rows, valid_states, matches)

    logging.debug ("Set Ground constraint")  
    ground_constraint(model, rows, valid_states, matches)   

    logging.debug ("solve")
    # Creates the model.
    solver = cp_model.CpSolver()
    # solver.parameters.log_search_progress = True
    solver.parameters.num_workers = 8
    solver.parameters.linearization_level = 0
    solver.preferred_variable_order = 3
    solver.randomize_search = True
    solver.subsolvers=0
    solver.parameters.stop_after_first_solution=True
    # Display the first five solutions.
    solution_limit = 1
    solution_printer = SolutionPrinter(rows, result_file, valid_states, matches, all_grounds, all_teams, all_days, solution_limit)

    # Enumerate all solutions.
    # solver.parameters.enumerate_all_solutions = True
    # print (f"Start solving {result_file}")
    solver.Solve(model, solution_printer)

    # Statistics.y 
    logging.debug('\nStatistics')
    logging.debug('  - conflicts      : %i' % solver.NumConflicts())
    logging.debug('  - branches       : %i' % solver.NumBranches())
    logging.debug('  - wall time      : %f s' % solver.WallTime())
    logging.debug('  - solutions found: %i' % solution_printer.solution_count())

    return solution_printer.solution_count()

if __name__ == '__main__':
    main()
