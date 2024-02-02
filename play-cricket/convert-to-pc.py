from ortools.sat.python import cp_model
from utils import *
import shutil
from test import test_results_indexes
from test import test_results
import logging

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

def main():
  play_cricket_upload_format("2024/result.xlsx", "2024/play-cricket-upload.xlsx")

if __name__ == '__main__':
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  main()
