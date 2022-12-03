from utils import *
import shutil
import subprocess

all_rows = read_data("data.xlsx")
processed_divisions = []

# create an empty partial file
data_file ="data.xlsx"
partial_file = "tmp/result-partial-1.xlsx"
save_result_to_file({},partial_file)
division_file = "tmp/divisions.txt"
status_file = "tmp/result_status.txt"

with open(division_file, "w") as the_file:
  the_file.write("")

with open(status_file, "w") as the_file:
  the_file.write("")

for division in get_all_divisions(all_rows):
  final_file=f"tmp/{division}-1.xlsx"
  # create division file
  with open(division_file, "a") as the_file:
    the_file.write(division+"\n")

  command = f"./solve.py --data-file {data_file} --result-status-file {status_file} --division-file {division_file} --partial-result-file {partial_file} --final-result-file '{final_file}'"
  print (command)

  result = subprocess.Popen(command, shell=True)
  result.wait()

  with open (status_file) as the_file:
    status = the_file.read()

  if status == "0":
    shutil.copyfile(final_file, partial_file)
  else:
    print ("No solution found")
    sys.exit()
