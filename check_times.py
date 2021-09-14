from model import *

volunteers = Volunteer.select().order_by(Volunteer.name)


for volunteer in volunteers:
    shifts = volunteer.get_shifts()

    for shift in shifts:
        if not volunteer.can_take(shift):
            print("%s can't do %d: %s" % (volunteer, shift.id, shift))
