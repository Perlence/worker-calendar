from flask import Flask

from .stats import stats
from .worker import worker
from elaboratecharts import ElaborateCharts

app = Flask(__name__)
app.register_blueprint(stats, url_prefix='/stats')
app.register_blueprint(worker, url_prefix='/worker')
charts = ElaborateCharts(app, url_prefix='/elaboratecharts')

if __name__ == '__main__':
    app.run(debug=True)
