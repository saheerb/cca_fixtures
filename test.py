from ortools.sat.python import cp_model
from utils import *
import shutil

def test_conditions(rows, matches):
  for team_row in rows:
    home_team_name = team_name(team_row)
    for the_match in matches:
      if the_match["Home"] != team_name:
        continue
      for the_date in get_all_dates(rows):
        assert team_row[the_date] != "No Home"
        assert team_row[the_date] != "No Play"
        assert team_row[the_date] != "Off Request"

    for the_date in get_all_dates(rows):
      if team_row[the_date] == "Home":
        # match exists
        bHome = False
        for a_match in matches:
          if a_match["Home"] == home_team_name and a_match["Date"] == the_date:
             bHome = True
        assert bHome == True

def test_no_ground_conflicts(rows, matches):
  for the_match in matches:
    fixture_ground = the_match["Ground"]
    fixture_date = the_match["Date"]
    for a_match in matches:
      if the_match == a_match:
        continue
      if fixture_date == a_match["Date"]:
        if fixture_ground == a_match["Ground"]:
          print (the_match)
          print (a_match)
        assert fixture_ground != a_match["Ground"]

def test_no_dates_conflicts(rows, matches):
  for the_match in matches:
    fixture_ground = the_match["Ground"]
    fixture_home = the_match["Home"]
    fixture_opposition = the_match["Away"]
    fixture_date = the_match["Date"]
    for a_match in matches:
      if the_match == a_match:
        continue
      if fixture_date == a_match["Date"]:
        assert fixture_home not in [a_match["Home"], a_match["Away"]]
        assert fixture_opposition not in [a_match["Home"], a_match["Away"]]

def test_number_of_matches(rows, matches):
  for division in get_all_divisions(rows):
    for team_name in get_all_teams(rows, division):
      nb_expected_one_leg_matches = len(get_all_teams(rows,division)) - 1
      home_matches_count = 0
      away_matches_count = 0
      for a_match in matches:
        if team_name == a_match["Home"]:
          home_matches_count += 1
        if team_name == a_match["Away"]:
          away_matches_count += 1
      assert nb_expected_one_leg_matches == home_matches_count
      assert nb_expected_one_leg_matches == away_matches_count


def test_results(rows, matches):
  test_number_of_matches(rows, matches)
  test_no_dates_conflicts(rows, matches)
  test_no_ground_conflicts(rows, matches)
  test_conditions(rows, matches)
  print ("all tests done")

def test_results_indexes(rows, matches):
  match_dicts = []
  for match in matches:
    match_dicts.append({"Ground":match[0], "Home":match[1], "Away":match[2],"Date": match[3]})

  
  test_number_of_matches(rows, match_dicts)
  test_no_dates_conflicts(rows, match_dicts)
  test_no_ground_conflicts(rows, match_dicts)
  test_conditions(rows, match_dicts)
  

def main():
  rows = read_data("data.xlsx")
  matches = read_data("tmp/result-partial-1.xlsx")
  test_results(rows, matches)
  print ("all tests done")


if __name__ == '__main__':
  main()
