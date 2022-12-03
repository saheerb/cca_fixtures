from itertools import combinations
import copy
import sys
import random
from utils import *

def test_results(rows, divisions):
  # check all have dates
  # for division, matches in divisions.items():
  #   for i in matches:
  #     assert i["Date"] != ""
  
  # no two teams playing on same date
  for division, matches in divisions.items():
    for a_match in matches:
      fixture_home_team = a_match["Home"]
      fixture_away_team = a_match["Away"]
      fixture_match_date = a_match["Date"]
      if fixture_match_date == "":
        continue
      for division, matches in divisions.items():
        for the_match in matches:
          if a_match == the_match:
            continue
          if fixture_match_date == the_match["Date"]:
            assert fixture_home_team not in [the_match["Home"], the_match["Away"]]
            assert fixture_away_team not in [the_match["Home"], the_match["Away"]]
  
  for division, matches in divisions.items():
    for a_match in matches:
      if a_match["Date"] == "":
        continue
      team_row = get_row_for_team(rows, a_match["Home"])
      assert team_row[a_match["Date"]] != "No Play"
      the_team_name = team_name(team_row)
      print (team_row[a_match["Date"]])
      if team_row[a_match["Date"]] == "Home":
        assert a_match["Home"] == the_team_name
      if team_row[a_match["Date"]] == "No Home":
        assert a_match["Home"] != the_team_name
      

def possible_solutions(rows, matches):
  # any of this will be possible
  # but order by possible dates, should be faster
  # to get to the solution
  # matches = []
  # for division, this_matches in divisions.items():
  #   for match in this_matches:
  #     matches.append(match)

  sorted_list = sorted(matches, key=lambda d: len(d['possible_dates']))

  for match in sorted_list:
    if match["Date"] != "":
      continue

    # Adjust dates such that "Home" matches are prioritized - BEGIN
    possible_dates_prio = []
    home_team_row = get_row_for_team(rows, match["Home"])
    for a_date in match["possible_dates"]:
      if home_team_row[a_date] == "Home":
        # possible_dates_prio.append(a_date)
        possible_dates_prio = [a_date]

    if possible_dates_prio != []:
      match["possible_dates"] =  possible_dates_prio
    # else:
    #   match["possible_dates"] = 
    # for a_date in match["possible_dates"]:
    #   if a_date not in possible_dates_prio:
    #     possible_dates_prio.append(a_date)

    # match["possible_dates"] = possible_dates_prio
    # Adjust dates such that "Home" matches are prioritized - END

    for a_date in match["possible_dates"]:
      if a_date not in possible_dates_prio:
        possible_dates_prio.append(a_date)
      yield match, a_date


def build_fixtures(rows, divisions, grounds):
  test_results(rows, divisions)
  print (rf"Allocated matches: {count_allocated(divisions)}")
  if all_matches_allotted(divisions):
    save_result_to_file(rows, divisions, "result-div.xlsx")
    test_results(rows, divisions)
    print ("Solved")
    sys.exit()
    # TODO: Add to solutions
    # reset match dates
    return True

  for division, matches in divisions.items():
    for match in matches:
      if match["Date"] != "":
        continue

      possible_dates, ground = find_all_possible_dates(rows, match, matches, grounds)
      match["possible_dates"] = possible_dates
      match["Ground"] = ground
      if len(possible_dates) == 0:
        #  if possible_dates are zero then go back previous stage and run with another date
        print ("This path wont work stop here")
        return False

    for possible_solution, the_date in possible_solutions(rows, matches):
      # find match associated to possible solution in the data structure
      # we may not need to do this as accessing possible solution may be enough
      possible_match = ""
      for match in matches:
        if match["Home"] == possible_solution["Home"] and match["Away"] == possible_solution["Away"]:
          possible_match = match
          break

      
      possible_match["Date"] = the_date
      test_results(rows, divisions)
      grounds[possible_match["Ground"]][possible_match["Date"]] = "Allotted"
      if build_fixtures(rows, copy.deepcopy(divisions), copy.deepcopy(grounds)) == False:
        grounds[possible_match["Ground"]][possible_match["Date"]] = ""
        possible_match["Date"] = ""
      else:
        pass

if __name__ == "__main__":
  sys.setrecursionlimit(3000)
  rows = read_data("test.xlsx")
  grounds = init_ground_availability(rows)
  divisions = init_divisions(rows)
  build_fixtures(rows, divisions, grounds)    
