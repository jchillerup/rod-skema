from model import *

vol_hours = 0
shift_hours = 0

for volunteer in Volunteer.select():
    vol_hours += (volunteer.available_end-volunteer.available_start).total_seconds()/60/60


for shift in Shift.select():
    # shift_hours += ((shift.ends-shift.starts).total_seconds()/60/60)*shift.num_people
    shift_hours += shift.get_load() * shift.num_people

print ("Volunteer hours:\t%d" % vol_hours)
print ("Shift hours:\t\t%d" % shift_hours)
print ("Even load:\t\t%f (%f hours per day on ROD)" % (shift_hours/vol_hours, shift_hours*24.0/vol_hours))

