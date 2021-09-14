import sys, os
from model import *



volunteer = Volunteer.query(" ".join(sys.argv[1:]))
shifts = Shift.select()

print("Finding places where %s could work..." % volunteer)


for shift in shifts:
    if volunteer.could_take(shift):
        print(shift)
