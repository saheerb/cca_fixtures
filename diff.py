# from ortools.sat.python import cp_model
# import shutil
# from test import test_results_indexes
# from test import test_results
import logging
from utils import *

prev = read_excel("2024/results/v4/v2/results.xlsx")
# prev = read_excel("2024/results/v4/v1/play-cricket-normalised.xlsx")
# now = read_excel("2024/results/v3.xlsx")
now = read_excel("2024/results/v4/v2/play-cricket-normalised.xlsx")
results_file = "2024/results/v4/v2/diff.xlsx"
diffs = []
for i in prev:
    if i not in now:
        print (i)
        i["type"] = "Removed"
        diffs.append(i)

for i in now:
    if i not in prev:
        print (i)
        i["type"] = "Added"
        diffs.append(i)

write_excel(diffs, results_file)

##
# # norms = read_data("data.xlsx", "Grounds")
# # results = read_data("./results/backup/data.xlsx", "Grounds")
# # # print (results)
# # diff1 = [item for item in norms if item not in results]
# # diff2 = [item for item in results if item not in norms]
# # # return (len(diff1) + len(diff2))
# # print (diff1)
# # # print (diff1)

# rows_1 = read_data("./tmp/play-cricket-download.xlsx", "Fixtures")
# rows_2 = read_data("/Users/sahbab01/Downloads/download_fixtures (18).xlsx", "Fixtures")

# keys = [
#     "Date",
#     "Home Team",
#     "Away Team",
#     "Division / Cup",
#     # "Ground"
# ]

# norm_1 = []
# for row in rows_1:
#     r = {}
#     for key in keys:
#         r[key] = row[key]
#     norm_1.append(r)

# norm_2 = []
# for row in rows_2:
#     r = {}
#     for key in keys:
#         r[key] = row[key].replace("&amp;", "and")
#     norm_2.append(r)

# diff1 = [item for item in norm_1 if item not in norm_2]
# diff2 = [item for item in norm_2 if item not in norm_1]

# for i in diff1:
#     print(i["Division / Cup"])

# print(len(diff1))
# print(len(diff2))
# print("++++++")
# # for i in diff2:
# #   # if i["Division / Cup"] == "CCA Junior League 5 South":
# #   #   print (i)
# #   print (i["Division / Cup"])
