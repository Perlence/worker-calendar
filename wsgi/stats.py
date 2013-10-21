import os

from flask import Flask, Response, request, render_template, abort

import skypelog

app = Flask(__name__)
app.template_folder = 'static/templates'

DATA_PATH = 'static/data/club.txt'

def relopen(name):
    return open(os.path.join(os.path.dirname(__file__), name))

@app.route('/')
def club():
    year    = request.args.get('year')
    month   = request.args.get('month')
    day     = request.args.get('day')
    groupby = request.args.get('groupby') or 'week'

    log = skypelog.SkypeLog()
    try:
        print os.path.abspath(__file__)
        fp = relopen(DATA_PATH)
        log.load(fp)
    except IOError:
        abort(404)

    try:
        rows = skypelog.club(log.querydate(year, month, day), groupby=groupby)
    except ValueError:
        abort(400)
    
    return render_template('index.html', 
                           members=skypelog.MEMBERS, 
                           rows=rows)

if __name__ == '__main__':
    app.run('127.0.0.1', 8000, debug=True)
