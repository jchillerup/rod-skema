from model import Shift, Volunteer, VolunteerShiftRelation, ROD_DAYS
from sanity import *
from ortools.sat.python import cp_model

LOAD_PRESETS = False
COMMIT = False

# Load alle folk
volunteers = list(Volunteer.select().execute())
shifts = list(Shift.select().execute())

volunteers_inv = dict()
volunteer_loads = dict()
for v, volunteer in enumerate(volunteers):
    volunteer_loads[v] = 0
    volunteers_inv[volunteer] = v

total_hours_needed = sum([x.get_load()*x.num_people for x in shifts])
total_hours_available = sum([x.hours_active() for x in volunteers])
expected_load = total_hours_needed / total_hours_available
load_deviation_tolerance = 0.013

def resolve_volunteer(name):
    for v, volunteer in enumerate(volunteers):
        if volunteer.name == name:
            return v, volunteer

    return None, None

print("Antal frivillige:           %d" % len(volunteers))
print("Antal tjanser:              %d" % len(shifts))
print("Antal timer vi behøver:     %d timer" % total_hours_needed)
print("Antal timer vi har:         %d timer" % total_hours_available)
print("Forventet load:             %f" % (expected_load))

print()
print("Laver sanity checks...")
SANITY_CHECKS = [#DoWeHaveEnoughPeopleForEveryShift,
                 VolunteersDontEndBeforeTheyStart]
for check in SANITY_CHECKS:
    print (check.__name__)
    if check() == False:
        print("Fejlede sanity check.")
        exit()

print("OK!")
model = cp_model.CpModel()

shift_loads = [int(s.get_load()) for s in shifts]

print()
print("Opstiller model...")
# Create work variables
work = {}
for v, volunteer in enumerate(volunteers):        
    for s, shift in enumerate(shifts):
        work[v, s] = model.NewBoolVar('work%i_%i' % (v, s))


if LOAD_PRESETS:
    print(" - Indsætter de nagelfaste tjansetildelinger (%d stk.)" % len(VolunteerShiftRelation.select().execute()) )
    for s, shift in enumerate(shifts):
        for volunteer in shift.get_volunteers():
            v = volunteers_inv[volunteer]

            model.Add(work[v, s] == 1)

# Assign n volunteers to each shift
print(" - Ansæt passende antal folk pr. tjans")
for v, volunteer in enumerate(volunteers):
    for s, shift in enumerate(shifts):
        #model.Add(sum(work[w, s] for w in range(len(volunteers))) > 0)

        if shift.num_people < 8:
            model.Add(sum(work[w, s] for w in range(len(volunteers))) == shift.num_people)
        else:
            model.Add(sum(work[w, s] for w in range(len(volunteers))) >= shift.num_people-1)
            model.Add(sum(work[w, s] for w in range(len(volunteers))) <= shift.num_people)

print(" - Ingen skal arbejde når de ikke er tilstede")
for v, volunteer in enumerate(volunteers):
    for s, shift in enumerate(shifts):
        if not volunteer.can_take(shift):
            model.Add(work[v, s] == 0)
        
# No soft collisions
print(" - Ikke to tjanser indenfor 8 timer af hinanden")
for s1, shift1 in enumerate(shifts):
    for s2, shift2 in enumerate(shifts):
        if s1 < s2 and shift1.soft_collides_with(shift2):
            for v, volunteer in enumerate(volunteers):
                model.Add(work[v, s1] + work[v, s2] <= 1)


print(" - Alle har %.02f <= load <= %.02f" % (expected_load-load_deviation_tolerance, expected_load+load_deviation_tolerance))
loads = []
errors = []
for v, volunteer in enumerate(volunteers):
    error = model.NewIntVar(-1000000, 1000000, 'error_%i' % v)
    abs_error = model.NewIntVar(0, 1000000, 'abs_error_%i' % v)
    
    hours_worked = sum((shift_loads[s] * work[v, s]) for s in range(len(shifts)))

    if volunteer.load_multiplier == 1:
        devtol = load_deviation_tolerance
    else:
        devtol = load_deviation_tolerance / volunteer.load_multiplier
    
    #model.Add(1000 * hours_worked >= int(volunteer.hours_present() * volunteer.load_multiplier * ((expected_load - devtol) * 1000) )) 
    #model.Add(1000 * hours_worked <= int(volunteer.hours_present() * volunteer.load_multiplier * ((expected_load + devtol) * 1000) ))

    # dette virker ikke
    # model.AddAbsEquality(error, 100000 * hours_worked - int(100000 * expected_load))

    model.Add(
        error == 10000 * hours_worked - int(10000 * volunteer.hours_present() * volunteer.load_multiplier * expected_load)
    )
    model.AddAbsEquality(abs_error, error)
    errors.append(abs_error)

# TODO: Minimize max(errors) - min(errors)
max_error = model.NewIntVar(0, 1000000, 'max_error')
min_error = model.NewIntVar(0, 1000000, 'max_error')

model.AddMaxEquality(max_error, errors)
model.AddMinEquality(max_error, errors)

# Doesn't work
# model.Minimize(max_error - min_error)


# Everybody gets a bar shift
print(" - Alle får mindst én bartjans og ingen får mere end to")
print(" - Ingen står for morgenbrød, toasts og natmad mere end én gang")
for v, volunteer in enumerate(volunteers):
    bar_shifts = list()
    bread_shifts = list()
    toast_shifts = list()
    natmad_shifts = list()
    
    for s, shift in enumerate(shifts):
        if shift.title == "Bar":
            bar_shifts.append(work[v, s])
            
        if shift.title == "Morgenbrød":
            bread_shifts.append(work[v, s])

        if shift.title == "Toasts":
            toast_shifts.append(work[v, s])

        if shift.title == "Natmad + opvask":
            natmad_shifts.append(work[v, s])
            

    model.Add(sum(bar_shifts) > 0)
    model.Add(sum(bar_shifts) <= 2)

    model.Add(sum(bread_shifts) <= 1)

    model.Add(sum(toast_shifts) <= 1)

    model.Add(sum(natmad_shifts) <= 1)

print(" - Folk arbejder med deres venner")
happies = list()
for v, volunteer in enumerate(volunteers):
    friends = volunteer.get_friends()
    fsum = 0
    for friend in friends:
        f = volunteers_inv[friend]

        # fsum += sum(work[v, s] and work[f, s] for s in range(len(shifts)))
        for s, shift in enumerate(shifts):
            happies.append((work[v, s] and work[f, s])) #.OnlyEnforceIf(work[v, s])



            
print("   Antal happies: %d" % len(happies))
# model.Maximize(sum(happies))


print(" - Alexandra har ingen nattevagter")
for v, volunteer in enumerate(volunteers):
    if volunteer.name == "Alexandra Nilsson":
        for s, shift in enumerate(shifts):

            starts_hour = shift.starts.time().hour
            ends_hour = shift.ends.time().hour

            if starts_hour >= 22 or ends_hour <= 8:
                model.Add(work[v,s] == 0)

print(" - Simon er lydmand til koncerten")
for s, shift in enumerate(shifts):
    if shift.title == "Lydmand til koncert":
        v, simon = resolve_volunteer("Simon Oxholm")

        # There can be only one...
        model.Add(work[v, s] == 1)

print(" - Rasmus arbejder ikke søndag")
r, rasmus = resolve_volunteer("Rasmus Brinck")
for s, shift in enumerate(shifts):
    if shift.starts.date() == ROD_DAYS[2]:
        model.Add(work[r, s] == 0)


print() 
print("Søger efter løsninger...")
solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 4
# solver.parameters.use_lns = 1

solution_printer = cp_model.ObjectiveSolutionPrinter()
status = solver.SolveWithSolutionCallback(model, solution_printer)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for s, shift in enumerate(shifts):
        print("* %s: %s" % (shift.starts, shift.title))

        for v, volunteer in enumerate(volunteers):
            if solver.BooleanValue(work[v, s]):
                if COMMIT:
                    shift.assign_volunteer(volunteer)
                    
                volunteer_loads[volunteers_inv[volunteer]] += shift.get_load()
                
                print("  - %s"% volunteer.name)
else:
    print("Ingen løsninger!")

print()
print("Belastninger:")
for v, volunteer in enumerate(volunteers):
    print("%.02f  %.02f  %s" % (volunteer_loads[v], (volunteer_loads[v] / volunteer.hours_active()), volunteer.name))
    
print()
print('Statistics')
print('  - status          : %s' % solver.StatusName(status))
print('  - conflicts       : %i' % solver.NumConflicts())
print('  - branches        : %i' % solver.NumBranches())
print('  - wall time       : %f s' % solver.WallTime())



# model.Add(sum(work[v, s] for s in range(len(shifts))) <= 7)


# kamil skal på nedtagning
