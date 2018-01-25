from loader import get_shifts_from_csv, get_volunteers_from_csv
from ortools.constraint_solver import pywrapcp

# hver vagt er en IntVar, og dens værdi er hvilken frivillig der tager den
solver = pywrapcp.Solver('rod')


volunteers = get_volunteers_from_csv()
shifts = get_shifts_from_csv()
slots = []

# A shift has a slot per person needed
for shift in shifts:
    # Make a slot for each person needed for a shift

    local_slots = []
    for i in range(shift.num_people):
        local_slots.append(solver.IntVar(0, len(volunteers)-1, str(shift)))

    # make sure that we're not assigning the same people to two slots on the same shift
    solver.Add(solver.AllDifferent(local_slots))
    slots.extend(local_slots)

    # In a minute we'll need to access the slots of this shift, so let's put
    # them somewhere where we can find them.
    shift.slots = local_slots


# Make sure we're not assigning the same people to overlapping shifts (one cannot work
# both in the bar and the kitchen at the same time)
for shift in shifts:
    for collision_candidate in shifts:
        if shift.collides_with(collision_candidate) and shift != collision_candidate:
            print("%s collides with %s" % (shift,collision_candidate))
            
            # We have two shifts that collide. We need different volunteers for *all*
            # the slots in those periods
            local_slots = []
            local_slots.extend(shift.slots)
            local_slots.extend(collision_candidate.slots)
            
            solver.Add(solver.AllDifferent(local_slots))

# decision builder
db = solver.Phase(slots, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)
solver.Solve(db)

# solutions print
count = 0
while solver.NextSolution():
    count += 1
    print("Solution", count, '\n')

    for slot in slots:
        print ("%s: %s" % (slot, volunteers[slot.Value()].name))
    
print("Number of solutions:", count)
