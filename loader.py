import csv
from datetime import datetime
from model import Volunteer, ShiftSlot


def csv_streamer(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="\"")

        first_line = True
        for line in reader:
            if first_line:
                first_line = False
                continue

            yield(line)

def get_shifts_from_csv():
    shifts = []
    
    for line in csv_streamer('tjanser.csv'):
        shifts.append(ShiftSlot(line))

    return shifts

def get_volunteers_from_csv():
    volunteers = []

    for line in csv_streamer('frivillige.csv'):
        volunteers.append(Volunteer(line))

    return volunteers
