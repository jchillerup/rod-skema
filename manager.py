from flask import Flask, render_template, request
import json
from model import *
from twilio.twiml.messaging_response import MessagingResponse
from sms import sms_volunteer

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

    specials = [
        # {
        #     'title': 'ROD starter :D',
        #     'start': '2019-04-13 14:00',
        #     'end': '2019-04-13 15:00',
        #     'color': 'white',
        #     'borderColor': 'red'
        # },
        # {
        #     'title': 'ROD slutter :\'(',
        #     'start': '2019-04-19 14:00',
        #     'end': '2019-04-19 15:00',
        #     'color': 'white',
        #     'borderColor': 'red'
        # },
        # {
        #     'title': '%s' % volunteer.get_first_name(),
        #     'start': volunteer.available_start.strftime("%Y-%m-%d %H:%M"),
        #     'end': volunteer.available_end.strftime("%Y-%m-%d %H:%M"),
        #     'color': 'white',
        #     'borderColor': 'red'
        # },{
        #     'title': 'ROD slutter :\'(',
        #     'start': '2019-04-19 14:00',
        #     'end': '2019-04-19 15:00',
        #     'color': 'white',
        #     'borderColor': 'red'
        # }, 
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

def find_bar_shift():
    shifts = Shift.select()

    for shift in shifts:
        if shift.title == "Bar" and Shift.starts < datetime.datetime.now() and Shift.ends > datetime.datetime.now():
            return shift

@app.route("/print")
def print():
    shifts = Shift.select().order_by(Shift.title, Shift.starts)

    return render_template('print.html', shifts=shifts)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    # Start our TwiML response
    resp = MessagingResponse()

    # Figure out who is in the bar
    bar_shift = find_bar_shift()

    body = request.values.get('Body', None)
    from_ = request.values.get('From', None)

    for volunteer in bar_shift.get_volunteers():
        sms_volunteer(volunteer, "Besked fra %s: %s" % (from_, body))
    
    # Add a message
    resp.message("Tak skal du have :)")

    return str(resp)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
