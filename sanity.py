from model import Volunteer, Shift

def DoWeHaveEnoughPeopleForEveryShift():
    for shift in Shift.select():
        if len(shift.find_candidates()) < shift.num_people:
            print(" !! %s is understaffed" % shift.title)
            return False
    return True

def VolunteersDontEndBeforeTheyStart():
    for volunteer in Volunteer.select():
        if volunteer.available_end <= volunteer.available_start:
            return False
    return True

if __name__ == '__main__':
    DoWeHaveEnoughPeopleForEveryShift()
