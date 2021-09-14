import model, loader, peewee

v = loader.get_volunteers_from_csv()

for volunteer in v:
    try:
        volunteer.save()
        print("Added: %s " % volunteer)
    except peewee.IntegrityError as exc:
        print(exc)
