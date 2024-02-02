# genereate results from Keith's Games.csv
import csv
from utils import *
input = "2024/Games.csv"
data_file = "2024/data.xlsx"
all_rows = read_data(data_file, "Grounds")

def get_mapped_team(team):
  if team == "Ramsey II":
    return "Ramsey CC, Hunts - 2nd XI"
  elif team == "Bluntisham":
    return "Bluntisham CC - 1st XI"
  elif team == "City of Ely":
    return "City of Ely CC - 1st XI"
  elif team == "Horseheath":
    return "Horseheath CC - 1st XI"
  elif team == "Thriplow":
    return "Thriplow CC - 1st XI"
  elif team == "Wilburton":
    return "Wilburton CC - 1st XI"
  elif team == "Cambourne II":
    return "Cambourne CC - 2nd XI"
  elif team == "Cambridge Old Monks":
    return "Cambridge Old Monks CC - 1st XI"
  elif team == "Cambridge St Giles II":
    return "Cambridge St. Giles CC - 2nd XI"
  elif team == "Milton":
    return "Milton CC, Cambs - 1st XI"
  elif team == "Wilbrahams":
    return "Wilbrahams CC - 1st XI"
  elif team == "Buntingford":
    return "Buntingford CC - 1st XI"
  elif team == "Chesterfords":
    return "Chesterfords CC - 1st XI"
  elif team == "Elmdon":
    return "Elmdon CC - 1st XI"
  elif team == "Ickleton":
    return "Ickleton CC - 1st XI"
  elif team == "Little Shelford":
    return "Little Shelford CC - 1st XI"
  elif team == "Abington":
    return "Abington CC, Cambs - 1st XI"
  elif team == "Fulbourn Institute":
    return "Fulbourn Institute CC - 1st XI"
  elif team == "Longstanton Grasshoppers":
    return "Longstanton Grasshoppers CC - 1st XI"
  elif team == "Wisbech Town II":
    return "Wisbech Town CC - 2nd XI"
  elif team == "Chatteris":
    return "Chatteris CC - 1st XI"
  elif team == "Linton Village":
    return "Linton Village CC - 1st XI"
  elif team == "Saffron Walden III":
    return "Saffron Walden CC - 3rd XI"
  elif team == "Chippenham":
    return "Chippenham CC, Cambs - 1st XI"
  elif team == "Saint Ives & Warboys II":
    return "St Ives Town and Warboys CC - 2nd XI"
  elif team == "TAC":
    return "Telugu Association of Cambridge CC - 1st XI"
  elif team == "Audley End":
    return "Audley End and Littlebury CC - 1st XI"
  elif team == "Cottenham":
    return "Cottenham CC - 1st XI"
  elif team == "March Town II":
    return "March Town CC - 2nd XI"
  elif team == "Madingley":
    return "Madingley CC - 1st XI"
  return team
result_keys =["Division","Division ID",	"Home",	
              "Home Team ID",	"Away",	"Away Team ID",
              "Ground",	"Ground ID",	"Date",	"Time"]   

def team_id(row):
  return row["Team URL"].split("/")[-1]

def ground_id(row):
  return row["Ground URL"].split("/")[-1]

def division_id(row):
  return row["Division"], row["Div URL"].split("/")[-1]

with open(input, newline='') as csvfile:
  results = []
  count = 0
  spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for csv_row in spamreader:
    count +=1
    if count == 1:
      continue

    if csv_row[5] in ["Friendly", "Whitings 1", "Whitings 2", "Whitings 3"]:
      continue

    match_date = csv_row[0]
    home = get_mapped_team(csv_row[2])
    away = get_mapped_team(csv_row[3])
    home_team_row = get_row_for_team(all_rows, home)
    away_team_row = get_row_for_team(all_rows, away) 

    result = {}

    division, div_id = division_id(home_team_row)
    result["Division ID"] = div_id

    result["Home"] = get_mapped_team(csv_row[2])
    result["Home Team ID"] = team_id(home_team_row)

    result["Away"] = get_mapped_team(csv_row[3])
    result["Away Team ID"] = team_id(away_team_row)
    result["Ground"] = home_team_row["Ground"]
    result["Ground ID"] =  ground_id(home_team_row)
    # convert date format
    yyyy, mm, dd = csv_row[0].split("/")
    result["Date"] =  "/".join([dd,mm,yyyy])
    result["Time"] =  csv_row[1]
    results.append(result)
    print (result)
    sys.exit()
  write_excel(results, "2024/partial_results.xlsx")
