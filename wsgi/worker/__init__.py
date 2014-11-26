from itertools import cycle, izip, takewhile, dropwhile
from datetime import datetime, date, timedelta

from flask import Blueprint, make_response
from icalendar import Calendar, Event


FIRST_DAY = date(2014, 11, 12)
FORMULA = '1111022220333300'
SUMMARY = {
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
    past = lambda (d, _): d < today - timedelta(days=31)
    future = lambda (d, _): d < today + timedelta(days=31)
    return takewhile(future,
                     dropwhile(past,
                               izip(days(FIRST_DAY),
                                    cycle(FORMULA))))


worker = Blueprint('worker', __name__)


@worker.route('/')
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
        event.add('summary', SUMMARY[type_])
        event['dtstamp'].to_ical()
        event['dtstart'].to_ical()
        event['dtend'].to_ical()
        calendar.add_component(event)
    response = make_response(calendar.to_ical())
    response.headers['Content-Type'] = 'text/calendar;charset=utf-8'
    response.headers['Content-Disposition'] = (
        'inline; filename="worker-day-%s.ics"' % day.isoformat())
    return response
