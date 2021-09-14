import sys
from model import Shift, Volunteer
from loader import get_shifts_from_csv, get_volunteers_from_csv
from ortools.constraint_solver import pywrapcp

solver = pywrapcp.Solver('rod')
volunteers = Volunteer.select()
shifts = get_shifts_from_csv()

v_range = range(len(volunteers))
s_range = range(len(shifts))

slots = {}
slots_flat = []
slots_cantake = {}

def get_volunteers_for_shift_id(shift_id):
    return [slots[(shift_id, v)] for v in v_range]

# Make a |V|x|S| matrix of volunteers to slots. 1 means the volunteer
# takes the slot. Initialize everything to 0.
for volunteer_id, volunteer in enumerate(volunteers):
    for shift_id, shift in enumerate(shifts):
        can_take = int(volunteer.can_take(shift))

        slots[(shift_id, volunteer_id)] = solver.IntVar(0, can_take, "%d,%d" % (shift_id, volunteer_id))
        slots_flat.append(slots[(shift_id, volunteer_id)])

        slots_cantake[(shift_id,volunteer_id)] = can_take
        sys.stdout.write(str(can_take))

    sys.stdout.write(" " + volunteer.name)    
    sys.stdout.write("\n")

for shift_id, shift in enumerate(shifts):
    sys.stdout.write(chr(shift.num_people+40))
exit()

for shift_id, shift in enumerate(shifts):
    # Assign exactly the amount of people needed for each shift
    solver.Add(solver.Sum(get_volunteers_for_shift_id(shift_id)) == shift.num_people)
    # solver.Add(solver.Sum(get_volunteers_for_shift_id(shift_id)) >1)

    # Moreover, make sure we don't add the same people to shifts that collide
    for candidate_id, collision_candidate in enumerate(shifts):
        if candidate_id > shift_id and shift.collides_with(collision_candidate):
            s1 = get_volunteers_for_shift_id(shift_id)
            s2 = get_volunteers_for_shift_id(candidate_id)

            for v1, v2 in zip(s1, s2):
                #print(v1, v2)
                # solver.Add(v1 + v2 <= 1)
                pass
    
    
# decision builder
db = solver.Phase(slots_flat, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)
solver.Solve(db)

while solver.NextSolution():
    for shift_id, shift in enumerate(shifts):
        print("%s from %s to %s:" % (shift.title, shift.starts, shift.ends))
        vols = [slots[(shift_id, x)].Value() for x in v_range]
        print(vols)
    break;
