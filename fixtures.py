import pylightxl as xl
import json
from datetime import datetime, timedelta
from collections import OrderedDict
import re
import sys
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
  header = OrderedDict()
  rows = []
  while True:
    value = ws.index(row_nbr, col_nbr)
    if value == "":
      break
    header[value]=col_nbr
    col_nbr += 1

  # For each row
  while True:
    row = OrderedDict()
    row_nbr += 1
    if ws.index(row_nbr, header["Division"]) == "":
      break
    for i in header:
      row[i] = ws.index(row_nbr, header[i])
    rows.append(row)
  return rows



def get_team_with_max_constraints(rows, processed_teams):
  # find row with maximum non empty
  for row in rows:
    row["constraints"] = 0
    for i in row:
      if not re.match(r"[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]", i) is not None:
        continue

      if row[i] in ["No Play",  "No Home", "Home"]:
        row["constraints"] += 1
      elif row[i] != "":
        raise "Unidentified constraint"

  # find the row with max constraint
  max_constraint = 0
  for row in rows:
    team = _team_name(row)
    if team in processed_teams:
      continue
    if row["constraints"] >= max_constraint:
      max_constrain_row = row
      max_constraint = row["constraints"]
  
  # print(max_constraint)
  return max_constrain_row

def _team_name(row):
  # print (row)
  return row['Club'] + "-" +row['Team']

def init_ground_availability(rows):
  grounds = {}
  for row in rows:
    grounds[row["Ground"]] = {}
    for i in row:
      if not re.match(r"[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]", i) is not None:
        continue
      grounds[row["Ground"]][i] = ""
  return grounds

def init_matches(rows):
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


    # print (list(combinations(divisions[division], 2)))
def _find_rows_for_ground(rows, ground):
  matching_rows = []
  for row in rows:
    if row["Ground"] == ground:
      matching_rows.append(row)
  return matching_rows

def ground_is_available(grounds, ground, the_date, rows):
  # if grounds[ground][the_date] == "Allotted":
  #   return False
  
  # if No Home match is indicated which is pretty much mean ground is allotted
  # but it has other meanings as the 2nd team could even play. So double check
  # this condition
  for row in _find_rows_for_ground(rows, ground):
    if row[the_date] != "":
      return False
  return True

def get_row_for_team(the_team, rows):
  for row in rows:
    a_team = _team_name(row)
    if the_team == a_team:
      return row

# def allot_ground_for_date(grounds, ground, the_date):
#   grounds[ground][the_date] = "Allotted"

def get_ground_of_team(team, rows):
  row = get_row_for_team(team, rows)
  return row["Ground"]

def add_constraint(constraint, rows, team, the_date):
  row = get_row_for_team(team, rows)
  row[the_date] = constraint

def teams_available(the_match, rows, the_date):
  # if any team can't play on this date
  for row in rows:
    if row[the_date] == "No Play":
      return False
    
  # if any team already has match allocated 
  for match in matches:
    if match["Home"] in [the_match["Home"], the_match["Home"]] and match["Date"] == the_date:
      return False
    if match["Away"] in [the_match["Home"], the_match["Home"]] and match["Date"] == the_date:
      return False
  return True

def _build_fixture_for_a_team(team, matches, grounds, rows):
  row = get_row_for_team(team, rows)
  for the_date in row:
    if not re.match(r"[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]", the_date) is not None:
      continue
    if row[the_date] in ["No Play"]:
      pass
    elif row[the_date] in ["No Home"]:
      # Give an away match on this date
      for match in matches:
        if (team in match["Away"] and match["Date"] == ""):
          away_ground = get_ground_of_team(match["Home"], rows)
          if ground_is_available(grounds, away_ground, the_date, rows) and teams_available(match, rows, the_date):
            match["Date"] = the_date
            match["Ground"] = away_ground
            # make sure ground is marked as allocated
            # allot_ground_for_date(grounds, away_ground, the_date)
            # now that ground is allocated add a constrain "No Home"
            add_constraint("No Home", rows, match["Home"], the_date)
            # save_result_to_file(rows, matches, "int.xlsx")
            # sys.exit()
            break

# def _build_fixture_for_a_team1(team, matches, grounds, rows):
#   row = get_row_for_team(team, rows)
#   for i in row:
#     if not re.match(r"[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]", i) is not None:
#       continue
#     if row[i] in ["No Play"]:
#       pass
#     elif row[i] in ["No Home"]:
#       # Give an away match on this date
#       for match in matches:
#         if (team in match["Away"] and match["Date"] == ""):
#           away_ground = get_ground_of_team(match["Home"], rows)
#           if ground_is_available(grounds, away_ground, i, rows) and teams_available(match, rows, i):
#             match["Date"] = i
#             match["Ground"] = away_ground
#             # make sure ground is marked as allocated
#             allot_ground_for_date(grounds, away_ground, i)
#             break
#     else:
#       # Give an home match on this date
#       for match in matches:
#         if (team in match["Home"] and match["Date"] == ""):
#           home_ground = get_ground_of_team(match["Home"], rows)
#           if ground_is_available(grounds, home_ground, i, rows) and teams_available(match, rows, i):
#             match["Date"] = i
#             match["Ground"] = home_ground
#             # make sure ground is marked as allocated
#             allot_ground_for_date(grounds, home_ground, i)
#             break
#         elif (team in match["Away"] and match["Date"] == ""):
#           away_ground = get_ground_of_team(match["Home"], rows)
#           if ground_is_available(grounds, away_ground, i, rows) and teams_available(match, rows, i):
#             match["Date"] = i
#             match["Ground"] = away_ground
#             # make sure ground is marked as allocated
#             allot_ground_for_date(grounds, away_ground, i)
#             break

def all_matches_allotted(team, matches):
  for match in matches:
    if (team in match["Home"] or team in match["Away"]) and match["Date"] == "":
      return False
  return True

def _get_possible_dates(rows):
  dates = []
  for row in rows:
    for the_date in row:
      if re.match(r"[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]", the_date) is not None:
        dates.append(the_date)
    # do only for one row
    break
  return dates

def match_present(team, the_date, matches, type="Away"):
  for match in matches:
    if (team == match[type]):
      if match["Date"] == the_date:
        return True
      print ("ddddd")
      print (the_date)
      print (match["Date"])
      print ("ddddd")
  return False

def all_matches_allotted(team, matches, type="Home"):
  for match in matches:
    if (team == match[type]):
      if match["Date"] == "":
        return False
  return True

def all_constrained_matches_allotted(team, matches, rows):
  team_row = get_row_for_team(team, rows)
  for the_date in _get_possible_dates(rows):
    # if No Home matches are possible
    if team_row[the_date] == "No Home":
      # either we have allocated all home matches for this team
      # an away match is allocated
      if not all_matches_allotted(team, matches, "Home") and not match_present(team, the_date, matches, "Away"):
        return False
  return True
    # elif team_row[the_date] == "Home":

def save_result_to_file(rows, matches, file_name="temp_out.xlsx"):
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

def print_teams(rows, processed_teams):
  row_names = []
  for row in rows:
    row_names.append(_team_name(row))
  
  row_names =sorted(row_names)
  processed_teams = sorted(processed_teams)

  print (row_names)
  print (processed_teams)
  i = 0
  while True:
    print (row_names[i])
    print (processed_teams[i])
    if row_names[i] != processed_teams[i]:
      break
    i += 1

  

def build_fixtures(matches, grounds, rows):
  # save_result_to_file(rows, matches)
  # sys.exit()
  processed_teams = []
  retry_count = 0
  loop_team = ""
  while True:
    if len(rows) == len(processed_teams):
      break
    row = get_team_with_max_constraints(rows, processed_teams)
    # print_teams(rows, processed_teams)
    team = _team_name(row)
    if loop_team == team:
      retry_count += 1
    else:
      retry_count = 0
      loop_team = team



    print (team)
    _build_fixture_for_a_team(team, matches, grounds, rows)

    # if constrained matches are allocated
    # add to done. Rest can be done late
    if all_constrained_matches_allotted(team, matches, rows):
      if team not in processed_teams:
        processed_teams.append(team)

    if retry_count == 10:
      save_result_to_file(rows, matches)
      sys.exit(0)
  # processed_teams = []
  # while True:
  #   if len(rows) == len(processed_teams):
  #     break
  #   row = get_team_with_max_constraints(rows, processed_teams)
  #   # print_teams(rows, processed_teams)
  #   team = _team_name(row)
  #   _build_fixture_for_a_team(team, matches, grounds, rows)

  #   # if constrained matches are allocated
  #   # add to done. Rest can be done late
  #   if all_constrained_matches_allotted(team, matches, rows):
  #     if team not in processed_teams:
  #       processed_teams.append(team)

    save_result_to_file(rows, matches)
    # sys.exit()
    # check if all matches are allocated
    # if all_matches_allotted(team, matches):
    # if team not in processed_teams:
    #   processed_teams.append(team)

    # print ("+++++++++")
    # for match in matches:
    #   if team in match["Home"] or team in match["Away"]:
    #     print (match)
    
    # if all matches are allotted, quit
      


  # print (row)
  # for match in matches:
  #   if team_name in match["Home"] or team_name in match["Away"]:
  #     print (match)
    # row = get_row_for_team(rows, team_name)
    # print (row)



      


  
rows = read_data("fix_.xlsx")

matches = init_matches(rows)
grounds = init_ground_availability(rows)

# teat = init_team_availability(rows)

build_fixtures(matches, grounds, rows)

# team = "Newmarket CC-2nd XI"
# for match in matches:
#   if (team in match["Home"] or team in match["Away"]) and match["Date"] == "":
#     print (match)