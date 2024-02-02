from ortools.sat.python import cp_model
from utils import *
from excel import *
import shutil
from test import test_results_indexes
from test import test_results
import logging
import os

global_solution_cnt = 0

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
  """Print intermediate solutions."""

  def __init__(self, rows, result_file, matches, grounds, teams, dates, limit):
      cp_model.CpSolverSolutionCallback.__init__(self)
      self._result_file = result_file
      self._rows = rows
      # self._valid_states = valid_states
      self._matches = matches
      self._teams = teams
      self._dates = dates
      self._grounds =grounds
      self._solution_count = 0
      self._solution_limit = limit

  def on_solution_callback(self):
    global global_solution_cnt
    global_solution_cnt += 1
    match_count = 0
    results = []
    print (f"Solution found : {global_solution_cnt}")
    rows = self._rows
    for division in get_all_divisions(rows):
      for h in get_all_teams(rows, division):
        for o in get_all_teams(rows, division):
          for g in get_grounds(rows, h):
            for d in get_all_dates(rows):
              if self.Value(self._matches[(g,h,o,d)]):
                match_count +=1
                results.append([g,h,o,d])

    logging.info('Match Count: %i' % match_count)
    logging.info(self._result_file)
    write_results(results, self._result_file, self._rows, global_solution_cnt)
    # results_meta=get_results_meta(results, self._rows)
    test_results_indexes(self._rows, results)
    if self._solution_limit and self._solution_count >= self._solution_limit:
        logging.info('Stop search after %i solutions' % self._solution_limit)
        self.StopSearch()

  def solution_count(self):
      return global_solution_cnt

def must_home_matches(rows):
  states = []
  # must  - Home 
  for row in rows:
    ground = row["Ground"]
    home_team = team_name(row)
    division = row["Division"]
    for the_date in get_all_dates(rows):
      states_for_oppositions = []
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
    if match in rows:
      states.append([match["Ground"], match["Home"], match["Away"], match["Date"]])
  return states

def must_constraint(model, rows, matches, partial_results):
  must_states = get_must_have_states(rows, partial_results)
  for state in must_states:
    g,h,o,d = state[0],state[1],state[2],state[3]
    model.AddExactlyOne(matches[g,h,o,d])

def make_variables(model, rows):
  matches = {}
  for division in get_all_divisions(rows):
    for h in get_all_teams(rows, division):
      for o in get_all_teams(rows, division):
        for g in get_grounds(rows, h):
          for d in get_all_dates(rows):
            matches[g,h,o,d] = model.NewBoolVar(f'match_g{g}_h{h}_o{o}d_{d}')
  return matches

def home_opposition_match_date_gap(model, rows, matches):
  consecutives = 10
  team_states = {}
  for division in get_all_divisions(rows):
    for h in get_all_teams(rows, division):
      for o in get_all_teams(rows, division):
        for g in get_grounds(rows, h):
          for d in get_all_dates(rows):
            try:
              team_states[f"{h}_{o}_{d}"].append(matches[g,h,o,d])
            except KeyError:
              team_states[f"{h}_{o}_{d}"] = []
              team_states[f"{h}_{o}_{d}"].append(matches[g,h,o,d])

  for home_team in get_all_teams(rows, division):
    for away_team in get_all_teams(rows, division):
      for date_index in range(len(all_dates)- consecutives):
          matches_in_consecutive_window = []
          for i in range(consecutives+1):
            try:
              matches_in_consecutive_window += team_states[f"{home_team}_{away_team}_{all_dates[date_index + i]}"]
            except KeyError:
                pass
            try:
              matches_in_consecutive_window += team_states[f"{away_team}_{home_team}_{all_dates[date_index + i]}"]
            except KeyError:
              pass
          home_oppostions = []
          for a_home_oppostion_match in matches_in_consecutive_window:
            home_oppostions.append(a_home_oppostion_match)
          model.AddExactlyOne(home_oppostions)
          # model.AddAtMostOne(home_oppostions)
          # model.Minimize(sum(home_oppostions))

def consecutive_home_or_aways(model, rows, matches):
  home_states = {}
  away_states = {}
  default_consecutives = 5
  for division in get_all_divisions(rows):
    for h in get_all_teams(rows, division):
      for o in get_all_teams(rows, division):
        for g in get_grounds(rows, h):
          for d in get_all_dates(rows):
            try:
              home_states[f"{h}_{d}"].append(matches[g,h,o,d])
            except KeyError:
              home_states[f"{h}_{d}"] = []
              home_states[f"{h}_{d}"].append(matches[g,h,o,d])
            
            try:
              away_states[f"{o}_{d}"].append(matches[g,h,o,d])
            except KeyError:
              away_states[f"{o}_{d}"] = []
              away_states[f"{o}_{d}"].append(matches[g,h,o,d])

  all_dates = get_all_dates(rows)
  for the_matches in [home_states, away_states]:
    for division in get_all_divisions(rows):
      for team in get_all_teams(rows, division):
        try:
          consecutives = int(get_row_for_team(rows, team)["Max Consecutive"])
        except:
          consecutives = default_consecutives

        for date_index in range(len(all_dates) - consecutives):
          matches_in_consecutive_window = []
          for i in range(consecutives+1):
            try:
              for a_match in the_matches[f"{team}_{all_dates[date_index + i]}"]:
                matches_in_consecutive_window.append(a_match)
            except KeyError:
              pass

          # model.Minimize(sum(matches_in_consecutive_window))
          model.AddBoolOr(matches_in_consecutive_window)

          negated_match = []
          for a_negated_match in matches_in_consecutive_window:
            negated_match.append(a_negated_match.Not())
          model.AddBoolOr(negated_match)

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

def must_home_match_constraint(model, rows, matches):
  # Home condition
  for states in must_home_matches(rows):
    constraints=[]
    for a_state in states:
      g,h,o,d = a_state[0],a_state[1],a_state[2],a_state[3]
      constraints.append(matches[g,h,o,d])
    model.AddExactlyOne(constraints)

def teams_on_a_day_constraint(model, rows, matches):
  # team plays atmost one match in a day
  # regardless of ground or opposition 
  logging.debug ("setting constraints home-opposition constraint")
  constraints = {}
  for division in get_all_divisions(rows):
    for h in get_all_teams(rows, division):
      for o in get_all_teams(rows, division):
        for g in get_grounds(rows, h):
          for d in get_all_dates(rows):
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

def ground_constraint(model, rows, matches):
  logging.debug ("setting ground constraint")
  constraints = {}
  for division in get_all_divisions(rows):
    for h in get_all_teams(rows, division):
      for o in get_all_teams(rows, division):
        for g in get_grounds(rows, h):
          for d in get_all_dates(rows):
            try:
              constraints[f"{g}_{d}"].append(matches[g,h,o,d])
            except KeyError:
              constraints[f"{g}_{d}"] = []
              constraints[f"{g}_{d}"].append(matches[g,h,o,d])

  for constraint in constraints.values():
    model.AddAtMostOne(constraint)

def add_consecutive_matches(rows, results, out_file="results/data_with_consecutive.xlsx"):
  dates = get_all_dates(rows)
  
  for team in get_all_teams(rows):
    # matches are ordered by date
    matches = _get_all_matches(team, results, type="Home")
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
  write_excel(rows, out_file)
      
# def build_from_partial_result(data_rows, partial_results):
#   result_file = f"tmp/re1.xlsx"
#   # print (len(partial_results))
#   # print (len(partial_results))
#   # test_results(data_rows, partial_results)
#   # sys.exit()
#   if process(data_rows, result_file, partial_results) == 0:
#     print(f"No solution found")
#   results = read_excel("tmp/re1_1.xlsx")
#   add_consecutive_matches(data_rows, results, "tmp/re1-with-cons.xlsx")
#   play_cricket_upload_format("tmp/re1_1.xlsx", "tmp/play-cricket-upload.xlsx")
#   play_cricket_download_format("tmp/re1_1.xlsx", "tmp/play-cricket-download.xlsx")
#   # test_result  
#   pass

def main(partial_file=None, run_one_after_another=False):
  data_file = "2024/data.xlsx"
  result_file = "2024/result.xlsx"
  udated_data_file = "2024/data_cons.xlsx"
  solution_found = False

  partial_results = []
  if partial_file:
    partial_results = read_excel(partial_file, "Fixtures")

  all_rows = read_excel(data_file, "Grounds")

  if run_one_after_another:
    partial_tmp_file = "2024/tmp/result-partial.xlsx"
    processed_divisions = []
    if partial_file ==  None:
      write_excel({},partial_tmp_file)
    else:
      shutil.copy(partial_file, partial_tmp_file)
  
    for division in get_all_divisions(all_rows):
      solution_found = False
      # if division in ["CCA Senior League Division 1",
      #                 "CCA Senior League Division 2",
      #                 "CCA Senior League Division 3"]:
      #   continue
      print (f"Solving: {division}")
      partial_results = read_excel(partial_tmp_file)
      if division not in processed_divisions:
        processed_divisions.append(division)
      rows = []
      for row in all_rows:
        if row["Division"] in processed_divisions:
          result_file = f"2024/tmp/{division}.xlsx"
          rows.append(row)

      if process(rows, result_file, partial_results) == 0:
        print(f"No solution..")
        sys.exit()
      else:
        shutil.copyfile(result_file, partial_tmp_file)
      solution_found = True
  else:
    if process(all_rows, result_file, partial_results) == 0:
      print(f"No solution..")
    else:
      solution_found = True
  
  results = read_excel(result_file)
  if solution_found:
    add_result_meta(all_rows, results, result_file)

def add_result_meta(rows, results, result_file):
  def _get_short_name(division):

    m = re.search("[0-9]", division)
    if m != None: nb=m.group(0)
    m = re.search("Junior|Senior", division)
    if m != None: div=m.group(0)
    m = re.search("South|North|West", division)
    if m != None: zone=m.group(0)
    try:
      return f"{div}-{nb}-{zone}"
    except:
      return f"{div}-{nb}"
  
  def _get_all_matches(team_name, results, type="Home"):
    def conv_date(str):
      d = datetime.strptime(str, "%Y/%m/%d")
      return d
    matches = []
    for a_result in results:
      if type == "Home" and a_result["Home"] == team_name:
        matches.append(a_result)
      if type == "Away" and a_result["Away"] == team_name:
        matches.append(a_result)
    matches = sorted(matches, key=lambda d: conv_date(d["Date"]))
    return matches

  def _get_gap(home_team, away_team, matches):
    matched = []
    for match in matches:
      if (match["Home"] == home_team and match["Away"] == away_team) or\
          (match["Away"] == home_team and match["Home"] == away_team):
          matched.append(match)
    assert 2 == len(matched)
    match_date = datetime.strptime(matched[0]["Date"], "%Y/%m/%d")
    prev_match_date = datetime.strptime(matched[1]["Date"], "%Y/%m/%d")
    difference = abs((match_date - prev_match_date).days)
    return difference/7

  def _get_max_consecutive(team, results, type="Home"):
    # matches are ordered by date
    matches = _get_all_matches(team, results, type)
    max_consecutive = 0
    prev_match = None
    consecutive = 1
    for match in matches:
      if prev_match == None:
        consecutive = 1
      else:
        match_date = datetime.strptime(match["Date"], "%Y/%m/%d")
        prev_match_date = datetime.strptime(prev_match["Date"], "%Y/%m/%d")
        assert match_date > prev_match_date
        difference = (match_date - prev_match_date).days
        if difference == 7:
          consecutive += 1
        else:
          consecutive = 1
      if consecutive > max_consecutive:
        max_consecutive = consecutive
      prev_match = match
    return max_consecutive

  div_dict = {}
  for division in get_all_divisions(rows):
    result_metas = []
    for home_team in get_all_teams(rows, division):
      # row = get_row_for_team(rows, home_team)
      meta = {}
      meta["home_team"] = home_team
      meta["home_cons"]=_get_max_consecutive(home_team, results, "Home")
      meta["away_cons"]=_get_max_consecutive(home_team, results, "Away")
      for away_team in get_all_teams(rows, division):
        if home_team == away_team:
          meta[home_team] = "-"
          continue
        meta[away_team] = _get_gap(home_team, away_team, results)
      result_metas.append(meta)
    sorted_metas = []

    div = _get_short_name(division)
    # .replace(' ','_')
    for meta in result_metas:
      sorted_metas.append(dict(sorted(meta.items())))
    div_dict[div]=sorted_metas
  update_excel(result_file, sheets_dict=div_dict)

def play_cricket_download_format(in_file, out_file):
  results = read_excel(in_file)
  result_with_date = []
  keys = [
    "Date",	
    "Home Team",	"Away Team",
    "Division / Cup",	"Ground"
  ]
										 	
  for result in results:
    r = {}
    for key in keys:
      if key == "Home Team":
        r[key] = result["Home"]
      elif key == "Away Team":
        r[key] = result["Away"]
      elif key == "Division / Cup":
        r[key] = result["Division"]
      else:
        r[key] = result[key]
    result_with_date.append(r)
  write_excel(result_with_date, out_file)

def play_cricket_upload_format(in_file="results/result.xlsx", out_file="results/play-cricket.xlsx"):
  results = read_excel(in_file)
  result_with_date = []
  keys = [
            "Division ID",
            "Match Date", "Time",
            "Home Team ID",	"Away Team ID",
            "Ground ID",	"Ground Name",
            "Umpire 1 ID", "Umpire 2 ID",	"Umpire 3 ID",
            "Match Ref ID",	"External Match ID"
  ]
										 	
  for result in results:
    r = {}
    for key in keys:
      if key == "Match Date":
        yyyy, mm, dd = result["Date"].split("/")
        r[key] = "%s/%s/%s" % (dd, mm, yyyy)
      elif key == "Ground Name":
        if result["Ground ID"] != "":
          r[key] = ""
        else:
          r[key] = result["Ground"]
      elif key not in result.keys():
        r[key] = ""
      else:
        r[key] = result[key]
    result_with_date.append(r)
  write_excel(result_with_date, out_file)

def invlalid_constraints(models, rows, matches):
    logging.debug ("setting constraints home-opposition constraint")
    constraints = {}
    # all teams play exactly one match against all oppositions
    # regardless of ground or days    
    for division in get_all_divisions(rows):
      for h in get_all_teams(rows, division):
        home_row = get_row_for_team(rows, h)
        for o in get_all_teams(rows, division):
          away_row = get_row_for_team(rows, o)
          for g in get_grounds(rows, h):
            for d in get_all_dates(rows):
              if h == o:
                models.AddBoolOr(matches[g,h,o,d].Not())
              elif home_row[d] in ["No Play", "Off Request", "No Home"]:
                # if  home_row[d] in ["No Home"] and g == "Saffron Walden County High School" and h=="Saffron Walden CC - 4th XI":
                #   print (matches[g,h,o,d])
                models.AddBoolOr(matches[g,h,o,d].Not())
              elif away_row[d] in ["No Play", "Off Request"]:
                models.AddBoolOr(matches[g,h,o,d].Not())

def home_opposition_constraint(model, rows, matches):
    logging.debug ("setting constraints home-opposition constraint")
    constraints = {}
    # all teams play exactly one match against all oppositions
    # regardless of ground or days    
    for division in get_all_divisions(rows):
      for h in get_all_teams(rows, division):
        for o in get_all_teams(rows, division):
          for g in get_grounds(rows, h):
            if h == o:
              continue
            for d in get_all_dates(rows):
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
    
    # Creates the model.
    model = cp_model.CpModel()

    logging.debug ("Start making variables")
    matches = make_variables(model, rows)

    logging.debug ("Set Home vs Opposition - Play exactly once") 
    home_opposition_constraint(model, rows, matches)

    # logging.debug ("Set Ground constraint")  
    ground_constraint(model, rows, matches)  

    # logging.debug ("Set Home Opposition constraint")  
    teams_on_a_day_constraint(model, rows, matches)

    # # logging.debug ("Set Must constraint from partial result")  
    must_constraint(model, rows, matches, partial_results)   

    # # logging.debug ("Set Home Match constraint")  
    must_home_match_constraint(model, rows, matches)

    # # logging.debug ("Set Consecutive dates constraint")    
    home_opposition_match_date_gap(model, rows, matches)

    # logging.debug ("Set Consecutive dates constraint")    
    consecutive_home_or_aways(model, rows, matches)

    # logging.debug ("Invalid constraints")
    invlalid_constraints(model, rows, matches)  
 
    # print ("Set Number of Matches Constraint")  
    # number_of_matches_constraint(model, rows, valid_states, matches)

    logging.debug ("solve")
    # Creates the model.
    solver = cp_model.CpSolver()
    solver.parameters.stop_after_first_solution=True
    # Display the first five solutions.
    solution_limit = 10
    solution_printer = SolutionPrinter(rows, result_file, matches, all_grounds, all_teams, all_days, solution_limit)

    # Enumerate all solutions.
    # solver.parameters.enumerate_all_solutions = True
    # print (f"Start solving {result_file}")
    status = solver.Solve(model, solution_printer)

    # Statistics.y 
    logging.debug('\nStatistics')
    logging.debug('  - status      : %i %i' % (status, cp_model.FEASIBLE))
    logging.debug('  - conflicts      : %i' % solver.NumConflicts())
    logging.debug('  - branches       : %i' % solver.NumBranches())
    logging.debug('  - wall time      : %f s' % solver.WallTime())
    logging.debug('  - solutions found: %i' % solution_printer.solution_count())

    return solution_printer.solution_count()

if __name__ == '__main__':
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  data_file = "data.xlsx"
  all_rows = read_excel(data_file, "Grounds")
  all_dates = get_all_dates(all_rows)
  # main("2024/partial_results.xlsx", False)
  main()
