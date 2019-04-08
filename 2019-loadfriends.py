from model import db, Volunteer, Shift, VolunteerRelation
import csv

def print_all_volunteers():
    all_volunteers = Volunteer.select().order_by(Volunteer.name)
    for v in all_volunteers:
        print("%d: %s" % (v.id, v.name))
    print()

def resolve_volunteer(name):
    return list(Volunteer.select().where(Volunteer.name.contains(name)))
    
fp = open('2019-venner.csv')

lines = csv.reader(fp, delimiter=',', quotechar='"')

for row in lines:
    v = list(Volunteer.select().where(Volunteer.email % row[0].lower()).execute())

    if (len(v) == 0):
        continue

    v = v[0]
    
    print("Volunteer: %s" % v.name)
    print("Input: %s" % row[1])
    print()

    i = ""
    while i != "x":
        print("Current friend list: %s" % [friend.name for friend in v.get_friends()])
        i = input("Friend: ")

        if i == "l":
            print_all_volunteers()
        else:
            friends = resolve_volunteer(i.strip())

            if len(friends) == 1:
                relation = VolunteerRelation()
                relation.volunteer = v
                relation.likes = friends[0]
                relation.save()
                print(relation)

                v.has_had_friends_added = True
                v.save()
            

    
