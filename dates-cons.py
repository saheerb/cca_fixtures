from ortools.sat.python import cp_model
from utils import *





def main():
  rows = read_data("data.xlsx")
  dates =  get_all_dates(rows)
  for i in window(dates, 3):
    print (i)

if __name__ == '__main__':
    main()

# for team in get_all_teams():
  

