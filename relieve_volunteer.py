import sys, os
from model import *

friend = Volunteer.query(" ".join(sys.argv[1:]))

print("Finding shifts where others could take work from %s..." % friend)

shifts = friend.get_shifts()

all_volunteers = list(Volunteer.select())
all_volunteers.sort(key=lambda x: x.get_load())

for shift in shifts:
    for volunteer in all_volunteers[:2]:
        if volunteer.could_take(shift):
            print("%s could take %s" % (volunteer.name, shift))
