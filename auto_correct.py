import cProfile
import pylightxl as xl
import json
from datetime import datetime, timedelta
from collections import OrderedDict
import re
import sys
import random
import copy
from itertools import combinations
from functools import reduce

# find teams with max contraints
# resolve the constraints
# if there are multiple ways to solve it, add a check point to return to it

def read_data(book):
  db = xl.readxl(book)
  ws = db.ws('Grounds')
  # get column
  row_nbr = 1
  col_nbr = 1
  header = {}
  rows = []
  while True:
    value = ws.index(row_nbr, col_nbr)
    if value == "":
      break
    header[value]=col_nbr
    col_nbr += 1

  # For each row
  while True:
    row = {}
    row_nbr += 1
    if ws.index(row_nbr, header["Division"]) == "":
      break
    for i in header:
      row[i] = ws.index(row_nbr, header[i])
    rows.append(row)
  return rows


def save_result_to_file(divisions, file_name="temp_single.xlsx"):
  db = xl.Database()
  db.add_ws(ws="Grounds")
  row_nbr = 1
  # Header row in rows:
  for row in rows:
    col_nbr = 1
    for key in row:      
      db.ws(ws="Grounds").update_index(row=row_nbr, col=col_nbr, val=key)
      col_nbr += 1
    break
  # Header row in rows
  for row in rows:
    col_nbr = 1
    row_nbr += 1
    for value in row.values():      
      db.ws(ws="Grounds").update_index(row=row_nbr, col=col_nbr, val=value)
      col_nbr += 1
  
  db.add_ws(ws="Matches")
  row_nbr = 1
  for matches in divisions.values():
    # Header row in rows:
    for match in matches:
      col_nbr = 1
      db.ws(ws="Matches").update_index(row=row_nbr, col=col_nbr, val="Division")
      for key in match:
        col_nbr += 1      
        db.ws(ws="Matches").update_index(row=row_nbr, col=col_nbr, val=key)
      break
    break
  for division, matches in divisions.items():
    # Header row in rows
    for match in matches:
      col_nbr = 1
      row_nbr += 1
      db.ws(ws="Matches").update_index(row=row_nbr, col=col_nbr, val=division)
      for value in match.values():
        col_nbr += 1      
        db.ws(ws="Matches").update_index(row=row_nbr, col=col_nbr, val=value)
  xl.writexl(db=db, fn=file_name)

def _team_name(row):
  # print (row)
  return row['Club'] + "-" +row['Team']

def init_ground_availability():
  grounds = {}
  for row in rows:
    grounds[row["Ground"]] = {}
    for i in row:
      if not re.match(r"[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]", i) is not None:
        continue
      grounds[row["Ground"]][i] = ""
  return grounds

def init_divisions():
  divisions = {}
  for row in rows:
    if row['Division'] not in divisions:
      divisions[row['Division']]=[]
    team_name = _team_name(row)
    divisions[row['Division']].append(team_name)


  divisions_cont = {}

  for division in divisions:
    divisions_cont[division] = []
    for match in combinations(divisions[division], 2):
      divisions_cont[division].append({"Home": match[0], "Away": match[1], "Date": "", "Ground": ""})
      divisions_cont[division].append({"Home": match[1], "Away": match[0], "Date": "", "Ground": ""})
  
  # initialize numbers to use somewhere else
  for row in rows:
    row['nbr_of_matches'] = 0
    row['home_slots'] = 0
    team = _team_name(row)
    for division, matches in divisions_cont.items():
      for match in matches:
        if team in [match["Home"], match["Away"]]:
          row['nbr_of_matches'] += 1
    for the_date in _get_all_dates():
      if row[the_date] in ["Home", ""]:
        row['home_slots'] += 1

  return divisions_cont


# def init_matches1():
#   divisions = {}
#   for row in rows:
#     if row['Division'] not in divisions:
#       divisions[row['Division']]=[]
#     team_name = _team_name(row)
#     divisions[row['Division']].append(team_name)
#   matches = []

#   for division in divisions:
#     for match in combinations(divisions[division], 2):
#       matches.append({"Division":division, "Home": match[0], "Away": match[1], "Date": "", "Ground": ""})
#       matches.append({"Division":division, "Home": match[1], "Away": match[0], "Date": "", "Ground": ""})
#   return matches

def _find_rows_for_ground(ground):
  matching_rows = []
  for row in rows:
    if row["Ground"] == ground:
      matching_rows.append(row)
  return matching_rows

def ground_is_available(grounds, ground, the_date):
  if grounds[ground][the_date] == "Allotted":
    return False
  
  # if No Home match is indicated which is pretty much mean ground is allotted
  # but it has other meanings as the 2nd team could even play. So double check
  # this condition
  # TODO: check only for team playing on that ground
  for row in _find_rows_for_ground(ground):
    if row[the_date] != "":
      if row[the_date] != "Home":
        return False
  return True

def ground_available_for_away(ground, the_date):
  for row in _find_rows_for_ground(ground):
    # Marked for Home only
    if row[the_date] == "Home":
      return False
    # if there is no window for an away match
  return True

def team_available_for_away(team, the_date, matches):
  row = get_row_for_team(team)
  # team only plays 
  if row[the_date] == "Home":
    return False
  
  initial_home_slots = row['home_slots'] 
  total_home_matches = row['nbr_of_matches']/2
  
  # team's Home window specific
  home_matches_allocated = 0
  nbr_home_slots_used = 0
  for match in matches:
    if match["Home"] == team and match["Date"] != "":
      home_matches_allocated += 1
      if row[match["Date"]] == "" or row[match["Date"]] == "Home":
        nbr_home_slots_used += 1

  nbr_home_matches_to_be_allocated = total_home_matches - home_matches_allocated
  nbr_home_slots_available = initial_home_slots - nbr_home_slots_used
  if nbr_home_slots_available == nbr_home_matches_to_be_allocated:
    return False
  elif nbr_home_slots_available < nbr_home_matches_to_be_allocated:
    # should never happen
    assert False
  return True
    
def get_row_for_team(the_team):
  for row in rows:
    a_team = _team_name(row)
    if the_team == a_team:
      return row

# def allot_ground_for_date(grounds, ground, the_date):
#   grounds[ground][the_date] = "Allotted"

# def get_ground_of_team(team):
#   row = get_row_for_team(team, rows)
#   return row["Ground"]

def add_constraint(constraint, team, the_date):
  row = get_row_for_team(team)
  row[the_date] = constraint

def teams_available(the_match, home_team_row, away_team_row, the_date, matches):
  # if any team can't play on this date
  # home_team_row = get_row_for_team(the_match["Home"])
  # away_team_row = get_row_for_team(the_match["Away"])
  if home_team_row[the_date] == "No Play" or away_team_row[the_date] == "No Play":
    return False

  # if any team already has match allocated 
  the_home_team = the_match["Home"]
  the_away_team = the_match["Away"]
  for match in matches:
    this_home_team = match["Home"] 
    this_away_team = match["Away"] 
    this_date = match["Date"] 
    # if (match["Away"] == the_match["Home"] or match["Away"]==the_match["Away"]) and match["Date"] == the_date:
    #   return False
    # if (match["Home"] == the_match["Home"] or match["Home"]==the_match["Away"]) and match["Date"] == the_date:
    #   return False
    # # if match["Away"] in [the_match["Home"], the_match["Away"]] and match["Date"] == the_date:
    # #   return False
    
    if this_home_team in [the_home_team, the_away_team] and this_date == the_date:
      return False
    if this_away_team in [the_home_team, the_away_team] and this_date == the_date:
      return False
  return True


def find_all_possible_dates(match, matches, grounds):
  home_team_row = get_row_for_team(match["Home"])
  away_team_row = get_row_for_team(match["Away"])
  ground =  home_team_row["Ground"]
  opposition = match["Away"]

  possible_dates = []

  for the_date in _get_all_dates():
    # can't do if home ground is not available
    if not ground_is_available(grounds, ground, the_date):
      continue

    # can't do if opposition is can't do Away game
    if not team_available_for_away(opposition, the_date, matches):
      continue

    # can't do if teams cannot play
    if not teams_available(match, home_team_row, away_team_row, the_date, matches):
      continue

    possible_dates.append(the_date)

  return possible_dates, ground

def all_matches_allotted(divisions):
  for divison, matches in divisions.items():
    for match in matches:
      if match["Date"] == "":
        return False
  return True

def choose_match_with_lower_possibility(matches):
  min_dates = 100
  for match in matches:
    if match["Date"] != "":
      continue
    if len(match["possible_dates"]) < min_dates:
      min_dates = len(match["possible_dates"])
      tmp_constrained_match = match
  
  # pick date least in demand
  equal_prio_matches = []
  for match in matches:
    if match["Date"] != "":
      continue
    if len(match["possible_dates"]) == len (tmp_constrained_match["possible_dates"]):
      equal_prio_matches.append(match)
  
  print ("Equal -> BEGIN")
  occurences = {}
  for match in equal_prio_matches:
    for the_date in match["possible_dates"]:
      if the_date not in occurences:
        occurences[the_date] = 0
      occurences[the_date] += 1
  
  min_occurence = 10
  for the_date in occurences:
    if occurences[the_date] < min_occurence:
      min_occurence = occurences[the_date]
      best_date = the_date

  for match in equal_prio_matches:
    if best_date in match["possible_dates"]:
      constrained_match = match
      break

  print (occurences)
  print (the_date)
  print ("Equal -> END")
  
  return constrained_match, best_date


def possible_solutions(matches):
  # any of this will be possible
  # but order by possible dates, should be faster
  # to get to the solution
  sorted_list = sorted(matches, key=lambda d: len(d['possible_dates']))

  for match in sorted_list:
    if match["Date"] != "":
      continue
    for a_date in match["possible_dates"]: 
      yield match, a_date
def number_of_allocated(divisions):
  count = 0
  for divison, matches in divisions.items():
    for match in matches:
      if match["Date"] != "":
        count +=1
  return count


def any_true(a, b):
  return bool(a or b)


def build_fixtures(divisions, grounds):
  # for match in matches:
  #   possible_dates, ground = find_all_possible_dates(match, matches, grounds)
  #   match["possible_dates"] = possible_dates
  # for match in matches:
  #   if "Cambourne CC-2nd XI" in [match ["Home"]]:
  #     match["constraints"] = 5
  #   # elif "Wisbech Town CC-3rd XI" in [match["Away"], match ["Home"]]:
  #   #   match["constraints"] = 4
  #   # elif "March Town CC-2nd XI" in [match["Away"], match ["Home"]]:
  #   #   match["constraints"] = 2
  #   # elif "Madingley CC-1st XI" in [match["Away"], match ["Home"]]:
  #   #   match["constraints"] = 3
  #   else:
  #     match["constraints"] = 0
  #     pass

  # sorted_list = sorted(matches, key=lambda d: d['constraints'])
  # _build_fixtures(divisions, grounds, 0)
  combinations = []
  for division, matches in divisions.items():
    for match in matches:
      if match["Date"] != "":
        continue
      possible_dates, ground = find_all_possible_dates(match, matches, grounds)
      for the_date in possible_dates:
        combinations.append({"Home": match["Home"], "Away": match["Away"], "Date": the_date, "Ground": ground})
  unique = []
  print (len(combinations))
  date_ground = []
  home_opposition_ground = []
  for combination in combinations:
    if combination in unique:
      assert False
    if combination not in unique:
      unique.append(combination)
      i = {"date": combination["Date"], "ground":  combination["Ground"]}
      j = {"date": combination["Date"], "Home":  combination["Home"], "Away":  combination["Away"]}
      if i not in date_ground:
        date_ground.append(i)
      if j not in home_opposition_ground:
        home_opposition_ground.append(j)
  
  reduce(get_unique, combinations)
  print (len(date_ground))
  print (len(home_opposition_ground))
    # if combination in unique:
    #   assert False



def _build_fixtures(divisions, grounds, count):
  count  = number_of_allocated(divisions)
  print (rf"Number of matches allocated - {count}")
  
  # may be we should do this in some sort of priority order
  if all_matches_allotted(divisions):
    save_result_to_file(divisions)
    sys.exit()
    return

  if count % 1 == 0:
    for division, matches in divisions.items():
      for match in matches:
        possible_dates, ground = find_all_possible_dates(match, matches, grounds)
        match["possible_dates"] = possible_dates

      matches = sorted(matches, key=lambda d: len(d['possible_dates']))
  # random.shuffle(matches)
  for division, matches in divisions.items():
    print (match)
    for match in matches:
      if match["Date"] != "":
        continue

      possible_dates, ground = find_all_possible_dates(match, matches, grounds)
      match["possible_dates"] = possible_dates
      
      if len(possible_dates) == 0:
        #  if possible_dates are zero then go back previous stage and run with another date
        print ("This path wont work stop here")
        print (match)
        return False

      for the_date in match["possible_dates"]:
        print (the_date)
        match["Date"] = the_date
        match["Ground"] = ground
        grounds[ground][the_date] = "Allotted"
        if not _build_fixtures(copy.deepcopy(divisions), copy.deepcopy(grounds), number_of_allocated(divisions)):
          match["Date"] = ""
          grounds[ground][the_date] = ""

      return True

  # for possible_solution, the_date in possible_solutions(matches):
  #   for match in matches:
  #     if match["Home"] == possible_solution["Home"] and match["Away"] == possible_solution["Away"]:
  #       break
  #   match["Date"] = the_date
  #   grounds[match["Ground"]][match["Date"]] = "Allotted"
  #   print (possible_solution)
  #   if not _build_fixtures(copy.deepcopy(matches), copy.deepcopy(grounds), number_of_allocated(matches)):
  #     match["Date"] = ""
  #     grounds[match["Ground"]][match["Date"]] = ""

  
rows = read_data("test.xlsx")

def get_all_dates():
  dates = []
  for row in rows:
    for the_date in row:
      if re.match(r"[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]", the_date) is not None:
        dates.append(the_date)
    # do only for one row
    break
  return dates

sys.setrecursionlimit(3000)
dates = get_all_dates()
def _get_all_dates():
  return dates
# divisions = init_divisions()
# grounds = init_ground_availability()
# build_fixtures(copy.deepcopy(matches), copy.deepcopy(grounds))
cProfile.run('build_fixtures(copy.deepcopy(init_divisions()), copy.deepcopy(init_ground_availability()))')
# build_fixtures(copy.deepcopy(matches), copy.deepcopy(grounds))
