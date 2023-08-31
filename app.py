from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:lidaning@82.157.147.8:3306/flaskDemo'
db = SQLAlchemy(app)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_desc = db.Column(db.String(120))
    schedule_type = db.Column(db.String(4))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_desc = db.Column(db.Integer)
    create_date = db.Column(db.Date())
    expire_date = db.Column(db.Date())
    is_completed = db.Column(db.String(4))
    complete_date = db.Column(db.Date())

@app.route('/hello_world')
def hello_world():
    return 'Hello World!'


@app.route('/')
def index():
    results = Todo.query.all()
    return render_template('index.html', results=results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
