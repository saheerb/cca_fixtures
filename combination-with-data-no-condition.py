from itertools import combinations
import copy
import sys
import random
from utils_simple import *

# teams = [x for x in range(10)]
# dates = [x for x in range(18)]

def all_matches_allocated(matches):
  for match in matches:
    if match["Date"] == "":
      return False
  return True

def count_allocated(matches):
  count = 0
  for match in matches:
    if match["Date"] != "":
      count +=1
  return count

def init_matches(rows):
  divisions = {}
  for row in rows:
    if row['Division'] not in divisions:
      divisions[row['Division']]=[]
    divisions[row['Division']].append(team_name(row))
  matches = []

  for division in divisions:
    for match in combinations(divisions[division], 2):
      matches.append({"Division":division, "Home": match[0], "Away": match[1], "Date": "", "Ground": ""})
    for match in combinations(divisions[division], 2):
      matches.append({"Division":division, "Home": match[1], "Away": match[0], "Date": "", "Ground": ""})
  return matches

def teams_already_playing(teams, matches, the_date):
  for match in matches:
    if match["Date"] == the_date:
      if match["Home"] in teams:
        return True
      if match["Away"] in teams:
        return True
  return False

def find_possible_dates(the_match, matches):
  possible_dates = []
  # if match is already allotted
  for the_date in get_all_dates(rows):
    if teams_already_playing([the_match["Home"], the_match["Away"]], matches, the_date):
      continue
    possible_dates.append(the_date)
  return possible_dates

def test_results(matches):
  # check all have dates
  # for division, matches in divisions.items():
  #   for i in matches:
  #     assert i["Date"] != ""


  for a_match in matches:
    fixture_home_team = a_match["Home"]
    fixture_away_team = a_match["Away"]
    fixture_match_date = a_match["Date"]
    if fixture_match_date == "":
      continue

    for the_match in matches:
      if a_match == the_match:
        continue
      if fixture_match_date == the_match["Date"]:
        assert fixture_home_team not in [the_match["Home"], the_match["Away"]]
        assert fixture_away_team not in [the_match["Home"], the_match["Away"]]
  
  # for division, matches in divisions.items():
  #   for a_match in matches:
  #     if a_match["Date"] == "":
  #       continue
  #     team_row = get_row_for_team(rows, a_match["Home"])
  #     assert team_row[a_match["Date"]] != "No Play"
  #     the_team_name = team_name(team_row)
  #     print (team_row[a_match["Date"]])
  #     if team_row[a_match["Date"]] == "Home":
  #       assert a_match["Home"] == the_team_name
  #     if team_row[a_match["Date"]] == "No Home":
  #       assert a_match["Home"] != the_team_name

def fixture(rows, matches):
  count = 0
  print (rf"Allocated matches: {count_allocated(matches)}")
  if all_matches_allocated(matches):
    test_results(matches)
    match_states = []
    for match in matches:
      print (match)
      print (get_all_dates(rows))
      match_states.append(get_all_dates(rows).index(match["Date"]))
    print (match_states)
    print ("Solved")
    sys.exit()
    # TODO: Add to solutions
    # reset match dates
    return True

  for match in matches:
    if match["Date"] != "":
      continue
    possible_dates = find_possible_dates(match, matches)
    match["possible_dates"] = possible_dates
    if (len(possible_dates)) == 0:
      pass
      #print ("Can't continue")
      return False
  
  # least possible dates can be in allocated ones too
  i = ""
  possible_matches = []
  for i in matches:
    if i["Date"] == "":
      possible_matches.append(i)

  possible_matches = sorted(possible_matches, key=lambda d: len(d['possible_dates']))
  match = possible_matches[0]
  
  for the_date in match["possible_dates"]:
    match["Date"] = the_date
    # TODO: check sanity
    # no team is playing on two date
    fixture(rows, copy.deepcopy(matches))
    match["Date"] = ""
    
if __name__ == "__main__":
  sys.setrecursionlimit(3000)
  rows = read_data("fix-1.xlsx")
  # grounds = init_ground_availability(rows)
  matches = init_matches(rows)
  fixture(rows, matches)  
