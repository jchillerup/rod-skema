import json, datetime
from model import Volunteer, Shift

volunteers = json.loads(open("out/6778801--7-volunteers.json", 'r').read())
shifts = json.loads(open("out/6778801--7-shifts.json", 'r').read())


print(volunteers)

volunteer_hours = {}

for shift in shifts:
    starts = datetime.datetime.strptime(shift["starts"], "%a %b %d %H:%M:%S %Y")
    ends = datetime.datetime.strptime(shift["ends"], "%a %b %d %H:%M:%S %Y")

    delta = ends - starts
    delta_s = delta.total_seconds()

    if delta_s == 24*60*60:
        delta_s /= 2
    
    for slot in shift["slots"]:
        try:
            volunteer_hours[slot] += delta_s
        except KeyError:
            volunteer_hours[slot] = delta_s


def get_total_seconds(volunteer):
    start = datetime.datetime.strptime(volunteer["arrives"], "%a %b %d %H:%M:%S %Y")
    ends = datetime.datetime.strptime(volunteer["departs"], "%a %b %d %H:%M:%S %Y")

    return (ends-starts).total_seconds()
    
for volunteer_id in volunteer_hours:
    seconds = volunteer_hours[volunteer_id]

    volunteer_total_seconds = get_total_seconds(volunteers[volunteer_id])

    frac = seconds / volunteer_total_seconds
    
    print("Volunteer %d: %d hours, %f%%" % (volunteer_id, seconds/60/60, frac))
