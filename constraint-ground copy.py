from ortools.sat.python import cp_model


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
  """Print intermediate solutions."""

  def __init__(self, matches, num_grounds, num_teams, num_days, limit):
      cp_model.CpSolverSolutionCallback.__init__(self)
      self._matches = matches
      self._num_teams = num_teams
      self._num_days = num_days
      self._num_grounds =num_grounds
      self._solution_count = 0
      self._solution_limit = limit

  def on_solution_callback(self):
      print (self.Value)
      self._solution_count += 1
      for g in range (self._num_grounds):
        for h in range(self._num_teams):
          for o in range(self._num_teams):
            for d in range(self._num_days):
              if self.Value(self._matches[(g,h,o,d)]):
                print(f'Team-{h} playing against Team-{o} on {d} at {g}')
                 
      if self._solution_count >= self._solution_limit:
          print('Stop search after %i solutions' % self._solution_limit)
          self.StopSearch()

  def solution_count(self):
      return self._solution_count


def main():
    # Data.
    num_teams = 4
    num_grounds = 3
    num_days = 6
    all_teams = range(num_teams)
    all_days = range(num_days)
    all_grounds = range(num_grounds)

    # Creates the model.
    model = cp_model.CpModel()

    matches = {}

    # create match variable
    for g in all_grounds:
      for h in all_teams:
        for o in all_teams:
          for d in all_days:
            matches[g,h,o,d] = model.NewBoolVar(f'match_g{g}_h{h}_o{o}d_{d}')

    # all teams play exactly one match against all oppositions
    # regardless of ground or days
    for h in all_teams:
      for o in all_teams:
        if h == o:
          continue
        model.AddExactlyOne(matches[g,h,o,d] for d in all_days for g in all_grounds)

    # team plays only one match in a day
    # regardless of ground or opposition 
    for h in all_teams:
      for d in all_days:
        model.AddAtMostOne(matches[g,h,o,d] for o in all_teams for g in all_grounds)
        model.AddAtMostOne(matches[g,o,h,d] for o in all_teams for g in all_grounds)
        states = []
        for g in all_grounds:
          for o in all_teams:
            if o!=h:
                states.append(matches[g,o,h,d])
                states.append(matches[g,h,o,d])
        model.AddAtMostOne(states)

  
    # at most one match on a ground on a day
    # regardless of team or opposition
    for g in all_grounds:
       for d in all_days:
          model.AddAtMostOne(matches[g,h,o,d] for h in all_teams for o in all_teams)        
  
          
    # Creates the model.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0

    # Display the first five solutions.
    solution_limit = 1
    solution_printer = SolutionPrinter(matches, num_grounds, num_teams, num_days, solution_limit)

    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    solver.Solve(model, solution_printer)


    
    # Statistics.y 
    print('\nStatistics')
    print('  - conflicts      : %i' % solver.NumConflicts())
    print('  - branches       : %i' % solver.NumBranches())
    print('  - wall time      : %f s' % solver.WallTime())
    print('  - solutions found: %i' % solution_printer.solution_count())

if __name__ == '__main__':
    main()
