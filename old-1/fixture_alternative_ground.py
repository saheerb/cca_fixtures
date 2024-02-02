from ortools.sat.python import cp_model
from utils import *
import shutil
from test import test_results_indexes
from test import test_results
import logging

global_solution_cnt = 0


def write_excel(results, result_file, rows, num):
    matches = []
    # Division ID	Match Date	Time	Home Team ID	Away Team ID	Ground ID	Ground Name
    for result in results:
        ground = result[0]
        home_team = result[1]
        away_team = result[2]
        the_date = result[3]
        home_team_id = get_team_id(rows, home_team)
        away_team_id = get_team_id(rows, away_team)
        ground_id = get_ground_id(rows, home_team)
        division, div_id = get_division(rows, home_team)
        yyy, mm, dd = the_date.split("/")
        matches.append(
            {
                "Division": division,
                "Division ID": div_id,
                "Home": home_team,
                "Home Team ID": home_team_id,
                "Away": away_team,
                "Away Team ID": away_team_id,
                "Ground": ground,
                "Ground ID": ground_id,
                # "Match Date": "%s/%s/%s" % (dd, mm, yyy), "Time": "13:00"})
                "Date": the_date,
                "Time": "13:00",
            }
        )
    extension = result_file.split(".")[-1]
    result_path = result_file.split(".")[:-1][0]
    logging.info(result_path)
    logging.info(extension)
    logging.info(num)
    logging.info(f"{result_path}_{num}.{extension}")
    save_result_to_file(matches, f"{result_path}_{num}.{extension}")

    pass


def remove_invalids(results):
    valid_results = []
    bValid = True
    # is ground on the date played by two teams?
    for the_result in results:
        for a_result in results:
            if the_result == a_result:
                continue
            if the_result["Ground"] == a_result["Ground"]:
                if the_result["Date"] == a_result["Date"]:
                    bValid = False
                    break
        if bValid:
            valid_results.append(the_result)

    logging.debug(len(valid_results))
    import time

    time.sleep(60)

    # no two teams playing on same date
    # for the_result in results:
    #   for a_result in results:
    #     if the_result == a_result:
    #       continue
    #     if the_result["Home"] == a_result["Home"] and the_result["Away"] == a_result["Away"]:
    #       assert False


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(
        self, rows, result_file, valid_states, matches, grounds, teams, dates, limit
    ):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._result_file = result_file
        self._rows = rows
        self._valid_states = valid_states
        self._matches = matches
        self._teams = teams
        self._dates = dates
        self._grounds = grounds
        self._solution_count = 0
        self._solution_limit = limit

    def on_solution_callback(self):
        self._solution_count += 1
        print("Solution found")
        # return

        match_count = 0
        result = []
        for state in self._valid_states:
            g = state[0]
            h = state[1]
            o = state[2]
            d = state[3]
            if self.Value(self._matches[(g, h, o, d)]):
                match_count += 1
                result.append([g, h, o, d])
                # print(f'Team-{h} playing against Team-{o} on {d} at {g}')
        global global_solution_cnt
        global_solution_cnt += 1
        logging.info("Match Count: %i" % match_count)
        logging.info(f"Global Solution Count: {global_solution_cnt}")
        # diff_count = diff_count(result)
        # if diff_count(result) < min_diff_count:
        #   min_diff_count = diff_count
        write_excel(result, self._result_file, self._rows, global_solution_cnt)
        test_results_indexes(self._rows, result)
        if self._solution_count >= self._solution_limit:
            logging.debug("Stop search after %i solutions" % self._solution_limit)
            self.StopSearch()

    def solution_count(self):
        return self._solution_count


# def get_valid_states(rows):
#   states = []
#   for row in rows:
#     ground = row["Ground"]
#     division = row["Division"]
#     home_team = team_name(row)
#     for the_date in get_all_dates(rows):
#       if row[the_date] in ["No Home", "No Play", "Off Request"]:
#         continue
#       for opposition in get_all_teams(rows, division):
#         is_valid = True
#         oppositions_row = get_row_for_team(rows,opposition)
#         if oppositions_row[the_date] in ["No Play", "Off Request"]:
#           continue
#         if opposition == home_team:
#            continue
#         states.append([ground, home_team, opposition, the_date])
#   return states


def get_valid_states(rows, partial_results):
    must_states = get_must_have_states(rows, partial_results)
    states = []
    for row in rows:
        ground = row["Ground"]
        division = row["Division"]
        home_team = team_name(row)
        for the_date in get_all_dates(rows):
            if row[the_date] in ["No Home", "No Play", "Off Request"]:
                continue
            for opposition in get_all_teams(rows, division):
                is_valid = True
                oppositions_row = get_row_for_team(rows, opposition)
                if oppositions_row[the_date] in ["No Play", "Off Request"]:
                    continue
                if opposition == home_team:
                    continue
                # some teams may have more than one home ground
                for the_ground in get_grounds(rows, home_team):
                    # if this home vs opposition combo in any of the must_states
                    # take only state which matches the date
                    for must_state in must_states:
                        if must_state[1] == home_team:
                            if (
                                must_state[2] == opposition
                                and must_state[3] == the_date
                                and must_state[0] == the_ground
                            ):
                                is_valid = True
                                break
                            else:
                                is_valid = False
                    if is_valid:
                        states.append([the_ground, home_team, opposition, the_date])
    return states


def must_home_matches(rows):
    states = []
    # must  - Home
    for row in rows:
        ground = row["Ground"]
        home_team = team_name(row)
        division = row["Division"]
        states_for_oppositions = []
        for the_date in get_all_dates(rows):
            if row[the_date] not in ["Home"]:
                continue
            for opposition in get_all_teams(rows, division):
                if opposition == home_team:
                    continue
                states_for_oppositions.append([ground, home_team, opposition, the_date])
        if states_for_oppositions != []:
            states.append(states_for_oppositions)
    return states


def get_must_have_states(rows, partial_results):
    states = []
    for match in partial_results:
        states.append([match["Ground"], match["Home"], match["Away"], match["Date"]])
    return states


def must_constraint(model, rows, matches, partial_results):
    must_states = get_must_have_states(rows, partial_results)
    for state in must_states:
        g, h, o, d = state[0], state[1], state[2], state[3]
        model.AddExactlyOne(matches[g, h, o, d])


def make_variables(model, valid_states):
    matches = {}
    for state in valid_states:
        g, h, o, d = state[0], state[1], state[2], state[3]
        matches[g, h, o, d] = model.NewBoolVar(f"match_g{g}_h{h}_o{o}d_{d}")
    return matches


def set_consecutive_date_constraint(model, rows, valid_states, matches):
    all_dates = get_all_dates(rows)
    for division in get_all_divisions(rows):
        for team in get_all_teams(rows, division):
            team_row = get_row_for_team(rows, team)
            states = {}
            for state in valid_states:
                g, h, o, d = state[0], state[1], state[2], state[3]
                if team != h:
                    continue
                # get maximum consecutive for this team
                # add 1 because we are building windows that are not allowed
                for a_window in window(all_dates, int(team_row["Max Consecutive"]) + 1):
                    if d in a_window:
                        window_id = get_text(a_window)
                        try:
                            states[window_id].append(matches[g, h, o, d])
                        except:
                            states[window_id] = []
                            states[window_id].append(matches[g, h, o, d])

            for state in states.values():
                model.Add(sum(state) <= int(team_row["Max Consecutive"]))


def number_of_matches_constraint(model, rows, valid_states, matches):
    for division in get_all_divisions(rows):
        num_home_matches = len(get_all_teams(rows, division)) - 1
        num_all_matches = num_home_matches * 2
        num_away_matches = num_home_matches
        for team in get_all_teams(rows, division):
            home_team_states = []
            away_team_states = []
            home_way_team_states = []
            for a_state in valid_states:
                g, h, o, d = a_state[0], a_state[1], a_state[2], a_state[3]
                if team == h:
                    home_team_states.append(matches[g, h, o, d])
                    home_way_team_states.append(matches[g, h, o, d])
                if team == o:
                    away_team_states.append(matches[g, h, o, d])
                    home_way_team_states.append(matches[g, h, o, d])
            model.Add(sum(home_team_states) == num_home_matches)
            model.Add(sum(away_team_states) == num_away_matches)
            model.Add(sum(home_way_team_states) == num_all_matches)


def must_home_match_constraint(model, rows, valid_states, matches):
    # Home condition
    for states in must_home_matches(rows):
        constraints = []
        for a_state in states:
            if a_state not in valid_states:
                # print (a_state)
                # While partial results are processed,
                # invalid "Home" match entries are also removed
                # That's why we are here
                continue
                # assert False

            g, h, o, d = a_state[0], a_state[1], a_state[2], a_state[3]
            # print (f"{g}_{h}_{o}_{d}")
            constraints.append(matches[g, h, o, d])
        model.AddExactlyOne(constraints)


def teams_on_a_day_constraint(model, rows, valid_states, matches):
    # team plays atmost one match in a day
    # regardless of ground or opposition
    logging.debug("setting constraints home-opposition constraint")
    constraints = {}
    for state in valid_states:
        g, h, o, d = state[0], state[1], state[2], state[3]
        try:
            constraints[f"{h}_{d}"].append(matches[g, h, o, d])
        except KeyError:
            constraints[f"{h}_{d}"] = []
            constraints[f"{h}_{d}"].append(matches[g, h, o, d])

        try:
            constraints[f"{o}_{d}"].append(matches[g, h, o, d])
        except KeyError:
            constraints[f"{o}_{d}"] = []
            constraints[f"{o}_{d}"].append(matches[g, h, o, d])

    for constraint in constraints.values():
        model.AddAtMostOne(constraint)


def ground_constraint(model, rows, valid_states, matches):
    logging.debug("setting ground constraint")
    constraints = {}
    for state in valid_states:
        g, h, o, d = state[0], state[1], state[2], state[3]
        try:
            constraints[f"{g}_{d}"].append(matches[g, h, o, d])
        except KeyError:
            constraints[f"{g}_{d}"] = []
            constraints[f"{g}_{d}"].append(matches[g, h, o, d])
    for constraint in constraints.values():
        model.AddAtMostOne(constraint)


def add_consecutive_matches(
    rows, results, out_file="results/data_with_consecutive.xlsx"
):
    dates = get_all_dates(rows)

    for team in get_all_teams(rows):
        # matches are ordered by date
        matches = get_all_matches(team, results, type="Home")
        max_consecutive = 0
        prev_match = None
        consecutive = 1
        for match in matches:
            if prev_match == None:
                consecutive = 1
            else:
                match_date = datetime.strptime(match["Date"], "%Y/%m/%d")
                prev_match_date = datetime.strptime(prev_match["Date"], "%Y/%m/%d")
                difference = abs((match_date - prev_match_date).days)
                if difference <= 7:
                    consecutive += 1
                else:
                    consecutive = 1
            if consecutive > max_consecutive:
                max_consecutive = consecutive
            prev_match = match
        team_row = get_row_for_team(rows, team)
        team_row["max_consecutive"] = max_consecutive
    save_result_to_file(rows, out_file)


def build_from_partial_result(data_rows, partial_results):
    result_file = f"tmp/re1.xlsx"
    # print (len(partial_results))
    # print (len(partial_results))
    # test_results(data_rows, partial_results)
    # sys.exit()
    if process(data_rows, result_file, partial_results) == 0:
        print(f"No solution found")
    else:
        results = read_data("tmp/re1_1.xlsx")
        add_consecutive_matches(data_rows, results, "tmp/re-with-cons.xlsx")
        play_cricket_format("tmp/re1_1.xlsx", "tmp/play-cricket.xlsx")
    # test_result

    pass


def diff_count(org, the_result):
    norms = []
    results_1 = read_data(org)
    for i in org:
        norm = {}
        norm["Division"] = i["Division"]
        norm["Home"] = i["Home"]
        norm["Away"] = i["Away"]
        norm["Ground"] = i["Ground"]
        norm["Date"] = i["Date"]
        norms.append(norm)
    results = []
    for i in the_result:
        norm = {}
        norm["Division"] = i["Division"]
        norm["Home"] = i["Home"]
        norm["Away"] = i["Away"]
        norm["Ground"] = i["Ground"]
        norm["Date"] = i["Date"]
        results.append(norm)

    diff1 = [item for item in norms if item not in results]
    diff2 = [item for item in results if item not in norms]
    return len(diff1) + len(diff2)


def diff(org, result):
    results_1 = read_data(org)
    norms = []
    for i in results_1:
        norm = {}
        norm["Division"] = i["Division"]
        norm["Home"] = i["Home"]
        norm["Away"] = i["Away"]
        norm["Ground"] = i["Ground"]
        norm["Date"] = i["Date"]
        norms.append(norm)

    results_2 = read_data(result)
    results = []
    for i in results_2:
        norm = {}
        norm["Division"] = i["Division"]
        norm["Home"] = i["Home"]
        norm["Away"] = i["Away"]
        norm["Ground"] = i["Ground"]
        norm["Date"] = i["Date"]
        results.append(norm)

    diff1 = [item for item in norms if item not in results]
    diff2 = [item for item in results if item not in norms]
    return len(diff1) + len(diff2)


def main():
    # diff()
    # sys.exit()
    partial_file = "results/play-cricket-normalised-updated.xlsx"
    partial_file = "results/play-cricket-normalised.xlsx"
    data_file = "data.xlsx"
    all_rows = read_data(data_file, "Grounds")
    partial_results = read_data(partial_file, "Fixtures")
    # for _ in partial_results:
    #   print (_)
    build_from_partial_result(all_rows, partial_results)

    # diff()
    exit()

    # if process(all_rows, "results/result-partial.xlsx", []) == 0:
    #   print(f"No solution for {division}")
    # sys.exit()
    attempt = 1
    while True:
        processed_divisions = []
        # create an empty partial file
        partial_file = "results/result-partial.xlsx"
        save_result_to_file({}, partial_file)
        solution_found = False
        print(f"Attempt: {attempt}")
        for division in get_all_divisions(all_rows):
            print(f"Solving: {division}")
            partial_results = read_data(partial_file)
            if division not in processed_divisions:
                processed_divisions.append(division)
            rows = []
            for row in all_rows:
                if row["Division"] in processed_divisions:
                    result_file = f"tmp/{division}.xlsx"
                    rows.append(row)

            if process(rows, result_file, partial_results) == 0:
                print(f"No solution for {division}")
                # start from beginning
                attempt += 1
                solution_found = False
                break
            else:
                solution_found = True
                shutil.copyfile(result_file, partial_file)
                # copy result_file to partial_file
        if solution_found == True:
            break
        elif attempt > 100:
            print(f"No solution found in {attempt} attempts")
            sys.exit()

    shutil.copyfile(partial_file, "results/result.xlsx")
    results = read_data("results/result.xlsx")
    add_consecutive_matches(rows, results)
    play_cricket_format("results/result.xlsx", "results/play-cricket.xlsx")


def play_cricket_format(
    in_file="results/result.xlsx", out_file="results/play-cricket.xlsx"
):
    results = read_data(in_file)
    result_with_date = []
    keys = [
        "Division ID",
        "Match Date",
        "Time",
        "Home Team ID",
        "Away Team ID",
        "Ground ID",
        "Ground Name",
        "Umpire 1 ID",
        "Umpire 2 ID",
        "Umpire 3 ID",
        "Match Ref ID",
        "External Match ID",
    ]

    for result in results:
        r = {}
        for key in keys:
            if key == "Match Date":
                yyyy, mm, dd = result["Date"].split("/")
                r[key] = "%s/%s/%s" % (dd, mm, yyyy)
            elif key == "Ground Name":
                if result["Ground ID"] != "":
                    r[key] = ""
                else:
                    r[key] = result["Ground"]
            elif key not in result.keys():
                r[key] = ""
            else:
                r[key] = result[key]
        result_with_date.append(r)
    save_result_to_file(result_with_date, out_file)


def home_opposition_constraint(model, valid_states, matches):
    logging.debug("setting constraints home-opposition constraint")
    # all teams play exactly one match against all oppositions
    # regardless of ground or days
    constraints = {}
    for state in valid_states:
        g, h, o, d = state[0], state[1], state[2], state[3]
        try:
            constraints[f"{h}_{o}"].append(matches[g, h, o, d])
        except KeyError:
            constraints[f"{h}_{o}"] = []
            constraints[f"{h}_{o}"].append(matches[g, h, o, d])
    for constraint in constraints.values():
        model.AddExactlyOne(constraint)


def process(rows, result_file, partial_results=[]):
    all_teams = get_all_teams(rows)
    all_days = get_all_dates(rows)
    all_grounds = get_all_grounds(rows)

    logging.debug("Start making states")
    # # match - pre-allocates
    # matches = read_data("results/result-partial.xlsx")

    valid_states = get_valid_states(rows, partial_results)
    logging.debug(f"Valid states: {len(valid_states)}")

    # Creates the model.
    model = cp_model.CpModel()

    logging.debug("Start making variables")
    matches = make_variables(model, valid_states)

    logging.debug("Set Home vs Opposition - Play exactly once")
    home_opposition_constraint(model, valid_states, matches)

    logging.debug("Set Consecutive dates constraint")
    set_consecutive_date_constraint(model, rows, valid_states, matches)

    # Number of matches - same as Home vs Opposition - so no need
    # print ("Set Number of Matches Constraint")
    number_of_matches_constraint(model, rows, valid_states, matches)

    logging.debug("Set Must constraint")
    must_constraint(model, rows, matches, partial_results)

    logging.debug("Set Home Match constraint")
    must_home_match_constraint(model, rows, valid_states, matches)

    logging.debug("Set Home Opposition constraint")
    teams_on_a_day_constraint(model, rows, valid_states, matches)

    logging.debug("Set Ground constraint")
    ground_constraint(model, rows, valid_states, matches)

    logging.debug("solve")
    # Creates the model.
    solver = cp_model.CpSolver()
    # solver.parameters.log_search_progress = True
    solver.parameters.num_workers = 8
    solver.parameters.linearization_level = 0
    solver.preferred_variable_order = 3
    solver.randomize_search = True
    solver.subsolvers = 0
    solver.parameters.stop_after_first_solution = True
    # Display the first five solutions.
    solution_limit = 10000
    solution_printer = SolutionPrinter(
        rows,
        result_file,
        valid_states,
        matches,
        all_grounds,
        all_teams,
        all_days,
        solution_limit,
    )

    # Enumerate all solutions.
    # solver.parameters.enumerate_all_solutions = True
    # print (f"Start solving {result_file}")
    solver.Solve(model, solution_printer)

    # Statistics.y
    logging.debug("\nStatistics")
    logging.debug("  - conflicts      : %i" % solver.NumConflicts())
    logging.debug("  - branches       : %i" % solver.NumBranches())
    logging.debug("  - wall time      : %f s" % solver.WallTime())
    logging.debug("  - solutions found: %i" % solution_printer.solution_count())

    return solution_printer.solution_count()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
