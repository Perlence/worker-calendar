from itertools import cycle, izip, takewhile, dropwhile
from datetime import datetime, date, timedelta

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
    calendar['prodid'] = '-//worker-perlence//Worker calendar'
    calendar['version'] = '2.0'
    calendar['x-wr-calname'] = 'Worker calendar'
    for day, type_ in workdays():
        if type_ == '0':
            continue
        event = Event()
        event.add('uid', 'WORKER-DAY-' + day.isoformat())
        event.add('dtstamp', datetime.now())
        event.add('dtstart', day)
        event.add('dtend', day + timedelta(days=1))
        event.add('summary', DESCRIPTION[type_])
        event['dtstart'].to_ical()
        event['dtend'].to_ical()
        calendar.add_component(event)
    response = make_response(calendar.to_ical())
    response.headers['Content-Type'] = 'text/calendar'
    response.headers['Content-Disposition'] = (
        'attachment; filename="worker-day-%s.ics"' % day.isoformat())
    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
