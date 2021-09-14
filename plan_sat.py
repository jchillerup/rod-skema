from model import Shift, Volunteer
from loader import get_shifts_from_csv, get_volunteers_from_csv
from ortools.sat.python import cp_model

model = cp_model.CpModel()

volunteers = Volunteer.select()
shifts = get_shifts_from_csv()

v_range = range(len(volunteers))
s_range = range(len(shifts))

slots = {}
slots_flat = []

def get_volunteers_for_shift_id(shift_id):
    return [slots[(shift_id, v)] for v in v_range]

class NursesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
  """Print intermediate solutions."""

  def __init__(self, slots):
    self.__slots = slots
    self.__solution_count = 0

  def NewSolution(self):
    self.__solution_count += 1

    print('Solution #%i' % self.__solution_count)
    for s in self.__slots:
        print(self.Value(s))
        if self.Value(s):
            print(s)

  def SolutionCount(self):
      return self.__solution_count



# Make a |V|x|S| matrix of volunteers to slots. 1 means the volunteer
# takes the slot. Initialize everything to 0.
for volunteer_id, volunteer in enumerate(volunteers):
    for shift_id, shift in enumerate(shifts):
        can_take = int(volunteer.can_take(shift))
#        print(can_take)
        
        slots[(shift_id, volunteer_id)] = model.NewBoolVar("%d,%d" % (shift_id, volunteer_id))
        slots_flat.append(slots[(shift_id, volunteer_id)])


for shift_id, shift in enumerate(shifts):
    # Assign exactly the amount of people needed for each shift
    print(shift.num_people)
    model.Add(sum(get_volunteers_for_shift_id(shift_id)) == shift.num_people)

    # Moreover, make sure we don't add the same people to shifts that collide
    for candidate_id, collision_candidate in enumerate(shifts):
        if candidate_id > shift_id and shift.collides_with(collision_candidate):
            s1 = get_volunteers_for_shift_id(shift_id)
            s2 = get_volunteers_for_shift_id(candidate_id)

            for v1, v2 in zip(s1, s2):
                pass
                #print(v1, v2)
                # model.Add(v1 + v2 <= 1)

solution_printer = NursesPartialSolutionPrinter(slots)

# decision builder
solver = cp_model.CpSolver()
status = solver.SearchForAllSolutions(model, solution_printer)

