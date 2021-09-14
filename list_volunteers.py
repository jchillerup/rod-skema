import sys, os
from model import *

volunteers = Volunteer.select().order_by(Volunteer.name)

s = 0

for candidate in volunteers:
    s += candidate.get_num_bar_shifts()
    print("%.2f [%02d] %s (%d bar shifts)" % (candidate.get_load(), candidate.id, candidate.name, candidate.get_num_bar_shifts()))


#print(s/len(volunteers))
