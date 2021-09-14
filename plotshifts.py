import sys
from model import Shift, Volunteer
from loader import get_shifts_from_csv, get_volunteers_from_csv
from ortools.constraint_solver import pywrapcp

solver = pywrapcp.Solver('rod')
volunteers = Volunteer.select()
shifts = get_shifts_from_csv()

v_range = range(len(volunteers))
s_range = range(len(shifts))

slots = {}
slots_flat = []
slots_cantake = {}

def get_volunteers_for_shift_id(shift_id):
    return [slots[(shift_id, v)] for v in v_range]

print("""<html><head><style>
.can-take { background: green }
.can-not-take {background: red }
</style><body><table>""")
print("<tr><td></td>")
for shift_id, shift in enumerate(shifts):
    print("<td>"+str(shift.num_people)+"</td>")
print("</tr>")


# Make a |V|x|S| matrix of volunteers to slots. 1 means the volunteer
# takes the slot. Initialize everything to 0.
for volunteer_id, volunteer in enumerate(volunteers):
    
    sys.stdout.write("<tr><td>" + volunteer.name + "</td>")

    for shift_id, shift in enumerate(shifts):
        can_take = int(volunteer.can_take(shift))

        slots[(shift_id, volunteer_id)] = solver.IntVar(0, can_take, "%d,%d" % (shift_id, volunteer_id))
        slots_flat.append(slots[(shift_id, volunteer_id)])

        slots_cantake[(shift_id,volunteer_id)] = can_take

        if can_take:
            class_ = "can-take"
        else:
            class_ = "can-not-take"
            
        sys.stdout.write("<td class='"+class_+"'></td>")

    sys.stdout.write("</tr>")

print("</table></body></html>")

exit()
