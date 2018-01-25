import csv

def resolve_driver(i):
    if i == "Ja": return 1
    if i == "Nej": return 0
    if i == "Jeg har kørekort men er helst fri for at køre": return 0.5

def resolve_has_car(i):
    if i.lower() == "ja": return 1

    return 0

def resolve_times(i):
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
    
    return(out)

# 17,18,19
def resolve_driver_choices(i):
    if i == "Det er tiptop": return 4
    if i == "Det har jeg det okay med": return 3
    if i == "Det vil jeg helst undgå": return 2
    if i == "Det har jeg det skidt med": return 1
    if i == "Jeg har ikke kørekort": return 0

    return -1
    

# 20,21,22,23
def resolve_shift_type_choices(i):
    if i == "Det synes jeg er mega fedt!": return 3
    if i == "Det har jeg det fint med": return 2
    if i == "Det vil jeg helst ikke": return 1
    if i == "Det vil jeg meget gerne undgå": return 0
    return -1


with open('frivillige.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=",", quotechar="\"")

    first_line = True
    for line in reader:
        
        if first_line:
            first_line = False
            continue
            
        name = line[1]
        driver = resolve_driver(line[8])
        has_car = resolve_has_car(line[9])

        sober_day = resolve_driver_choices(line[17])
        sober_sleeping_night = resolve_driver_choices(line[18])
        sober_wake_night = resolve_driver_choices(line[19])
        
        late_night = resolve_shift_type_choices(line[20])
        kitchen = resolve_shift_type_choices(line[21])
        bar = resolve_shift_type_choices(line[22])
        high_tempo = resolve_shift_type_choices(line[23])
        
        print(name)
#       print(resolve_times(line[11]))
#       print(sober_day, sober_sleeping_night, sober_wake_night)
#       print(late_night, kitchen, bar, high_tempo)
