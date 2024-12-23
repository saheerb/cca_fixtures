from ortools.sat.python import cp_model
import os
import inspect
import sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from utils import *
import shutil
from test import test_results_indexes
from test import test_results
import logging

def team_id(row):
    return row["Team URL"].split("/")[-1]


def ground_id(home_team_row, ground):
    if home_team_row["Ground"].strip() == ground.strip():
        return home_team_row["Ground URL"].split("/")[-1]
    else:
        return ""


def division_id(data_rows, div_id):
    for row in data_rows:
        if row['Division'] == div_id:
            return row["Div URL"].split("/")[-1]

def get_ground(home, home_team_row, match):
    if home == "Bassingbourn CC - 1st XI" and match["Ground"] == "Recreation Ground":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    if home == "Bassingbourn CC - 2nd XI" and match["Ground"] == "Recreation Ground":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "St Ives Town and Warboys CC - 3rd XI" and match["Ground"] == "Warboys Sports Field":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "St Ives Town and Warboys CC - 2nd XI" and match["Ground"] == "One Leisure Outdoor Centre":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Wisbech Town CC - 3rd XI" and match["Ground"] == "Wisbech Town CC":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Wisbech Town CC - 4th XI" and match["Ground"] == "Wisbech Town CC":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Northstowe CC - 1st XI" and match["Ground"].strip() == "THE CLUB HOUSE":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Over and Willingham CC - 1st XI" and match["Ground"].strip() == "The Pavilion (Over Green)":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Over and Willingham CC - 2nd XI" and match["Ground"].strip() == "Willingham Recreation Ground":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Ramsey CC, Hunts - 3rd XI" and match["Ground"].strip() == "Abbey College":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Thriplow CC - 1st XI" and match["Ground"].strip() == "Cricket Meadow   SG8 7QU":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Haslingfield CC - 1st XI" and match["Ground"].strip() == "The Recreation Ground":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Burwell and Exning CC - 3rd XI" and match["Ground"].strip() == "Mingay Park":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Fen Ditton CC - 1st XI" and match["Ground"].strip() == "Recreation Ground":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Linton Village CC - 1st XI" and match["Ground"].strip() == "Recreation Ground":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    elif home == "Linton Village CC - 2nd XI" and match["Ground"].strip() == "Recreation Ground":
        return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    # elif home == "Wilbrahams CC - 1st XI" and match["Ground"].strip() == "Wilbraham Recreation Ground CB21 5JG":
    #     return home_team_row["Ground"], home_team_row["Ground URL"].split("/")[-1]
    else:
        return match["Ground"].strip(), ground_id(home_team_row, match["Ground"])

def main():
    data_rows = read_excel("2024/results/v4/v2/data.xlsx", "Grounds")
    play_cricket_data = "2024/results/v4/v2/download_fixtures.xlsx"
    result_file = "2024/results/v4/v2/play-cricket-normalised.xlsx"
    original_matches = read_excel(play_cricket_data)
    results = []
    for match in original_matches:
        result= {}
        print(match)

        division = match["Division / Cup"]
        match["Division"] = division
        home = str(html.unescape(match["Home Team"])).replace("&", "and")
        away = str(html.unescape(match["Away Team"])).replace("&", "and")
        # updated.append(match)
        print (home)
        home_team_row = get_row_for_team(data_rows, home)
        print (home_team_row)
        away_team_row = get_row_for_team(data_rows, away)

        result = {}

        result["Division"] = division
        result["Division ID"] = division_id(data_rows, division)

        result["Home"] = str(html.unescape(home)).replace("&", "and")
        result["Home Team ID"] = team_id(home_team_row)

        result["Away"] = str(html.unescape(away)).replace("&", "and")
        result["Away Team ID"] = team_id(away_team_row)
        result["Ground"], result["Ground ID"] = get_ground(result["Home"], home_team_row, match)
        # convert date format
        # yyyy, mm, dd = csv_row[0].split("/")
        result["Date"] = match["Date"]
        result["Time"] = match["Start Time"]
        results.append(result)

    write_excel(results, result_file)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
