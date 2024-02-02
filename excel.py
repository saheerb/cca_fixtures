import logging
import pylightxl as xl
import html
import sys


def _read(db, ws):
    ws = db.ws(ws)
    # get column
    row_nbr = 1
    col_nbr = 1
    header = {}
    rows = []
    while True:
        value = ws.index(row_nbr, col_nbr)
        if value == "":
            break
        header[value] = col_nbr
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


def read_excel(book, ws="Fixtures"):
    db = xl.readxl(book)
    return _read(db, ws)


# def update_excel(rows, file_name, ws):
#   db = xl.Database()
#   db = xl.readxl(file_name)
#   db.add_ws(ws="test")
#   # loop to add our data to the worksheet
#   for row_id, data in enumerate(rows, start=1):
#     db.ws(ws="test").update_index(row=row_id, col=1, val=data)

#   xl.writexl(db=db, fn="output.xlsx")


def _write(db, rows, ws):
    # Header row in rows:
    row_nbr = 1
    for row in rows:
        col_nbr = 1
        for key in row:
            db.ws(ws=ws).update_index(row=row_nbr, col=col_nbr, val=key)
            col_nbr += 1
        break
    for row in rows:
        col_nbr = 1
        row_nbr += 1
        for value in row.values():
            value = html.unescape(str(value))
            value = str(value).replace("&", "and")
            db.ws(ws=ws).update_index(row=row_nbr, col=col_nbr, val=value)
            col_nbr += 1


def update_excel(filename, ws="Fixtures", sheets_dict=[]):
    db = xl.readxl(filename)
    result = _read(db, ws)
    db = xl.Database()
    db.add_ws(ws=ws)
    _write(db, result, ws)
    for key in sheets_dict:
        db.add_ws(ws=key)
        _write(db, sheets_dict[key], key)
    xl.writexl(db=db, fn=filename)


def write_excel(matches, file_name, ws="Fixtures"):
    db = xl.Database()
    db.add_ws(ws=ws)
    _write(db, matches, ws)
    xl.writexl(db=db, fn=file_name)
