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

    # når vi laver slots udfra en spec over stævnet, så tilføj constraints
    # med det samme så vi ikke får de samme hjælpere i samtidige slots
    # evt. AllDifferent for slots der overlapper i tid


# ### Hard constraints:
# Ikke to steder samtidig
# Ikke mere end seks timers sammenhængende arbejde (eller bare to vagter lige efter hinanden)
# Lige meget arbejde til alle (afhængigt af antal dage på stævnet)
# Ikke arbejde på et tidspunkt, hvor man ikke er på stævnet
# Mindst x timers pause efter en vagt
# Ædruvagt skal have kørekort

# Sørg for at hårdt constrainede frivillige i hvert fald får noget arbejde!

# ### Soft constriants:
# En fridag til hver frivillig
# Tag højde for ønsker ifht. arbejdstid og arbejdstype

#solver.Add(slots[0] < slots[1])
#solver.Add(slots[1] < slots[2])
#solver.Add(slots[2] < slots[3])
#solver.Add(slots[3] < slots[4])

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
