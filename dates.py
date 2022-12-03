from itertools import combinations

teams = [x for x in range(6)]
dates = [x for x in range(10)]

matches = {}
for the_date in dates:
  matches[the_date] = []
  for match in combinations(teams, 2):
    matches[the_date].append({"Home": match[0], "Away": match[1]})
  for match in combinations(teams, 2):
    matches[the_date].append({"Home": match[1], "Away": match[0]})


for the_date in dates:
  if the_date is dates.index(0):
    for match in matches[the_date]:
      print (match)

match_selected =   []
selected_matches = {}
for the_date in matches:
  teams_playing_today =[]
  selected_matches[the_date] = []
  for match in matches[the_date]:
    if match["Home"] in teams_playing_today or match["Away"] in teams_playing_today:
        continue
    if match in match_selected:
      continue
    teams_playing_today.append(match["Home"])
    teams_playing_today.append(match["Away"])
    match_selected.append(match)
    selected_matches[the_date].append(match)

print (len(match_selected))
