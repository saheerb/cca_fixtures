from ortools.sat.python import cp_model
import logging
import sys
import math

result_count = 0
def match_date(n):  
    return n[-1]    

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
  """Print intermediate solutions."""

  def __init__(self, matches):
      cp_model.CpSolverSolutionCallback.__init__(self)
      self._matches = matches

  def on_solution_callback(self):
      global result_count
      result_count += 1
      result = []
      match_count = 0
      for match in self._matches:
        h,o,d = match[0],match[1],match[2]
        if self.Value(self._matches[(h,o,d)]):
          match_count += 1
          result.append(match)
      logging.info('Match Count: %i' % match_count)
      logging.info('Result Count: %i' % result_count)
      for match in sorted(result, key=match_date):
        print (f"{match[2]}: {match[0]} X {match[1]}")
      # self.StopSearch()

def teams_on_a_day_constraint(model, matches):
  # team plays atmost one match in a day
  # regardless of ground or opposition 
  constraints = {}
  for match in matches:
    h,o,d = match[0],match[1],match[2]
    try:
      constraints[f"{h}_{d}"].append(matches[h,o,d])
    except KeyError:
      constraints[f"{h}_{d}"] = []
      constraints[f"{h}_{d}"].append(matches[h,o,d])

    try:
      constraints[f"{o}_{d}"].append(matches[h,o,d])
    except KeyError:
      constraints[f"{o}_{d}"] = []
      constraints[f"{o}_{d}"].append(matches[h,o,d])

  for constraint in constraints.values():
    model.AddAtMostOne(constraint)

def home_opposition_constraint(model, matches):
    logging.debug ("setting constraints home-opposition constraint")
    # all teams play exactly one match against all oppositions
    # regardless of ground or days
    constraints = {}
    for match in matches:
      h,o,d = match[0],match[1],match[2]
      try:
        constraints[f"{h}_{o}"].append(matches[h,o,d])
      except KeyError:
        constraints[f"{h}_{o}"] = []
        constraints[f"{h}_{o}"].append(matches[h,o,d])
    for constraint in constraints.values():
      model.AddExactlyOne(constraint)

def forbid_consecutive_home_aways(model, teams, dates, matches):
  # team plays atmost one match in a day
  # regardless of ground or opposition 
  home_constraints = {}
  away_constraints = {}
  for match in matches:
    h,o,d = match[0],match[1],match[2]
    try:
      home_constraints[f"{h}_{d}"].append(matches[h,o,d])
    except KeyError:
      home_constraints[f"{h}_{d}"] = []
      home_constraints[f"{h}_{d}"].append(matches[h,o,d])

    try:
      away_constraints[f"{o}_{d}"].append(matches[h,o,d])
    except KeyError:
      away_constraints[f"{o}_{d}"] = []
      away_constraints[f"{o}_{d}"].append(matches[h,o,d])
  
  consecutives = 2
  for constraints in [home_constraints, away_constraints]:
  # for constraints in [home_constraints]:
    for a_team in teams:
      for date_index in range(len(dates)- consecutives):
        team_contraints = []
        for i in range(consecutives+1):
          team_contraints += constraints[f"{a_team}_{dates[date_index + i]}"]
        the_contraints = []
        for contraint in team_contraints:
          the_contraints.append(contraint)
        
        model.AddBoolOr(the_contraints)

        negated = []
        for contraint in team_contraints:
          negated.append(contraint.Not())
        model.AddBoolOr(negated)

def forbid_consecutive_opponents(model, teams, dates, matches):
  # team plays atmost one match in a day
  # regardless of ground or opposition 
  constraints = {}
  for match in matches:
    h,o,d = match[0],match[1],match[2]
    try:
      constraints[f"{h}_{o}_{d}"].append(matches[h,o,d])
    except KeyError:
      constraints[f"{h}_{o}_{d}"] = []
      constraints[f"{h}_{o}_{d}"].append(matches[h,o,d])
  
  consecutives = 1 #TODO change only this value
  for home_team in teams:
    for away_team in teams:
      if home_team == away_team:
        continue
      for date_index in range(len(dates)- consecutives):
        team_contraints = []
        for i in range(consecutives+1):
          team_contraints += constraints[f"{home_team}_{away_team}_{dates[date_index + i]}"]
          team_contraints += constraints[f"{away_team}_{home_team}_{dates[date_index + i]}"]
        the_contraints = []
        for contraint in team_contraints:
          the_contraints.append(contraint)
        
        model.AddAtMostOne(the_contraints)


if __name__ == '__main__':
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  nb_teams = 4
  home_teams = [f"Team_{x+1}" for x in range(nb_teams)]
  oppo_teams = [f"Team_{x+1}" for x in range(nb_teams)]
  # for 3 and teams, date neeed is 6
  nb_dates_needed = (math.ceil(nb_teams/2)*2*2) -2
  dates = [f"Date_{x+1}" for x in range(nb_dates_needed)]

  # Creates the model.
  model = cp_model.CpModel()
  
  # create variables
  matches = {}

  for h in home_teams:
    for o in oppo_teams:
      for d in dates:
        if h == o:
          continue
        matches[h,o,d] = model.NewBoolVar(f'match_h{h}_o{o}d_{d}')  

  # constraints
  home_opposition_constraint(model, matches)
  teams_on_a_day_constraint(model, matches)
  forbid_consecutive_home_aways(model, home_teams, dates, matches)
  forbid_consecutive_opponents(model, home_teams, dates, matches)
  # minimize consecutive home matches
  # maximize weeks between same opponents

  logging.debug ("solve")
  # Creates the model.
  solver = cp_model.CpSolver()
  solver.parameters.enumerate_all_solutions = True
  solution_printer = SolutionPrinter(matches)
  status = solver.Solve(model, solution_printer)
