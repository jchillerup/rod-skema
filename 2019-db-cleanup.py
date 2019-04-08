from model import db, Volunteer, Shift, VolunteerRelation
import csv

def print_all_volunteers():
    all_volunteers = Volunteer.select().order_by(Volunteer.name)
    for v in all_volunteers:
        print("%d: %s" % (v.id, v.name))
    print()

def resolve_volunteer(name):
    return list(Volunteer.select().where(Volunteer.name.contains(name)))


for volunteer in Volunteer.select():
    volunteer.name = volunteer.name.strip()
    volunteer.save()
