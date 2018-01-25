from util import parse_datetime

WEEKDAYS = ["Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"]


class ShiftSlot:
    # bar, kitchen, janitor
    type = None
    num_people = 0
    starts = None
    ends = None
    needs_driver = False

    def __init__(self, gdocs_line):
        self.type = gdocs_line[0]
        self.num_people = int(gdocs_line[1])
        self.starts = parse_datetime(gdocs_line[2])
        self.ends = parse_datetime(gdocs_line[3])
        self.needs_license = int(gdocs_line[4])
    
    def __repr__(self):
        day = WEEKDAYS[self.starts.weekday()]
        
        return "<%s: %s from %s to %s (%s people)>" % (day, self.type, self.starts, self.ends, self.num_people)


class Volunteer:

    name = None
    can_drive = False
    has_car = False
    phone_number = None
    
