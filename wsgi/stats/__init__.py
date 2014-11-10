import os

from flask import Blueprint, request, render_template, abort

from . import skypelog


DATA_PATH = 'static/data/club.txt'

stats = Blueprint('stats', __name__,
                  template_folder='templates',
                  static_folder='static')


def relopen(name):
    return open(os.path.join(os.path.dirname(__file__), name))


@stats.route('/')
def club():
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')
    groupby = request.args.get('groupby', 'week')

    log = skypelog.SkypeLog()
    try:
        fp = relopen(DATA_PATH)
        log.load(fp)
    except IOError:
        abort(404)

    try:
        rows = skypelog.club(log.querydate(year, month, day), groupby=groupby)
    except ValueError:
        abort(400)

    return render_template('stats/index.html',
                           members=skypelog.MEMBERS,
                           rows=rows)
