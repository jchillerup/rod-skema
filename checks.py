from termcolor import colored, cprint
from model import *

volunteers = Volunteer.select().order_by(Volunteer.name)
shifts = Shift.select()

def get_shifts_for_volunteer(volunteer):
    return volunteer.get_shifts()

def get_load_for_volunteer(volunteer):
    return volunteer.get_load()


for volunteer in volunteers:
    s = get_shifts_for_volunteer(volunteer)
    load = get_load_for_volunteer(volunteer)
    working_hours = volunteer.hours_active()
    
    print("* %s" % volunteer.name)
    print("Arrives: %s" % WEEKDAYS[(volunteer.available_start.weekday()+1) % 7])
    print("Departs: %s" % WEEKDAYS[(volunteer.available_end.weekday() +1) % 7])
    print("Load: %.02f" % load)

    volunteer.load = load

    bar_hours = 0
    kitchen_hours = 0

    for shift in s:
        if shift.is_bar:
            bar_hours += shift.get_load()
        if shift.is_kitchen:
            kitchen_hours += shift.get_load()

    bar_percentage = bar_hours / working_hours
    kitchen_percentage = kitchen_hours / working_hours
    
    print("Bar / Kitchen: %.02f / %0.02f" % (bar_percentage, kitchen_percentage))

    for shift in s:
        if shift.starts < volunteer.available_start:
            cprint("%s STARTS BEFORE %s ARRIVES" % (shift.title, volunteer.name), 'red')

        if shift.ends > volunteer.available_end:
            cprint("%s ENDS AFTER %s LEAVES" % (shift.title, volunteer.name), 'red')
    
    for s1 in s:
        for s2 in s:
            if s1 != s2 and s1.starts <= s2.starts:
                if s1.collides_with(s2):
                    cprint("%s COLLIDES %s" % (s1, s2), 'red')
                    continue
                
                if s1.soft_collides_with(s2):
                    cprint("%s TOO CLOSE %s" % (s1, s2), 'yellow')
                

    print()

exit()

for shift in shifts:
    relations = VolunteerShiftRelation.select().where(VolunteerShiftRelation.shift == shift)

    if len(relations) < shift.num_people:
        print(shift)
        print("Needs %d volunteers, has %d" % (shift.num_people, len(relations)))
