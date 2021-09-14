import model, loader, peewee

shifts = loader.get_shifts_from_csv()

for s in shifts:
    s.save()
