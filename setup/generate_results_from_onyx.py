# genereate results from Keith's Games.csv
import csv
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from utils import *
from excel import *
in_file = "2026/results/Onyx.csv"
out_file = "2026/results/onyx_out.xlsx"
data_file = "2026/workspace/data.xlsx"
all_rows = read_excel(data_file, "Grounds")


def get_mapped_team(team):
    # print ("mpa_in:" + team)
    if team == "Biggleswade Town":
        team = "Biggleswade CC - 1st XI"
    elif team == "Barnack":
        team = "Barnack CC - 1st XI"
    elif team == "Cambourne":
        team = "Cambourne CC - 1st XI"
    elif team == "Cambridge Saint Giles":
        team = "Cambridge St. Giles CC - 1st XI"
    elif team == "Cambridge NCI":
        team = "Cambridge NCI CC - 1st XI"
    elif team == "Elstow":
        team = "Elstow CC - 1st XI"
    elif team == "Newmarket":
        team = "Newmarket CC - 1st XI"
    elif team == "Old Leysians":
        team = "Old Leysians CC - 1st XI"
    elif team == "Godmanchester Town":
        team = "Godmanchester Town CC - 1st XI"
    elif team == "Histon":
        team = "Histon CC - 1st XI"
    elif team == "Saint Ives & Warboys":
        team = "St Ives Town and Warboys CC - 1st XI"
    elif team == "Foxton Granta":
        team = "Foxton Granta CC - 1st XI"
    elif team == "Burwell & Exning":
        team = "Burwell and Exning CC - 1st XI"
    elif team == "Kimbolton":
        team = "Kimbolton CC - 1st XI"
    elif team == "Blunham":
        team = "Blunham CC - 1st XI"
    elif team == "Eaton Socon":
        team = "Eaton Socon CC - 1st XI"
    elif team == "Saffron Walden":
        team = "Saffron Walden CC - 1st XI"
    elif team == "Southill Park":
        team = "Southill Park CC - 1st XI"
    elif team == "Southill Park":
        team = "Southill Park CC - 1st XI"
    elif team == "Waresley":
        team = "Waresley CC - 1st XI"
    elif team == "Upwood":
        team = "Upwood CC - 1st XI"
    elif team == "Wisbech Town":
        team = "Wisbech Town CC - 1st XI"
    elif team == "Sawston & Babraham II":
        team = "Sawston and Babraham CC - 2nd XI"
    elif team == "City of Ely":
        team = "City of Ely CC - 1st XI"
    elif team == "Cambridge Old Monks":
        team = "Cambridge Old Monks CC - 1st XI"
    elif team == "Saffron Walden II":
        team = "Saffron Walden CC - 2nd XI"
    elif team == "LGR":
        team = "LGR XI CC - 1st XI"
    elif team == "Foxton Granta II":
        team = "Foxton Granta CC - 2nd XI"
    elif team == "Eaton Socon II":
        team = "Eaton Socon CC - 2nd XI"
    elif team == "Stamford Town":
        team = "Stamford Town CC, Lincs - 1st XI"
    elif team == "March Town":
        team = "March Town CC - 1st XI"
    # print ("mpa_out:" + team)
    return team


result_keys = [
    "Division",
    "Division ID",
    "Home",
    "Home Team ID",
    "Away",
    "Away Team ID",
    "Ground",
    "Ground ID",
    "Date",
    "Time",
]


def team_id(row):
    return row["Team URL"].split("/")[-1]


def ground_id(row):
    return row["Ground URL"].split("/")[-1]


def division_id(row):
    return row["Division"], row["Div URL"].split("/")[-1]


with open(in_file, newline="") as csvfile:
    results = []
    count = 0
    spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
    # print (spamreader)
    for csv_row in spamreader:

        count += 1
        if count == 1:
            continue

        csv_row = [_.strip('"') for _ in csv_row]

        # print (csv_row)
        if csv_row[5] not in ['Onyx 1', 'Onyx 2', 'Onyx 3']:
            continue

        match_date = csv_row[0]
        home = get_mapped_team(csv_row[2])
        away = get_mapped_team(csv_row[3])
        # print ("Home: " + home)
        # print ("AWAY: " + away)
        home_team_row = get_row_for_team(all_rows, home)
        # print ("Home_team_row: %s" % home_team_row)
        away_team_row = get_row_for_team(all_rows, away)
        # print ("away_team_row: %s" % away_team_row)

        result = {}

        division, div_id = division_id(home_team_row)

        # print (division)
        result["Division"] = division
        result["Division ID"] = div_id

        result["Home"] = get_mapped_team(csv_row[2])
        result["Home Team ID"] = team_id(home_team_row)

        result["Away"] = get_mapped_team(csv_row[3])
        # print (result["Away"])
        result["Away Team ID"] = team_id(away_team_row)
        result["Ground"] = home_team_row["Ground"]
        result["Ground ID"] = ground_id(home_team_row)
        # convert date format
        yyyy, mm, dd = csv_row[0].split("/")
        result["Date"] = "/".join([dd, mm, yyyy])
        result["Time"] = csv_row[1]
        results.append(result)
    write_excel(results, out_file)
