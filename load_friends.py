from model import Volunteer, VolunteerRelation
import peewee

def print_all_volunteers():
    all_volunteers = Volunteer.select().order_by(Volunteer.name)
    for v in all_volunteers:
        print("%d: %s" % (v.id, v.name))
    print()


print_all_volunteers()

no_friends = Volunteer.select().where(Volunteer.has_had_friends_added == False)

for v in no_friends:
    print("Volunteer: %s" % v.name)
    print("Input: %s" % v.wants_to_work_with_string)
    print()

    i = ""
    while i != "x":
        print("Current friend list: %s" % [relation.likes.name for relation in VolunteerRelation.select().where(VolunteerRelation.volunteer == v)])
        i = input("Friend: ")
        try:
            ii = int(i)
            friend = Volunteer.get(Volunteer.id == ii)
        
            relation = VolunteerRelation()
            relation.volunteer = v
            relation.likes = friend
            relation.save()
            print(relation)

            v.has_had_friends_added = True
            v.save()
        except ValueError:
            pass
            
        if i == "l":
            print_all_volunteers()
