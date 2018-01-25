from ortools.constraint_solver import pywrapcp

solver = pywrapcp.Solver('rod')

num_slots = 5
num_volunteers = 10

# hver vagt er en IntVar, og dens værdi er hvilken frivillig der tager den
slots = []

for i in range(num_slots):
    # når vi laver slots udfra en spec over stævnet, så tilføj constraints
    # med det samme så vi ikke får de samme hjælpere i samtidige slots

    # evt. AllDifferent for slots der overlapper i tid
    
    slots.append(solver.IntVar(0, num_volunteers, "Vagt %d" % i))

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

solver.Add(slots[0] < slots[1])
solver.Add(slots[1] < slots[2])
solver.Add(slots[2] < slots[3])
solver.Add(slots[3] < slots[4])

# decision builder
db = solver.Phase(slots, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)
solver.Solve(db)

# solutions print
count = 0
while solver.NextSolution():
    count += 1
    print("Solution", count, '\n')
    print(slots)
    
print("Number of solutions:", count)
