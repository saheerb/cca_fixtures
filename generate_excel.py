import pylightxl as xl
import json
from datetime import datetime, timedelta

with open('data.json', 'r') as f:
  data_list = json.load(f)

db = xl.Database()
db.add_ws(ws="Grounds")

def add_dates(start_col=8, start_date = '22/04/2023', end_date = "20/10/2023"):
  end = datetime.strptime(end_date, '%d/%m/%Y')
  d = datetime.strptime(start_date, '%d/%m/%Y')
  col = start_col
  while end > d:
    d = d + timedelta(days=7)
    this_date = d.strftime("%d/%m/%Y")
    db.ws(ws="Grounds").update_index(row=1, col=col, val=this_date)
    col += 1
    


row_count= 1
for data in data_list:
  db.ws(ws="Grounds").update_index(row=row_count, col=1, val="Division")
  db.ws(ws="Grounds").update_index(row=row_count, col=2, val="Div URL")
  db.ws(ws="Grounds").update_index(row=row_count, col=3, val="Club")
  db.ws(ws="Grounds").update_index(row=row_count, col=4, val="Team")
  db.ws(ws="Grounds").update_index(row=row_count, col=5, val="Team URL")
  db.ws(ws="Grounds").update_index(row=row_count, col=6, val="Ground")
  db.ws(ws="Grounds").update_index(row=row_count, col=7, val="Ground URL")

add_dates(start_col=8)

for data in data_list:
  row_count += 1
  db.ws(ws="Grounds").update_index(row=row_count, col=1, val=data["div_name"])
  db.ws(ws="Grounds").update_index(row=row_count, col=2, val=data["div_url"])
  db.ws(ws="Grounds").update_index(row=row_count, col=3, val=data["club_name"])
  db.ws(ws="Grounds").update_index(row=row_count, col=4, val=data["team_name"])
  db.ws(ws="Grounds").update_index(row=row_count, col=5, val=data["team_url"])
  db.ws(ws="Grounds").update_index(row=row_count, col=6, val=data["ground_name"])
  db.ws(ws="Grounds").update_index(row=row_count, col=7, val=data["ground_url"])
xl.writexl(db=db, fn="output.xlsx")