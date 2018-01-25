import datetime

WEEKDAYS = ["Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"]

class TimeSlot:
    # bar, kitchen, janitor
    type = None
    time_from = None
    time_to = None

    def __repr__(self):
        day = WEEKDAYS[time_from.weekday()]
        
        return "%s: %s from %s to %s" % (day, type, time_from, time_to)

shifts = []

