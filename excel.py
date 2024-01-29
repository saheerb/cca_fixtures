import logging
import pylightxl as xl
import html

def read_data(book, sheet="Fixtures"):
  db = xl.readxl(book)
  ws = db.ws(sheet)
  # get column
  row_nbr = 1
  col_nbr = 1
  header = {}
  rows = []
  while True:
    value = ws.index(row_nbr, col_nbr)
    if value == "":
      break
    header[value]=col_nbr
    col_nbr += 1

  while True:
    row = {}
    row_nbr += 1
    # if row's 1st colum is empty quite
    if ws.index(row_nbr, 1) == "":
      break
    for i in header:
      value = ws.index(row_nbr, header[i])
      row[i] = html.escape(str(value))
    rows.append(row)
  return rows

def save_result_to_file(matches, file_name="temp_single.xlsx", ws="Fixtures"):
  db = xl.Database()  
  db.add_ws(ws=ws)
  row_nbr = 1

  # Header row in rows:
  for match in matches:
    col_nbr = 1
    for key in match:
      db.ws(ws=ws).update_index(row=row_nbr, col=col_nbr, val=key)
      col_nbr += 1 
    break
  for match in matches:
    col_nbr = 1
    row_nbr += 1
    for value in match.values():
      value = html.unescape(str(value))
      value = str(value).replace("&", "and")
      db.ws(ws=ws).update_index(row=row_nbr, col=col_nbr, val=value)
      col_nbr += 1  
  xl.writexl(db=db, fn=file_name)
