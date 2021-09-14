from model import *

volunteers = Volunteer.select().order_by(Volunteer.id)
shifts = Shift.select()

for shift in shifts:
    shift.slots = []

    for rel in VolunteerShiftRelation.select().where(VolunteerShiftRelation.shift == shift):
        shift.slots.append(rel.volunteer_id)

fp = open('volunteers.json', 'w')
fp.write(Volunteer.volunteers_to_json(volunteers))
fp.close()

fp = open('shifts.json', 'w')
fp.write(Shift.shifts_to_json(shifts))
fp.close()
