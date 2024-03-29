from model import Shift, Volunteer
from loader import get_shifts_from_csv, get_volunteers_from_csv
from ortools.constraint_solver import pywrapcp
import statistics, math

MINIMUM_SHIFT_LENGTH_TO_TRIGGER_COOLDOWN = 0
COOL_DOWN_HOURS = 6

# hver vagt er en IntVar, og dens værdi er hvilken frivillig der tager den
solver = pywrapcp.Solver('rod')


#volunteers = get_volunteers_from_csv()
#volunteers.extend(volunteers[:16])

volunteers = Volunteer.select()

print ("Number of volunteers: %d" % len(volunteers))

shifts = get_shifts_from_csv()
slots = []
loads = []

# TODO: Consider a 2D model of boolean values instead


# Make a slot for each person needed for a shift
for shift in shifts:
    local_slots = []
    for i in range(shift.num_people):
        # TODO: Consider using a sparse variable instead of defining the availability
        # in terms of constraints:
        #   x = solver.IntVar([1, 3, 5], 'x')

        slot = solver.IntVar(0, len(volunteers)-1, str(shift))

        # Tag on the a reference to the shift so we can use it for soft constraints
        slot.shift = shift
        local_slots.append(slot)

        # Put the shift load into a structure so we can calculate a fair schedule for
        # everyone
        loads.append(shift.get_load())

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
            # print("%s collides with %s" % (shift,collision_candidate))
            
            # We have two shifts that collide. We need different volunteers for *all*
            # the slots in those periods

            # TODO: Use NullIntersect instead?
            local_slots = []
            local_slots.extend(shift.slots)
            local_slots.extend(collision_candidate.slots)
            
            solver.Add(solver.AllDifferent(local_slots))


# Make sure we don't assign shifts to days when a volunteer is not present
for volunteer_idx, volunteer in enumerate(volunteers):
    for shift in shifts:
        if not volunteer.can_take(shift):
            shift.number_of_constraints += 1
            #print("Volunteer %s can't take shift %s" % (volunteer, shift)

            for slot in shift.slots:
                solver.Add(slot != volunteer_idx)


# Give volunteers a "cool down period" after a shift
for shift in shifts:
    # debug: look at the number of constraints on each shift
    # print("%s: %d" % (shift, shift.number_of_constraints))
    
    # We could have a minimum shift duration in order to trigger the cooldown
    if shift.duration_hours() > MINIMUM_SHIFT_LENGTH_TO_TRIGGER_COOLDOWN:
        for too_close_candidate in shifts:
            if shift == too_close_candidate: continue
            d = too_close_candidate.starts - shift.ends
            
            # if the candidate is before the current shift, we don't care
            if d.seconds < 0: continue

            if (d.seconds/60/60) < COOL_DOWN_HOURS:
                # print("Shift %s is too close to %s" % (too_close_candidate, shift))
                local_slots = []
                local_slots.extend(shift.slots)
                local_slots.extend(too_close_candidate.slots)

                #for s1 in shift.slots:
                #    for s2 in too_close_candidate.slots:
                #        solver.Add(s1 != s2)

                solver.Add(solver.AllDifferent(local_slots))



def variable_evaluator(a):
    print("variable", a)
                
def value_evaluator(a, b):
    print("value", a, b)
                
# decision builder
db = solver.Phase(slots, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_RANDOM_VALUE)
solver.Solve(db)


# Solution collector
solution = solver.Assignment()
solution.Add(slots)
collector = solver.AllSolutionCollector(solution)


# solutions print
count = 0
cur_high_score = -10000000
cur_lowest_stdev = 10000000

print("Solutions found:", collector.SolutionCount())


def norm(l):
    s = 0
    for i in l:
        s += i**2
    return math.sqrt(s)

while solver.NextSolution():
    count += 1

    # TODO: Grade the solution
    # TODO: Local Neighbor Search?

    score = 0

    hours_worked = [0] * len(volunteers)
    
    for slot in slots:
        
        # score += volunteers[slot.Value()].consider_shift(slot.shift)
        hours_worked[slot.Value()] += ( slot.shift.get_load() / volunteers[slot.Value()].load_multiplier ) / volunteers[slot.Value()].hours_active()

    if (not norm(hours_worked) < cur_lowest_stdev): continue
    cur_lowest_stdev = norm(hours_worked)
    print("%s: %s" % (cur_lowest_stdev, hours_worked))
    
    #if score > cur_high_score:
    #    print("Solution %d, score: %f" % (count, score))
    #    cur_high_score = score

    #    fp = open('out/%d-%d-volunteers.json' % (count, score), 'w')
    #    fp.write(Volunteer.volunteers_to_json(volunteers))
    #    fp.close()

        
    #    fp = open('out/%d-%d-shifts.json' % (count, score), 'w')
    #    fp.write(Shift.shifts_to_json(shifts))
    #    fp.close()

print("Number of solutions:", count)
