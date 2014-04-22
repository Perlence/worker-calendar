from itertools import cycle, izip, takewhile, dropwhile
from datetime import date, timedelta

from flask import Flask, make_response
from icalendar import Calendar, Event


FIRST_DAY = date(2014, 4, 17)
FORMULA = '111102222033330'
DESCRIPTION = {
    '0': 'Day out',
    '1': 'First shift',
    '2': 'Second shift',
    '3': 'Third shift',
}


def days(start):
    day = start
    while True:
        yield day
        day += timedelta(days=1)


def workdays():
    today = date.today()
    month = today + timedelta(days=31)
    drop = lambda (d, _): d < today
    take = lambda (d, _): d < month
    return takewhile(take,
                     dropwhile(drop,
                               izip(days(FIRST_DAY),
                                    cycle(FORMULA))))


app = Flask(__name__)


@app.route('/')
def index():
    calendar = Calendar()
    for day, type_ in workdays():
        event = Event()
        event['uid'] = 'worker-day-' + day.isoformat()
        event['dtstart'] = day
        event['dtend'] = day + timedelta(days=1)
        event['summary'] = DESCRIPTION[type_]
        calendar.add_component(event)
    response = make_response(calendar.to_ical())
    response.headers['Content-Type'] = 'text/calendar'
    response.headers['Content-Disposition'] = (
        'attachment; filename="worker-day-%s.ics"' % day.isoformat())
    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
