import json
from utils import *

with open("2024/data.json", 'r') as f:
  rows = json.load(f)

with open("2024/results.json", 'r') as f:
  results = json.load(f)

def get_all_matches(team_name, results, type="Home"):
  matches = []
  for a_result in results:
    if type == "Home" and a_result[1] == team_name:
      matches.append(a_result)
    if type == "Away" and a_result[2] == team_name:
      matches.append(a_result)
  matches = sorted(matches, key=lambda d: len(d[3]))
  return matches

# for division in get_all_divisions(rows):
#   for h in get_all_teams(rows, division):
#     for o in get_all_teams(rows, division):
#       for g in get_grounds(rows, h):
#         for d in get_all_dates(rows):
#           print (g,h,o,d)
def get_gap(home_team, away_team, matches):
  matched = []
  for match in matches:
    if (match[1] == home_team and match[2] == away_team) or\
        (match[2] == home_team and match[1] == away_team):
        matched.append(match)
  match_date = datetime.strptime(matched[0][3], "%d/%m/%Y")
  prev_match_date = datetime.strptime(matched[1][3], "%d/%m/%Y")
  difference = abs((match_date - prev_match_date).days)
  return difference/7


def get_max_consecutive(team, type="Home"):
  # matches are ordered by date
  matches = get_all_matches(team, results, type)
  max_consecutive = 0
  prev_match = None
  consecutive = 1
  for match in matches:
    if prev_match == None:
      consecutive = 1
    else:
      match_date = datetime.strptime(match[3], "%d/%m/%Y")
      prev_match_date = datetime.strptime(prev_match[3], "%d/%m/%Y")
      difference = abs((match_date - prev_match_date).days)
      if difference <= 7:
        consecutive += 1
      else:
        consecutive = 1
    if consecutive > max_consecutive:
      max_consecutive = consecutive
    prev_match = match
  return max_consecutive

dates = get_all_dates(rows)
for division in get_all_divisions(rows):
  print (division)
  result_metas = []
  for home_team in get_all_teams(rows, division):
    row = get_row_for_team(rows, home_team)
    row["home_cons"]=get_max_consecutive(home_team, "Home")
    row["away_cons"]=get_max_consecutive(home_team, "Away")
    meta = {}
    for away_team in get_all_teams(rows, division):
      meta ["1home_team"] = home_team
      if home_team == away_team:
        meta[home_team] = "-"
        continue
      meta[away_team] = get_gap(home_team, away_team, results)
    result_metas.append(meta)
    fn = division.replace(' ','')
  sorted_metas = []
  for meta in result_metas:
    sorted_metas.append(dict(sorted(meta.items())))
  save_result_to_file(sorted_metas, f"tmp/1{fn}.xlsx", division)
  sys.exit()
