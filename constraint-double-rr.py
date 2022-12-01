from ortools.sat.python import cp_model


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
  """Print intermediate solutions."""

  def __init__(self, matches, num_teams, num_days, limit):
      cp_model.CpSolverSolutionCallback.__init__(self)
      self._matches = matches
      self._num_teams = num_teams
      self._num_days = num_days
      # self._num_grounds =num_grounds
      self._solution_count = 0
      self._solution_limit = limit

  def on_solution_callback(self):
      print (self.Value)
      self._solution_count += 1
      for h in range(self._num_teams):
        for o in range(self._num_teams):
          for d in range(self._num_days):
            if self.Value(self._matches[(h,o,d)]):
              print(f'Team-{h} playing against Team-{o} on {d}')
                 
      if self._solution_count >= self._solution_limit:
          print('Stop search after %i solutions' % self._solution_limit)
          self.StopSearch()

  def solution_count(self):
      return self._solution_count


def main():
    # Data.
    num_teams = 10
    num_grounds = 4
    num_days = 18
    num_match_types = 2
    all_match_types = range(num_match_types)
    all_teams = range(num_teams)
    all_days = range(num_days)
    # all_grounds = range(num_grounds)

    # Creates the model.
    model = cp_model.CpModel()

    matches = {}

    # create match variable
    for h in all_teams:
      for o in all_teams:
        for d in all_days:
          matches[h,o,d] = model.NewBoolVar(f'match_h{h}_o{o}_{d}')

    # all teams play exactly one match against all oppositions
    for h in all_teams:
       for o in all_teams:
        if h == o:
           continue
        model.AddExactlyOne(matches[h,o,d] for d in all_days)

    # no team plays more than once in a day    
    # for d in all_days:
    #   for h in all_teams:
    #     model.AddAtMostOne(matches[h,o,d] for o in all_teams)
    #     model.AddAtMostOne(matches[o,h,d] for o in all_teams)
    #     states = []
    #     for o in all_teams:
    #        if o!=h:
    #           states.append(matches[o,h,d])
    #           states.append(matches[h,o,d])
    #     model.AddAtMostOne(states
        
    for h in all_teams:
      for d in all_days:
        model.AddAtMostOne(matches[h,o,d] for o in all_teams)
        model.AddAtMostOne(matches[o,h,d] for o in all_teams)
        states = []
        for o in all_teams:
           if o!=h:
              states.append(matches[o,h,d])
              states.append(matches[h,o,d])
        model.AddAtMostOne(states)
        
    # Creates the model.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0

    # Display the first five solutions.
    solution_limit = 1
    solution_printer = SolutionPrinter(matches, num_teams, num_days, solution_limit)

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
