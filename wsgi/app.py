from flask import Flask

from stats import stats

app = Flask(__name__)
app.register_blueprint(stats, url_prefix='/stats')

if __name__ == '__main__':
    app.run(debug=True)
