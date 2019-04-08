import sys, os
from model import *
from twilio.rest import Client
import datetime
import secrets

client = Client(secrets.TWILIO_ACCOUNT, secrets.TWILIO_TOKEN)

GRACE_TIME_MINUTES = 20
MESSAGE_TEMPLATE = "Hej %s 😘! Husk at du har en vagt kl. %s: %s"


def sms_volunteer(volunteer, message):
    message = client.messages.create(to=volunteer.phone_number,
                                     from_="ROD Vagt",
                                     body=message)

if __name__ == '__main__':
    if (len(sys.argv) > 1):
        if sys.argv[1] == 'zero':
            for vsr in VolunteerShiftRelation.select():
                vsr.has_had_reminder = False
                vsr.save()
    
    shifts = Shift.select()
    for shift in shifts:
        now = datetime.datetime.now()
        minutes_to_shift = (shift.starts - now).total_seconds()/60


        if minutes_to_shift > 0 and minutes_to_shift <= GRACE_TIME_MINUTES:
            print("%s , %s" % (shift, minutes_to_shift))

            for v in shift.get_volunteers():
                vsr = VolunteerShiftRelation.select().where(VolunteerShiftRelation.volunteer == v).where(VolunteerShiftRelation.shift == shift)[0]

                if vsr.has_had_reminder == False:
                    message = MESSAGE_TEMPLATE % (v.get_first_name(), shift.starts.strftime("%H:%M"), shift.title)

                    # print(message)
                    sms_volunteer(v, message)
                    
                    vsr.has_had_reminder = True
                    vsr.save()
