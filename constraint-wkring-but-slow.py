from ortools.sat.python import cp_model
from utils import *

def write_excel(results, rows, num):
  matches = []
  for result in results:
    ground = result[0]
    home_team = result[1]
    away_team = result[2]
    the_date  = result[3]
    division = get_division(rows, home_team)
    matches.append({"Division":division, "Home":home_team, "Away":away_team, "Ground":ground, "Date": the_date})
  save_result_to_file(matches,rf"result-div{num}.xlsx")
  
  pass
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
    assert home_team_row[the_date] != "No Play"
    assert away_team_row[the_date] != "No Play"
    assert home_team_row[the_date] != "No Home"

  # check Home condition
  for row in rows:
    for the_date in get_all_dates(rows):
      if row[the_date] == "Home":
        home_team_row = get_row_for_team(rows, home)
        # team_name(home_team_row)
        ground = home_team_row["Ground"]
        pass
        # results[g,h,o,d]

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
  """Print intermediate solutions."""

  def __init__(self, rows, valid_states, matches, grounds, teams, dates, limit):
      cp_model.CpSolverSolutionCallback.__init__(self)
      self._rows = rows
      self._valid_states = valid_states
      self._matches = matches
      self._teams = teams
      self._dates = dates
      self._grounds =grounds
      self._solution_count = 0
      self._solution_limit = limit

  def on_solution_callback(self):
      print (self.Value)
      self._solution_count += 1
      match_count = 0
      result = []
      for g in self._grounds:
        for h in self._teams:
          for o in self._teams:
            for d in self._dates:
              if [g,h,o,d] not in self._valid_states:
                continue
              if self.Value(self._matches[(g,h,o,d)]):
                match_count +=1
                result.append([g,h,o,d])
                # print(f'Team-{h} playing against Team-{o} on {d} at {g}')

      print('Match Count: %i' % match_count)
      write_excel(result, self._rows, self._solution_count)
      test_results(self._rows, result)
      if self._solution_count >= self._solution_limit:
          print('Stop search after %i solutions' % self._solution_limit)
          self.StopSearch()

  def solution_count(self):
      return self._solution_count

def get_valid_states(rows):
  states = []
  for row in rows:
    ground = row["Ground"]
    home_team = team_name(row)
    for the_date in get_all_dates(rows):
      if row[the_date] in ["No Home", "No Play"]:
        continue
      for opposition in get_all_teams(rows):
        oppositions_row = get_row_for_team(rows,opposition)
        if oppositions_row[the_date] == "No Play":
          continue
        if opposition == home_team:
           continue
        states.append([ground, home_team, opposition, the_date])
  return states

def get_must_have_states(rows):
  states = []
  for row in rows:
    ground = row["Ground"]
    home_team = team_name(row)
    states_for_oppositions = []
    for the_date in get_all_dates(rows):
      if row[the_date] not in ["Home"]:
        continue
      for opposition in get_all_teams(rows):
        if opposition == home_team:
           continue
        states_for_oppositions.append([ground, home_team, opposition, the_date])
    if states_for_oppositions != []:
     states.append(states_for_oppositions)
  return states
   
def main():
    rows = read_data("fix-1.xlsx")
    
    # Data.
    num_teams = len(get_all_teams(rows))
    num_grounds = len(get_all_grounds(rows))
    num_days = len(get_all_dates(rows))
    all_teams = get_all_teams(rows)
    all_days = get_all_dates(rows)
    all_grounds = get_all_grounds(rows)
    print (num_teams*num_teams*num_grounds*num_days)
    print ("Start making states")
    valid_states = get_valid_states(rows)
    must_have_states = get_must_have_states(rows)
  
    
    # Creates the model.
    model = cp_model.CpModel()

    matches = {}
    print ("Start making variables")
    # create match variable
    count =0
    for g in all_grounds:
      for h in all_teams:
        for o in all_teams:
          for d in all_days:
            count +=1
            if count % 1000 == 0:
              print (f"Processing {count} of {len(valid_states)}")
            if [g,h,o,d] not in valid_states:
               continue
            matches[g,h,o,d] = model.NewBoolVar(f'match_g{g}_h{h}_o{o}d_{d}')

    # for state in valid_states:
    # for all h and o
    # add to constraints[h_0].append(state)
    # for constraint in constraints:
    # model.AddExactlyOne(constraint)
    
    print ("Start setting constraints")
    # all teams play exactly one match against all oppositions
    # regardless of ground or days
    for h in all_teams:
      for o in all_teams:
        if h == o:
          continue
        model.AddExactlyOne(matches[g,h,o,d] for d in all_days for g in all_grounds if [g,h,o,d] in valid_states)

    # for state in valid_states:
    # for all h and d are different
    # add to constraints[h_d].append(state)
    # for constraint in constraints:
    # model.AddAtMostOne(constraint)
    # how to add the last one?
        
    # team plays only one match in a day
    # regardless of ground or opposition 
    for h in all_teams:
      for d in all_days:
        model.AddAtMostOne(matches[g,h,o,d] for o in all_teams for g in all_grounds if [g,h,o,d] in valid_states)
        model.AddAtMostOne(matches[g,o,h,d] for o in all_teams for g in all_grounds if [g,o,h,d] in valid_states)
        states = []
        for g in all_grounds:
          for o in all_teams:
            if o!=h:
              if [g,o,h,d] in valid_states:
                states.append(matches[g,o,h,d])
              if [g,h,o,d] in valid_states:
                states.append(matches[g,h,o,d])
        model.AddAtMostOne(states)

  
    # at most one match on a ground on a day
    # regardless of team or opposition
    for g in all_grounds:
       for d in all_days:
          model.AddAtMostOne(matches[g,h,o,d] for h in all_teams for o in all_teams if [g,h,o,d] in valid_states)        
  
    # respect must have states
    # for state in must_have_states:
    #   model.AddAtLeastOne(state)        

    # Creates the model.
    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = True
    solver.parameters.num_search_workers = 8
    solver.parameters.linearization_level = 0

    # Display the first five solutions.
    solution_limit = 1000
    solution_printer = SolutionPrinter(rows, valid_states, matches, all_grounds, all_teams, all_days, solution_limit)

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
