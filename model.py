import datetime, json
from util import parse_datetime, check_range_collision
from peewee import *

db = SqliteDatabase('rod2019.db')

# Use for debugging
HALF_LOAD = False

WEEKDAYS = ["Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"]
MONTHS = ["", "januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"]

ROD_DAYS = [
    datetime.date(2019, 4, 12),
    datetime.date(2019, 4, 13),
    datetime.date(2019, 4, 14),
    datetime.date(2019, 4, 15),
    datetime.date(2019, 4, 16),
    datetime.date(2019, 4, 17),
    datetime.date(2019, 4, 18),
    datetime.date(2019, 4, 19),
    datetime.date(2019, 4, 20),
]

STARTING_DAYS = {
    "fredag": datetime.date(2019, 4, 12),
    "lørdag": datetime.date(2019, 4, 13),
    "søndag": datetime.date(2019, 4, 14),
    "mandag": datetime.date(2019, 4, 15),
    "tirsdag": datetime.date(2019, 4, 16),
    "onsdag": datetime.date(2019, 4, 17),
    "torsdag": datetime.date(2019, 4, 18),
}

ENDING_DAYS = {
    "søndag": datetime.date(2019, 4, 14),
    "mandag": datetime.date(2019, 4, 15),
    "tirsdag": datetime.date(2019, 4, 16),
    "onsdag": datetime.date(2019, 4, 17),
    "torsdag": datetime.date(2019, 4, 18),
    "fredag": datetime.date(2019, 4, 19),
    "lørdag": datetime.date(2019, 4, 20),
}

class Shift(Model):
    title = CharField()
    num_people = IntegerField()
    starts = DateTimeField()
    ends = DateTimeField()
    needs_driver = BooleanField()
    is_kitchen = BooleanField()
    is_bar = BooleanField()
    is_high_tempo = BooleanField()
    
    number_of_constraints = 0
    
    class Meta:
        database = db

    def find_candidates(self):
        cand = []
        for v in Volunteer.select():
            if v.could_take(self):
                cand.append(v)
        return cand
        
    def get(sid):
        return Shift.select().where(Shift.id == sid)[0]
        
    def get_volunteers(self):
        return Volunteer.select().join(VolunteerShiftRelation).where(VolunteerShiftRelation.shift == self)        
    
    def collides_with(self, candidate):
        return check_range_collision(self.starts, self.ends, candidate.starts, candidate.ends)

    def soft_collides_with(self, candidate):
        if self.collides_with(candidate):
            return True

        time_to_next = (candidate.starts - self.ends).total_seconds()
        time_from_prev = (self.starts - candidate.ends).total_seconds()
        
        if time_to_next >= 0 and time_to_next < 8*60*60:
            return True

        if time_from_prev >= 0 and time_from_prev < 8*60*60:
            return True

        return False
    
    def duration_hours(self):
        d = self.ends - self.starts
        return d.total_seconds() / 60 / 60

    def get_day(self):
        return WEEKDAYS[(self.starts.weekday() + 1) % 7] 
    
    def get_load(self):
        d = self.duration_hours()
        # TODO: Make this a bit smarter...
        if d > 12:
            return d / 2
        else:
            return d
    
    def from_csv(self, gdocs_line):
        self.title = gdocs_line[0]
        self.num_people = int(gdocs_line[1])
        self.starts = parse_datetime(gdocs_line[2])
        self.ends = parse_datetime(gdocs_line[3])

        self.needs_license = bool(int(gdocs_line[4]))
        self.is_kitchen = bool(int(gdocs_line[5]))
        self.is_bar = bool(int(gdocs_line[6]))
        self.is_high_tempo = bool(int(gdocs_line[7]))
        self.needs_driver = False

        if HALF_LOAD:
            self.num_people = self.num_people // 2
    
    def __repr__(self):
        day = WEEKDAYS[(self.starts.weekday()+1)%7]
        
        return "<%s %s-%s: %s (%s/%s people) [%d]>" % (day, self.starts.strftime("%H:%M"), self.ends.strftime("%H:%M"), self.title, len(self.get_volunteers()), self.num_people, self.id)

    def to_dict(self):
        s = []
        for slot in self.slots:
            try:
                s.append(slot.Value())
            except:
                s.append(slot)
        
        return {
            "id": self.id,
            "title": self.title,
            "starts": self.starts.ctime(),
            "ends": self.ends.ctime(),
            "slots": s
        }

    def assign_volunteer(self, volunteer):
        if type(volunteer) == str:
            volunteer = Volunteer.query(volunteer)

        if (self not in volunteer.get_shifts()):
            vsr = VolunteerShiftRelation(shift=self, volunteer=volunteer)
            vsr.save()

    def remove_volunteer(self, volunteer):
        if type(volunteer) == str:
            volunteer = Volunteer.query(volunteer)
        
        vsr = VolunteerShiftRelation.delete().where(VolunteerShiftRelation.shift == self).where(VolunteerShiftRelation.volunteer == volunteer)
        return vsr.execute()
        
    
    def shifts_to_json(shifts):
        s = []
        for shift in shifts:
            s.append(shift.to_dict())

        return json.dumps(s)


class Volunteer(Model):
    name = CharField(unique=True)
    phone_number = CharField(null=True)
    ice_number = CharField(null=True)
    email = CharField(null=True)
    can_drive = BooleanField(null=True)
    has_car = BooleanField(null=True)
    available_start = DateTimeField()
    available_end = DateTimeField()
    
    comments = TextField(null=True)

    load_multiplier = FloatField()
    has_had_friends_added = BooleanField(null=True)

    class Meta:
        database = db

    def get(i):
        return Volunteer.select().where(Volunteer.id==i)[0]
        
    def query(name):
        return Volunteer.select().where(Volunteer.name.startswith(name))[0]

    def set_arrival(self, day, time):
        timestamp = datetime.datetime.combine(STARTING_DAYS[day], datetime.datetime.strptime(time, "%H:%M").time())

        print("Setting arrival for %s to %s" % (self.name, timestamp))
        
        self.available_start = timestamp
        self.save()

    def set_departure(self, day, time):
        timestamp = datetime.datetime.combine(ENDING_DAYS[day], datetime.datetime.strptime(time, "%H:%M").time())
        print("Setting departure for %s to %s" % (self.name, timestamp))
        
        self.available_end = timestamp
        self.save()
        
    def get_first_name(self):
        return self.name.split(" ")[0]
        
    def get_friends(self):
        return Volunteer.select().join(VolunteerRelation, on=VolunteerRelation.likes).where(VolunteerRelation.volunteer == self)

    def get_shifts(self):
        return Shift.select().join(VolunteerShiftRelation).where(VolunteerShiftRelation.volunteer == self).order_by(Shift.starts)
    
    def get_num_bar_shifts(self):
        ret = 0
        for s in self.get_shifts():
            if s.is_bar:
                ret += 1
        return ret

    def hours_present(self):
        return ((self.available_end-self.available_start).total_seconds()/60/60)
    
    def hours_active(self):
        return self.hours_present() * self.load_multiplier
    
    def get_load(self):
        hours_available = self.hours_active()
        total_shift_time = sum([s.get_load() for s in self.get_shifts()])

        return (total_shift_time/hours_available)
    
    def takes_shift(self, shift):
        vsr = VolunteerShiftRelation.select().where(VolunteerShiftRelation.volunteer == self and VolunteerShiftRelation.shift == shift)

        return len(vsr) > 0
    
    def can_take(self, shift):
        # return shift.starts >= self.available_start and shift.ends <= self.available_end
        return check_range_collision(self.available_start, self.available_end, shift.starts, shift.ends) and shift.ends <= self.available_end and shift.starts >= self.available_start
        #return (self.available_start <= shift.starts) and (self.available_end >= shift.ends)

    def could_take(self, shift):
        if not self.can_take(shift):
            return False

        if shift in self.get_shifts():
            return False
        
        for coll_candidate in self.get_shifts():
            if shift.collides_with(coll_candidate):
                return False

            if shift.soft_collides_with(coll_candidate):
                return False
        
        return True
        
    def __repr__(self):
        return "<Volunteer: %s [%d]>" % (self.name, self.id)

    def volunteers_to_json(volunteers):
        v = dict()
        for volunteer in volunteers:
            v[volunteer.id] = volunteer.to_dict()
            
        return json.dumps(v)


class VolunteerRelation(Model):
    volunteer = ForeignKeyField(Volunteer)
    likes = ForeignKeyField(Volunteer)

    class Meta:
        database = db

class VolunteerShiftRelation(Model):
    volunteer = ForeignKeyField(Volunteer)
    shift = ForeignKeyField(Shift)
    has_had_reminder = BooleanField(default=False, null=False)

    class Meta:
        database = db
        
if __name__ == '__main__':
    # Volunteer, VolunteerRelation, Shift, 
    db.create_tables([Volunteer, Shift, VolunteerShiftRelation]);
