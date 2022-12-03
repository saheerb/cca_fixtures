import pylightxl as xl
import json
from datetime import datetime, timedelta
from collections import OrderedDict
import re
import sys
import random
from itertools import combinations

# find teams with max contraints
# resolve the constraints
# if there are multiple ways to solve it, add a check point to return to it

def read_data(book):
  db = xl.readxl(book)
  ws = db.ws('Grounds')
  # get column
  row_nbr = 1
  col_nbr = 1
  header = OrderedDict()
  rows = []
  while True:
    value = ws.index(row_nbr, col_nbr)
    if value == "":
      break
    header[value]=col_nbr
    col_nbr += 1

  # For each row
  while True:
    row = OrderedDict()
    row_nbr += 1
    if ws.index(row_nbr, header["Division"]) == "":
      break
    for i in header:
      row[i] = ws.index(row_nbr, header[i])
    rows.append(row)
  return rows

def read_match(book):
  db = xl.readxl(book)
  ws = db.ws('Matches')
  # get column
  row_nbr = 1
  col_nbr = 1
  header = OrderedDict()
  rows = []
  while True:
    value = ws.index(row_nbr, col_nbr)
    if value == "":
      break
    header[value]=col_nbr
    col_nbr += 1

  # For each row
  while True:
    row = OrderedDict()
    row_nbr += 1
    if ws.index(row_nbr, header["Away"]) == "":
      break
    for i in header:
      row[i] = ws.index(row_nbr, header[i])
    rows.append(row)
  return rows

rows = read_data("fix_.xlsx") 
matches = read_data("temp_out.xlsx")

for match in matches:
  print (match)


# test if all matches are created
# test if all matches are allocated
# test number of matches for a team - home, away
# test team "No Play" is satisfied
# test ground "No Home" is satisfied
# test ground "Home" is satisfied