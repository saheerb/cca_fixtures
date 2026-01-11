# What is it
This automates CCA fixture management. 

# Running the program
## install necessary requirements
`pip install -r requirements.txt`

## steps
- Create data.xlsx, which stores constraints
  - python setup/get_play_cricket_data.py
  - python setup/generate_data_excel.py
- Generate partial result from Onyx.
  - python setup/generate_data_excel.py
- Manually fill in the constraints in data.xlsx
  - This is the most boring and tedious part. Go through the CCA forms and add No Home, No Play etc
    for each Date entry
  - Check Grounds
  - There may be also tweaks needed as program has some limitations (like ground status NO_HOME, NO_PLAY etc are shared between alternative and primary grounds). Consecutive matches, need to be manually tuned.
- Manually update the get_halves return values
  - The values need to be setup such a way that there are a few vacant weeks between two halves
- Run the fixture
  


## Making the input data
* Once division is grouped run `get_data.py`, this basically fetches the divisions and team information and store in `data.json`
* Run `get_data.py`, this will create `data.xlsx`
* Check sanity on `data.xlsx`
  * Some entries in `data.xlsx` is not correct, ground may be wrong. Team number may be wrong in play-cricket. Verify this.
* Remove `&` character, for some reason `&` didn't seem to working while finding solution.

## Add constraints needed to input data
Each date for a team can have
* No Home
* Home
* No Play/ Off Request - There is no difference between these two fields. Except, while solution is not found, you can manually delete "Off Request" for helping program to find a solution.

Create necessary "drop down list" in data.xlsx and fill in the constraints

## Check sanity of data
* Read `rules.txt` and see if the input data is solvable.

## Run the program

`python fixture.py`

Result is generate in `results/` folder.


# How does it work
This is a constraint program using Google OR tools. 


Solving all the constraint for all the matches didn't work (probably it will take days to solve). So, solving a Division first and then keeping that solution, solving the next division and so on.

If a solution cannot be found, restarting the attempt from beginning in hope to find a solution.

In a nutshell
* Get valid states
* Add constraints
* Find solutions for one division after another as given above. 

# Future Ideas
## Solve constraints first 
Current final solution is done by solving division after division. This at times is not giving "best" solution. Solve teams with "constraints" first and move on to next team.

## Solve remaining matches
During course of the season, fixture may need to be regenerated. So, load all "must fixture"
and solve rest

## Run this program from Gooogle colab
Read data from Google drive, run from Google colab and store result in Google colab

## Add UI/Web
Add proper user interface


#  Limitations
* CK3 case - CK3 wants to share two grounds, which is not currently possible. 
* Consecutive matches - Not working perfectly
