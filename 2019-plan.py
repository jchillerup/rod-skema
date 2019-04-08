from model import Shift, Volunteer, VolunteerShiftRelation, ROD_DAYS
from ortools.sat.python import cp_model

COMMIT = True

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

min_load = expected_load-0.01
max_load = expected_load+0.02

model = cp_model.CpModel()

shift_loads = [int(s.get_load()) for s in shifts]

print()
print("Opstiller model...")
# Create work variables
work = {}
for v, volunteer in enumerate(volunteers):        
    for s, shift in enumerate(shifts):
        work[v, s] = model.NewBoolVar('work%i_%i' % (v, s))


print(" - Indsætter de nagelfaste tjansetildelinger (%d stk.)" % len(VolunteerShiftRelation.select().execute()) )
for s, shift in enumerate(shifts):
    for volunteer in shift.get_volunteers():
        v = volunteers_inv[volunteer]

        model.Add(work[v, s] == 1)

# Assign n volunteers to each shift
print(" - Ansæt passende antal folk pr. tjans")
for v, volunteer in enumerate(volunteers):
    for s, shift in enumerate(shifts):
        # sum af shifts == shift.num_people
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


print(" - Alle har %.02f <= load <= %.02f" % (min_load, max_load))
loads = []
for v, volunteer in enumerate(volunteers):
    hours_worked = sum((shift_loads[s] * work[v, s]) for s in range(len(shifts)))

    model.Add(1000 * hours_worked >= int(volunteer.hours_present() * volunteer.load_multiplier * (min_load * 1000) )) 
    model.Add(1000 * hours_worked <= int(volunteer.hours_present() * volunteer.load_multiplier * (max_load * 1000) ))



    
# Everybody gets a bar shift
print(" - Alle får mindst én bartjans og ingen får mere end to")
print(" - Ingen står for morgenbrød mere end én gang")
for v, volunteer in enumerate(volunteers):
    bar_shifts = list()
    bread_shifts = list()
    for s, shift in enumerate(shifts):
        if shift.title == "Bar":
            bar_shifts.append(work[v, s])
            
        if shift.title == "Morgenbrød":
            bread_shifts.append(work[v, s])

    model.Add(sum(bar_shifts) > 0)
    model.Add(sum(bar_shifts) <= 2)

    model.Add(sum(bread_shifts) <= 1)


    
# TODO: minimize error expected load / actual load
#model.Minimize(volunteer_max_load - volunteer_min_load)


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
model.Maximize(sum(happies))



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

print(" - Kragen og Kamil er på opsætning")
for s, shift in enumerate(shifts):
    if shift.title == "Opsætning":        
        v, kamil = resolve_volunteer("Kamil Dzielinski")
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
