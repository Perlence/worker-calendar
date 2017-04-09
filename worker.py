import json
from datetime import datetime, date, timedelta
from hashlib import md5
from itertools import cycle, izip, takewhile, dropwhile
from os import path
from warnings import warn

from flask import Flask, Blueprint, make_response
from icalendar import Calendar, Event


DEFAULT_CFG = {
    'FIRST_DAY': date(2017, 4, 2),
    'FORMULA': '3333002222011110',
    'SUMMARY': {
        '0': 'Day out',
        '1': 'First shift',
        '2': 'Second shift',
        '3': 'Third shift',
    }
}

worker = Blueprint('worker', __name__)


@worker.route('/')
def index():
    cfg = load_config('config.json')

    calendar = Calendar()
    calendar['prodid'] = '-//worker-perlence//Worker calendar'
    calendar['version'] = '2.0'
    calendar['x-wr-calname'] = 'Worker calendar'
    for day, shift in workdays(cfg['FORMULA'], cfg['FIRST_DAY']):
        if shift == '0':
            continue
        event = Event()
        event.add('uid', 'WORKER-DAY-' + day.isoformat())
        event.add('dtstamp', datetime.now())
        event.add('dtstart', day)
        event.add('dtend', day + timedelta(days=1))
        event.add('summary', cfg['SUMMARY'][shift])
        event['dtstamp'].to_ical()
        event['dtstart'].to_ical()
        event['dtend'].to_ical()
        calendar.add_component(event)

    data = calendar.to_ical()
    cache_bust = md5(data).hexdigest()[:7]

    response = make_response(data)
    response.headers['Content-Type'] = 'text/calendar;charset=utf-8'
    response.headers['Content-Disposition'] = (
        'inline; filename="worker-day-%s.ics"' % cache_bust)
    return response


def load_config(filename):
    abspath = path.join(path.dirname(__file__), filename)
    try:
        with open(abspath) as fp:
            config = json.load(fp)
    except IOError:
        warn('No user config found')
        config = {}
    first_day = config.get('FIRST_DAY')
    if first_day is not None:
        config['FIRST_DAY'] = datetime.strptime(first_day, '%Y-%m-%d').date()
    return dict(DEFAULT_CFG, **config)


def workdays(formula, first_day):
    today = date.today()
    past = lambda (d, _): d < today - timedelta(days=31)
    future = lambda (d, _): d < today + timedelta(days=31)
    return takewhile(future,
                     dropwhile(past,
                               izip(days(first_day),
                                    cycle(formula))))


def days(start):
    day = start
    while True:
        yield day
        day += timedelta(days=1)


if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(worker)
    app.run('127.0.0.1', debug=True)
