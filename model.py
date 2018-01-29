import datetime, json
from util import parse_datetime, check_range_collision

# Use for debugging
HALF_LOAD = True

WEEKDAYS = ["Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"]

ROD_DAYS = [
    datetime.date(2018, 3, 23),
    datetime.date(2018, 3, 24),
    datetime.date(2018, 3, 25),
    datetime.date(2018, 3, 26),
    datetime.date(2018, 3, 27),
    datetime.date(2018, 3, 28),
    datetime.date(2018, 3, 29),
    datetime.date(2018, 3, 30),
    datetime.date(2018, 3, 31),
]

class Shift:
    # bar, kitchen, janitor
    type = None
    num_people = 0
    starts = None
    ends = None
    needs_driver = False
    is_kitchen = False
    is_bar = False
    is_high_tempo = False
    
    number_of_constraints = 0

    def collides_with(self, candidate):
        return check_range_collision(self.starts, self.ends, candidate.starts, candidate.ends)

    def duration_hours(self):
        d = self.ends - self.starts
        return d.seconds / 60 / 60
    
    def __init__(self, gdocs_line):
        self.type = gdocs_line[0]
        self.num_people = int(gdocs_line[1])
        self.starts = parse_datetime(gdocs_line[2])
        self.ends = parse_datetime(gdocs_line[3])

        self.needs_license = bool(int(gdocs_line[4]))
        self.is_kitchen = bool(int(gdocs_line[5]))
        self.is_bar = bool(int(gdocs_line[6]))
        self.is_high_tempo = bool(int(gdocs_line[7]))

        if HALF_LOAD:
            self.num_people = self.num_people // 2
    
    def __repr__(self):
        day = WEEKDAYS[self.starts.weekday()]
        
        return "<%s: %s from %s to %s (%s people)>" % (day, self.type, self.starts, self.ends, self.num_people)

    def to_dict(self):
        s = []
        for slot in self.slots:
            s.append(slot.Value())
        
        return {
            "type": self.type,
            "starts": self.starts.ctime(),
            "ends": self.ends.ctime(),
            "slots": s
        }

    def shifts_to_json(shifts):
        s = []
        for shift in shifts:
            s.append(shift.to_dict())

        return json.dumps(s)


class Volunteer:
    name = None
    can_drive = False
    has_car = False
    phone_number = None
    available_starts = None
    available_ends = None
    
    def can_take(self, shift):
        return check_range_collision(self.available_start, self.available_end, shift.starts, shift.ends)
    
    def resolve_driver(self, i):
        if i == "Ja": return 1
        if i == "Nej": return 0
        if i == "Jeg har kørekort men er helst fri for at køre": return 0.5

    def resolve_has_car(self, i):
        if i.lower() == "ja": return 1

        return 0

    def resolve_times(self, i):
        times = i.split(";")
        out = []

        strings = [
            "Opsætningsvagt fredag d. 23/3 til lørdag d. 24/3: Til opsætning/forberedelse af stævnet fra kl. 15 fredag til 15 lørdag dag (Selvfølgelig med søvn og pauser indregnet!)", 
            "Lørdag d. 24/3",
            "Søndag d. 25/3",
            "Mandag d. 26/3",
            "Tirsdag d. 27/3",
            "Onsdag d. 28/3",
            "Torsdag d. 29/3",
            "Fredag d. 30/3",
            "Nedtagningsvagt fredag d. 30/3 til lørdag d. 31/3: Nedtagning af ROD fra fredag eftermiddag til lørdag ved middagstid. (Der er mulighed for at aftale afgangstidspunkt lørdag med arbejdsgruppen).",
        ]

        for j in range(len(strings)):
            if strings[j] in times: out.append(j)

        # Shouldn't really be necessary...
        out.sort()

        # Special case: the block contains consecutive days:
        #print("Max: %d, Min: %d, Len: %d" % (max(out), min(out), len(out)))
        if (max(out)-min(out)+1 == len(out)):
            # TODO: Support arrival and departure times
            
            self.available_start = datetime.datetime.combine(ROD_DAYS[min(out)],
                                                             datetime.time(12,00)
            )
            self.available_end = datetime.datetime.combine(ROD_DAYS[max(out)],
                                                           datetime.time(18,00))

            self.available = self.available_end - self.available_start
            
        else:
            raise ValueError('Volunteer %s has non-consecutive dates' % self)
        
        # print("Given: %s\nStart: %s, end: %s" % (i, self.available_start, self.available_end))
        
        return out

    # 17,18,19
    def resolve_shift_sobriety_choices(self, i):
        if i == "Det er tiptop": return 1
        if i == "Det har jeg det okay med": return 0
        if i == "Det vil jeg helst undgå": return -1
        if i == "Det har jeg det skidt med": return -3
        if i == "Jeg har ikke kørekort": return -10

        return -1

    # 20,21,22,23
    def resolve_shift_type_choices(self, i):
        if i == "Det synes jeg er mega fedt!": return 1
        if i == "Det har jeg det fint med": return 0
        if i == "Det vil jeg helst ikke": return -1
        if i == "Det vil jeg meget gerne undgå": return -5
        return -1

    def consider_shift(self, shift):
        penalty = 0

        #penalty += shift.is_late_night * self.late_night_penalty
        penalty += shift.is_kitchen * self.kitchen_penalty
        penalty += shift.is_bar * self.bar_penalty
        penalty += shift.is_high_tempo * self.high_tempo_penalty
        
        # TODO: Driving constraints?
        # TODO: Working with friends?
        return penalty


    def __init__(self, gdocs_line):
        self.name = gdocs_line[1]
        self.phone_number = gdocs_line[2];
        self.email = gdocs_line[3];
        self.ice_number = gdocs_line[4];
        
        driver = self.resolve_driver(gdocs_line[8])
        has_car = self.resolve_has_car(gdocs_line[9])

        self.resolve_times(gdocs_line[11])
        
        sober_day = self.resolve_shift_sobriety_choices(gdocs_line[17])
        sober_sleeping_night = self.resolve_shift_sobriety_choices(gdocs_line[18])
        sober_wake_night = self.resolve_shift_sobriety_choices(gdocs_line[19])
        
        self.late_night_penalty = self.resolve_shift_type_choices(gdocs_line[20])
        self.kitchen_penalty = self.resolve_shift_type_choices(gdocs_line[21])
        self.bar_penalty = self.resolve_shift_type_choices(gdocs_line[22])
        self.high_tempo_penalty = self.resolve_shift_type_choices(gdocs_line[23])

        # TODO: Normalize the penalties! Very important.
        
    def __repr__(self):
        return "<Volunteer: %s>" % self.name

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "ice_number": self.ice_number,
            "can_drive": self.can_drive,
            "has_car": self.has_car            
        }

    
    def volunteers_to_json(volunteers):
        v = []
        for volunteer in volunteers:
            v.append(volunteer.to_dict())
            
        return json.dumps(v)
