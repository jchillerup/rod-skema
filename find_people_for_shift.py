import sys, os
from model import *

shift =Shift.get(int(sys.argv[1]))

for candidate in shift.find_candidates():
    print("%.2f [%02d] %s (%d bar shifts)" % (candidate.get_load(), candidate.id, candidate.name, candidate.get_num_bar_shifts()))


if (len(sys.argv) > 2):
    i = int(sys.argv[2])
    v = Volunteer.get(i)
    
    print("Assigning %s to shift %s" % (v, shift))
    shift.assign_volunteer(v)

    print("New load %.02f" % v.get_load())
