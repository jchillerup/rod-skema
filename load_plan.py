from model import Shift, Volunteer, VolunteerShiftRelation

shifts = Shift.select()

def get_names():
    names = []
    while True:
        name = input().rstrip()

        if name == "":
            break;

        names.append(name)

    return names



for shift in shifts:
    print("Loading volunteers for shift %s." % shift)

    cur_vols = VolunteerShiftRelation.select().where(VolunteerShiftRelation.shift == shift)
    for vol in cur_vols:
        print(" - %s" % vol.volunteer.name)
    
    while True:
        names = get_names()

        # Resolve volunteers from names
        for name in names:
            vol = None
            q = Volunteer.select().where(Volunteer.name.contains(name))

            if len(q) == 1:
                vol = q[0]

                vsr = VolunteerShiftRelation(volunteer=vol, shift=shift)
                print("%s - %s" % (vsr.volunteer, vsr.shift))

                vsr.save()
            else:
                print("Ambiguous, please specify: %s" % name)

        if len(names) == 0:
            break
