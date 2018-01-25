from util import parse_datetime

WEEKDAYS = ["Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"]


class ShiftSlot:
    # bar, kitchen, janitor
    type = None
    num_people = 0
    starts = None
    ends = None
    needs_driver = False

    def collides_with(self, candidate):
        # https://stackoverflow.com/questions/325933/determine-whether-two-date-ranges-overlap
        return (max(self.starts, candidate.starts) < min(self.ends, candidate.ends))
    
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

    def resolve_driver(self, i):
        if i == "Ja": return 1
        if i == "Nej": return 0
        if i == "Jeg har kørekort men er helst fri for at køre": return 0.5

    def resolve_has_car(self, i):
        if i.lower() == "ja": return 1

        return 0

    def resolve_times(self, i):
        times = i.split(", ")
        out = []

        if "Opsætningsvagt fredag d. 23/3 til lørdag d. 24/3: Til opsætning/forberedelse af stævnet fra kl. 15 fredag til 15 lørdag dag (Selvfølgelig med søvn og pauser indregnet!)" in times: out.append(0)
        if "Lørdag d. 24/3" in times: out.append(1)
        if "Søndag d. 25/3" in times: out.append(2)
        if "Mandag d. 26/3" in times: out.append(3)
        if "Tirsdag d. 27/3" in times: out.append(4)
        if "Onsdag d. 28/3" in times: out.append(5)
        if "Torsdag d. 29/3" in times: out.append(6)
        if "Fredag d. 30/3" in times: out.append(7)
        if "Nedtagningsvagt fredag d. 30/3 til lørdag d. 31/3: Nedtagning af ROD fra fredag eftermiddag til lørdag ved middagstid. (Der er mulighed for at aftale afgangstidspunkt lørdag med arbejdsgruppen)." in times: out.append(8)
    
        return out

    # 17,18,19
    def resolve_driver_choices(self, i):
        if i == "Det er tiptop": return 4
        if i == "Det har jeg det okay med": return 3
        if i == "Det vil jeg helst undgå": return 2
        if i == "Det har jeg det skidt med": return 1
        if i == "Jeg har ikke kørekort": return 0

        return -1

    # 20,21,22,23
    def resolve_shift_type_choices(self, i):
        if i == "Det synes jeg er mega fedt!": return 3
        if i == "Det har jeg det fint med": return 2
        if i == "Det vil jeg helst ikke": return 1
        if i == "Det vil jeg meget gerne undgå": return 0
        return -1    


    def __init__(self, gdocs_line):
        self.name = gdocs_line[1]
        driver = self.resolve_driver(gdocs_line[8])
        has_car = self.resolve_has_car(gdocs_line[9])
    
        sober_day = self.resolve_driver_choices(gdocs_line[17])
        sober_sleeping_night = self.resolve_driver_choices(gdocs_line[18])
        sober_wake_night = self.resolve_driver_choices(gdocs_line[19])
        
        late_night = self.resolve_shift_type_choices(gdocs_line[20])
        kitchen = self.resolve_shift_type_choices(gdocs_line[21])
        bar = self.resolve_shift_type_choices(gdocs_line[22])
        high_tempo = self.resolve_shift_type_choices(gdocs_line[23])
