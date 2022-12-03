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
from collections import deque

# find teams with max contraints
# resolve the constraints
# if there are multiple ways to solve it, add a check point to return to it

def read_data(book, sheet="Grounds"):
  db = xl.readxl(book)
  ws = db.ws(sheet)
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
  # print(f"{book} {header}")
  # For each row
  while True:
    row = {}
    row_nbr += 1
    # if row's 1st colum is empty quite
    if ws.index(row_nbr, 1) == "":
      break
    for i in header:
      row[i] = ws.index(row_nbr, header[i])
    rows.append(row)
  return rows

def window(seq, n=2):
    it = iter(seq)
    win = deque((next(it, None) for _ in range(n)), maxlen=n)
    yield win
    append = win.append
    for e in it:
        append(e)
        yield win

def get_text(a_window):
  text = ""
  for i in a_window:
    text += i
  return text

def save_result_to_file(matches, file_name="temp_single.xlsx"):
  db = xl.Database()  
  db.add_ws(ws="Grounds")
  row_nbr = 1

  # Header row in rows:
  for match in matches:
    col_nbr = 1
    for key in match:
      db.ws(ws="Grounds").update_index(row=row_nbr, col=col_nbr, val=key)
      col_nbr += 1 
    break

  for match in matches:
    col_nbr = 1
    row_nbr += 1
    for value in match.values():    
      db.ws(ws="Grounds").update_index(row=row_nbr, col=col_nbr, val=value)
      col_nbr += 1  
  xl.writexl(db=db, fn=file_name)

def team_name(row):
  # print (row)
  return row['Club'] + "-" +row['Team']

def init_ground_availability(rows):
  grounds = {}
  for row in rows:
    grounds[row["Ground"]] = {}
    for i in row:
      if not re.match(r"[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]", i) is not None:
        continue
      grounds[row["Ground"]][i] = ""
  return grounds

def init_divisions(rows):
  divisions = {}
  for row in rows:
    if row['Division'] not in divisions:
      divisions[row['Division']]=[]
    divisions[row['Division']].append(team_name(row))

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
    team = team_name(row)
    for division, matches in divisions_cont.items():
      for match in matches:
        if team in [match["Home"], match["Away"]]:
          row['nbr_of_matches'] += 1
    for the_date in get_all_dates(rows):
      if row[the_date] in ["Home", ""]:
        row['home_slots'] += 1

  return divisions_cont


def _find_rows_for_ground(rows, ground):
  matching_rows = []
  for row in rows:
    if row["Ground"] == ground:
      matching_rows.append(row)
  return matching_rows

def ground_is_available(rows, grounds, ground, the_date):
  if grounds[ground][the_date] == "Allotted":
    return False
  
  # if No Home match is indicated which is pretty much mean ground is allotted
  # but it has other meanings as the 2nd team could even play. So double check
  # this condition
  # TODO: check only for team playing on that ground
  for row in _find_rows_for_ground(rows, ground):
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

def team_available_for_away(rows, team, the_date, matches):
  row = get_row_for_team(rows, team)
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
  # if nbr_home_slots_available == nbr_home_matches_to_be_allocated:
  #   return False
  if nbr_home_slots_available < nbr_home_matches_to_be_allocated:
    # should never happen
    return False
  return True
    
def get_row_for_team(rows, the_team):
  for row in rows:
    a_team = team_name(row)
    if the_team == a_team:
      return row

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
    
    if this_home_team in [the_home_team, the_away_team] and this_date == the_date:
      return False
    if this_away_team in [the_home_team, the_away_team] and this_date == the_date:
      return False
  return True


def find_all_possible_dates(rows, match, matches, grounds):
  home_team_row = get_row_for_team(rows, match["Home"])
  away_team_row = get_row_for_team(rows, match["Away"])
  ground =  home_team_row["Ground"]
  opposition = match["Away"]

  possible_dates = []

  for the_date in get_all_dates(rows):    
    # can't do if home ground is not available
    if not ground_is_available(rows, grounds, ground, the_date):
      continue

    # can't do if opposition is can't do Away game
    if not team_available_for_away(rows, opposition, the_date, matches):
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

# def possible_solutions(rows, matches):
#   # any of this will be possible
#   # but order by possible dates, should be faster
#   # to get to the solution
#   sorted_list = sorted(matches, key=lambda d: len(d['possible_dates']))

#   for match in sorted_list:
#     possible_dates = []
#     if match["Date"] != "":
#       continue
#     # if "Home" match is set then give this a high priority
#     possible_dates_prio = []
#     for row in rows:
#       home_team_row = get_row_for_team(match["Home"])
#       if home_team_row[match ["Date"]] == "Home":
#         possible_dates_prio.append(match["Date"])
#         pass
#       break
#     for a_date in match["possible_dates"]:
#       if a_date not in possible_dates_prio:
#         possible_dates_prio.append(a_date)
#     match["possible_dates"] = possible_dates_prio
#     for a_date in match["possible_dates"]: 
#       yield match, a_date
def get_division(rows, the_team_name):
  for row in rows:
    a_team_name = team_name(row)
    if a_team_name == the_team_name:
      return row["Division"]
  assert False

def count_allocated(divisions):
  count = 0
  for divison, matches in divisions.items():
    for match in matches:
      if match["Date"] != "":
        count +=1
  return count

@staticmethod
def get_all_grounds(rows):
  grounds = []
  for row in rows:
    if row["Ground"] not in grounds:
      grounds.append(row["Ground"])
  
  ground_teams ={}
  for row in rows:
    try:
      # if "Quy" in row["Ground"]:
      #   print (row["Ground"])
      ground_teams[row["Ground"]].append(team_name(row))
    except KeyError:
      ground_teams[row["Ground"]] = []
      ground_teams[row["Ground"]].append({"Division":row["Division"] , "team":team_name(row)})
  
  for ground, teams in ground_teams.items():
    if len(teams) > 1:
      pass
      # print (ground)
      # print (teams)
  return grounds

@staticmethod
def get_all_teams(rows, division=""):
  teams = []
  for row in rows:
    the_team = team_name(row)
    if the_team not in teams:
      if division != "" and row["Division"] != division:
        continue
      teams.append(the_team)
  return teams

@staticmethod
def get_all_divisions(rows):
  divisions = []
  for row in rows:
    if row["Division"] not in divisions:
      divisions.append(row["Division"])
  return divisions

@staticmethod
def get_all_dates(rows):
  dates = []
  for row in rows:
    for the_date in row:
      if re.match(r"[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]", the_date) is not None:
        if the_date not in dates:
          dates.append(the_date)
  return dates
  #   # do only for one row
  #   break
  # date_dicts = {}
  # for the_date in dates:
  #   date_dicts[the_date] = 0
  #   for row in rows:
  #     if row[the_date] != "":
  #       date_dicts[the_date] += 1
  
  # return (dict(sorted(date_dicts.items(), key=lambda item: item[1], reverse=True))).keys()

  # return dates
