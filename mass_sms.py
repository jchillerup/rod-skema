from model import *
import datetime
from sms import sms_volunteer

volunteers = Volunteer.select()

# message = "Kære søde frivillige på ROD. Snart går det løs, og vi er ved at være klar! Husk at tjekke dit skema en ekstra gang på http://rod.rasmusbrinck.se/links.html, for der har lige været nogle sidste-øjebliks-ændringer. Vi glæder os til at se dig! KH Arbejdsgruppen og de frivillig-frivillige"

message = "Hej %s! Så fedt, at du vil være frivillig på ROD! Vagtplanen er klar, og hvis du ikke har set den, så ligger den på http://rodvagt.dk . Siden fungerer bedst på computer indtil videre :)"

def format_date(date):
    return WEEKDAYS[int(date.strftime("%w"))].lower() + date.strftime(" d. %-d kl. %H")

for volunteer in volunteers:
    m = message % (volunteer.get_first_name())
    print(m)
    print()
    sms_volunteer(volunteer, m)



"""
Jakob toft kommer først lørdag (men hvornår?) og bliver han til nedrivning

Lene Nørgaard skal have lavere load pga. hjælp til opstilling
   hvornår rejser hun?

Faste tjanser:
kamil                       opsætning
Dagmar og Mads Almosetoft   nedrivning
Simon                       lydmand

"""
