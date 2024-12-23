from utils import *
# get_all_dates
# get_all_grounds
# find_all_matches
def get_rows_for_the_ground(rows, ground):
    ground_rows = []
    for row in rows:
        if row['Ground'] == ground:
            ground_rows.append(row)
    return ground_rows

def is_ground_available(matches, rows, ground, date):
    ground_rows = get_rows_for_the_ground(rows, ground)
    for match in matches:
        if match["Date"] == date and match["Ground"] == ground:
            return ""
            return "Occupied"
    # if the ground is marked as "No play" "No Home"
    for row in ground_rows:
        if row[date] != "":
            return ""
            return row[date]
    return "Free"

matches = read_excel("2024/results/v3.xlsx")
data_file = "2024/data-v3.xlsx"
rows = read_excel(data_file, "Grounds")
dates = get_all_dates(rows)

grounds = []
for division in get_all_divisions(rows):
    for h in get_all_teams(rows, division):
        for g in get_grounds(rows, h):
            if g not in grounds: grounds.append(g)

ground_maps = []
for ground in sorted(grounds):
    ground_map = {"Ground": ground}
    for date in dates:
        ground_map[date] = is_ground_available(matches, rows, ground, date)
    ground_maps.append(ground_map)

print (ground_maps)
write_excel(ground_maps, "2024/results/grounds.xlsx")
