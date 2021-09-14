from model import *

shifts = Shift.select()

for shift in shifts:
    actual = len(shift.get_volunteers())
    if actual < shift.num_people:
        print("%d < %d: %s" % (actual, shift.num_people, shift))
