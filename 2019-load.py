from model import db, Volunteer, Shift, VolunteerRelation, VolunteerShiftRelation
import datetime, csv

db.create_tables([Volunteer, Shift, VolunteerShiftRelation, VolunteerRelation]);

# volunteer_names = [x.rstrip() for x in open('2019-folk.csv', 'r').read().rstrip().split("\n")]

start_day_dict = {
    "fredag": datetime.date(2019, 4, 12),
    "lørdag": datetime.date(2019, 4, 13),
    "søndag": datetime.date(2019, 4, 14),
    "mandag": datetime.date(2019, 4, 15),
    "tirsdag": datetime.date(2019, 4, 16),
    "onsdag": datetime.date(2019, 4, 17),
    "torsdag": datetime.date(2019, 4, 18),
}

end_day_dict = {
    "søndag": datetime.date(2019, 4, 14),
    "mandag": datetime.date(2019, 4, 15),
    "tirsdag": datetime.date(2019, 4, 16),
    "onsdag": datetime.date(2019, 4, 17),
    "torsdag": datetime.date(2019, 4, 18),
    "fredag": datetime.date(2019, 4, 19),
    "lørdag": datetime.date(2019, 4, 20),
}

with open('2019-folk.csv', 'r') as csvfile:
    pplreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in pplreader:
        v = Volunteer()
        v.name = row['Navn']
        v.available_start = datetime.datetime.combine(
            start_day_dict[row['Ankommer dag'].strip().lower()],
            datetime.datetime.strptime(row['Ankommer tid'], "%H:%M").time()
            )
        
        v.available_end   = datetime.datetime.combine(
            end_day_dict[row['Skrider dag'].strip().lower()],
            datetime.datetime.strptime(row['Skrider tid'], "%H:%M").time()
            )
        v.load_multiplier = float(row['Load'])
        v.email = row['Mail']
        v.phone_number = row['Telefon']

        if len(v.phone_number) > 0 and v.phone_number[0] != '+':
            v.phone_number = "+45" + v.phone_number
            
        v.save()


skipped_first = False
for line in open('2019-tjanser.csv', 'r').readlines():
    if not skipped_first:
        skipped_first = True
        continue
    
    s = Shift()
    s.from_csv(line.split(","))
    s.save()
