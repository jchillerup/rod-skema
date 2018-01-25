from datetime import datetime

def parse_datetime(i):
    # Dates from GDocs can look like this: Thu 29/03 13:00
    # Since the output doesn't contain a year, we tack the current one onto
    # the GDocs one
    current_year = datetime.now().year
    new_date_string = "%s %s" % (current_year, i)
    d = datetime.strptime(new_date_string, '%Y %a %d/%m %H:%M')
    
    return d
