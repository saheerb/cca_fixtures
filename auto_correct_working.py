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


def save_result_to_file(matches, file_name="temp.xlsx"):
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
  # Header row in rows:
  for match in matches:
    col_nbr = 1
    for key in match:      
      db.ws(ws="Matches").update_index(row=row_nbr, col=col_nbr, val=key)
      col_nbr += 1
    break
  # Header row in rows
  for match in matches:
    col_nbr = 1
    row_nbr += 1
    for value in match.values():      
      db.ws(ws="Matches").update_index(row=row_nbr, col=col_nbr, val=value)
      col_nbr += 1
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

def init_matches():
  divisions = {}
  for row in rows:
    if row['Division'] not in divisions:
      divisions[row['Division']]=[]
    team_name = _team_name(row)
    divisions[row['Division']].append(team_name)
  matches = []

  for division in divisions:
    for match in combinations(divisions[division], 2):
      matches.append({"Division":division, "Home": match[0], "Away": match[1], "Date": "", "Ground": ""})
      matches.append({"Division":division, "Home": match[1], "Away": match[0], "Date": "", "Ground": ""})
  return matches

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
  def nbr_possible_home_slots(row):
    count = 0
    for the_date in _get_all_dates():
      if row[the_date] in ["Home", ""]:
        count += 1
    return count

  row = get_row_for_team(team)
  # team only plays 
  if row[the_date] == "Home":
    return False
  home_slots_available = nbr_possible_home_slots(row) 

  
  # team's Home window specific
  home_slots_needed = 0
  for match in matches:
    if match["Home"] == team and match["Date"] == "":
      home_slots_needed += 1

  if home_slots_available < home_slots_needed:
    return False

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

def teams_available(the_match, home_team_row, away_team_row, the_date):
  # if any team can't play on this date
  # home_team_row = get_row_for_team(the_match["Home"])
  # away_team_row = get_row_for_team(the_match["Away"])
  if home_team_row[the_date] == "No Play" or away_team_row[the_date] == "No Play":
    return False

  # if any team already has match allocated 
  for match in matches:
    # match
    if (match["Away"] == the_match["Home"] or match["Away"]==the_match["Away"]) and match["Date"] == the_date:
      return False
    if (match["Home"] == the_match["Home"] or match["Home"]==the_match["Away"]) and match["Date"] == the_date:
      return False
    # # if match["Away"] in [the_match["Home"], the_match["Away"]] and match["Date"] == the_date:
    # #   return False
    
    # if match["Home"] in [the_match["Home"], the_match["Away"]] and match["Date"] == the_date:
    #   return False
    # if match["Away"] in [the_match["Home"], the_match["Away"]] and match["Date"] == the_date:
    #   return False
  return True


def find_all_possible_dates(i, matches, grounds):
  home_team_row = get_row_for_team(matches[i]["Home"])
  away_team_row = get_row_for_team(matches[i]["Away"])
  ground =  home_team_row["Ground"]
  opposition = matches[i]["Away"]

  possible_dates = []

  for the_date in _get_all_dates():
    # can't do if home ground is not available
    if not ground_is_available(grounds, ground, the_date):
      continue

    # can't do if opposition is can't do Away game
    if not team_available_for_away(opposition, the_date, matches):
      continue

    # can't do if teams cannot play
    if not teams_available(matches[i], home_team_row, away_team_row, the_date):
      continue

    possible_dates.append(the_date)

  return possible_dates, ground

def all_matches_allotted(matches):
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
def number_of_allocated(matches):
  count = 0
  for match in matches:
    if match["Date"] != "":
      count +=1
  return count
def build_fixtures(matches, grounds):
  print (rf"Number of matches allocated - {number_of_allocated(matches)}")

  if all_matches_allotted(matches):
    save_result_to_file(matches)
    sys.exit()
    return

  for i in range(len(matches)):
    if matches[i]["Date"] != "":
      continue

    possible_dates, ground = find_all_possible_dates(i, matches, grounds)
    
    if len(possible_dates) == 0:
      #  if possible_dates are zero then go back previous stage and run with another date
      print ("This path wont work stop here")
      return

    matches[i]["possible_dates"] = possible_dates
    matches[i]["Ground"] = ground

  for possible_solution, the_date in possible_solutions(matches):
    for match in matches:
      if match["Home"] == possible_solution["Home"] and match["Away"] == possible_solution["Away"]:
        break
    match["Date"] = the_date
    grounds[match["Ground"]][match["Date"]] = "Allotted"
    print (possible_solution)
    build_fixtures(copy.deepcopy(matches), copy.deepcopy(grounds))








  
rows = read_data("fix_.xlsx")

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
matches = init_matches()
grounds = init_ground_availability()
# build_fixtures(copy.deepcopy(matches), copy.deepcopy(grounds))
cProfile.run('build_fixtures(copy.deepcopy(matches), copy.deepcopy(grounds))')
# build_fixtures(copy.deepcopy(matches), copy.deepcopy(grounds))
