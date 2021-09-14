from model import *

volunteer = Volunteer.query("Søren Vinther")

pals = {}

for s in volunteer.get_shifts():
    if s.title == "Bar": continue
    for v in s.get_volunteers():
        try:
            pals[v.name] += 1
        except:
            pals[v.name] = 1

print(pals)
