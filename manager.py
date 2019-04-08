from flask import Flask, render_template
import json
from model import *
#import locale
#locale.setlocale(locale.LC_ALL, "da_DK")

app = Flask(__name__)

app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True
)

@app.template_filter('roddate')
def roddate(value):
    weekday = WEEKDAYS[int(value.strftime("%w"))]
    month = MONTHS[int(value.strftime("%-m"))]
    return weekday + " " + value.strftime("d. %-d. ") + month + value.strftime(" kl. %H:%M")

@app.template_filter('hour')
def hour(value):
    return value.strftime("%H:%M")


@app.route("/")
def list_of_volunteers():
    volunteers = Volunteer.select().order_by(Volunteer.name)
    return render_template('list.html', volunteers=volunteers)

@app.route("/volunteer/<int:vid>")
def volunteer(vid):
    volunteer = Volunteer.select().where(Volunteer.id == vid)[0]
    shifts = volunteer.get_shifts()

    specials = [{
        'title': 'ROD starter :D',
        'start': '2019-04-13 14:00',
        'end': '2019-04-13 15:00',
        'color': 'white',
        'borderColor': 'red'
    },{
        'title': 'ROD slutter :\'(',
        'start': '2019-04-19 14:00',
        'end': '2019-04-19 15:00',
        'color': 'white',
        'borderColor': 'red'
    },
    
    ]
    
    shifts_json = json.dumps([{"title": s.title, "start": s.starts.strftime("%Y-%m-%d %H:%M"), "end": s.ends.strftime("%Y-%m-%d %H:%M"), "borderColor": "#ffeaa7", "color": "#fafad2"} for s in shifts] + specials)

    return render_template('volunteer.html', volunteer=volunteer, shifts=shifts, shifts_json=shifts_json)

@app.route("/shifts")
def shifts():
    shifts = Shift.select().order_by(Shift.starts)

    return render_template('shifts.html', shifts=shifts)

@app.route("/overview")
def hello():
    shifts = Shift.select()
    volunteers = Volunteer.select()
    
    return render_template('overview.html', shifts=shifts, volunteers=volunteers)
