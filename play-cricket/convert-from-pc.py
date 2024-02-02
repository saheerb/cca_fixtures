from ortools.sat.python import cp_model
from utils import *
import shutil
from test import test_results_indexes
from test import test_results
import logging

def main():
  data_rows = read_data("data.xlsx", "Grounds")
  play_cricket_data = "/Users/sahbab01/Downloads/download_fixtures (19).xlsx"
  original_matches = read_data(play_cricket_data)
  updated = []
  for match in original_matches:
    print (match)
    home = match["Home Team"]
    away = match["Away Team"]
    division = match["Division / Cup"]
    match.pop("Home Team")
    match.pop("Away Team")
    match.pop("Division / Cup")
    match["Division"] = division
    match["Home"] = str(html.unescape(home)).replace("&", "and")
    match["Away"] = str(html.unescape(away)).replace("&", "and")
    match["Ground"] = get_ground_name(data_rows, match["Home"])
    updated.append(match)
  write_excel(updated, "results/play-cricket-normalised.xls")

if __name__ == '__main__':
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  main()
