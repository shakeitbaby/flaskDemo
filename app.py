from datetime import datetime, timedelta
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from apscheduler.schedulers.background import BackgroundScheduler
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/flaskDemo'
db = SQLAlchemy(app)
scheduler = BackgroundScheduler()


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_desc = db.Column(db.String(120))
    schedule_type = db.Column(db.String(4))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_desc = db.Column(db.String(180))
    schedule_type = db.Column(db.String(4))
    create_date = db.Column(db.Date())
    expire_date = db.Column(db.Date())
    is_completed = db.Column(db.String(4))
    complete_date = db.Column(db.Date())
    is_expired = db.Column(db.String(4))


@app.route('/hello_world')
def hello_world():
    return 'Hello World!'


@app.route('/')
def index():
    results = Todo.query.filter(Todo.is_completed == '0').all()
    return render_template('index.html', results=results)


@app.route('/todo/add')
def todo_add():
    results = Schedule.query.all()
    return render_template('/todo/edit.html', results=results)


@app.route('/todo/save', methods=['POST'])
def todo_save():
    item_desc = request.form.get("item_desc")
    expire_date = request.form.get("expire_date")
    now = datetime.now()
    item = Todo(item_desc=item_desc, schedule_type='0', create_date=now, is_completed='0',
                expire_date=expire_date)
    db.session.add(item)
    db.session.commit()
    return index()


@app.route('/todo/<id>', methods=['PUT'])
def todo_complete(id):
    now = datetime.now()
    todo = Todo.query.get(id)
    todo.is_completed = '1'
    todo.complete_date = now
    db.session.commit()
    return {'code': 200, 'msg': 'success'}


@app.route('/stat')
def stat():
    sql = text('select schedule_type, '
               'case when schedule_type=\'0\' then \'Normal\' '
               '   when schedule_type = \'1\' then \'Daily\' end schedule_name, '
               'count(1) total, '
               'sum(case when is_expired=\'1\' then 1 else 0 end) is_expired '
               'from todo '
               'group by schedule_type ')
    results = list(db.session.execute(sql))
    fig, ax = plt.subplots()
    x = [result[1] for result in results]
    y1 = [result[2] for result in results]
    y2 = [result[3] for result in results]
    ax.bar(x, y1, label='Total')
    ax.bar(x, y2, label='Expired')
    ax.legend()
    ax.set_title('Statistics')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return render_template('stat.html', image=image)


def job_function():
    now = datetime.now()
    with app.app_context():
        db.session.begin()

        # handle expired daily task
        yesterday = now.date() - timedelta(days=1)
        undones = Todo.query.filter(db.func.DATE(Todo.expire_date) == yesterday, Todo.is_completed == '0').all()
        for todo in undones:
            todo.is_expired = '1'

        # generate daily task
        schedule_dailies = Schedule.query.filter(Schedule.schedule_type == '1').all()
        for schedule in schedule_dailies:
            todo = Todo(item_desc=schedule.schedule_desc, schedule_type='1', create_date=now, expire_date=now.date(),
                        is_completed='0')
            db.session.add(todo)

        # generate weekly task
        if now.weekday() == 0:
            schedule_weeklies = Schedule.query.filter(Schedule.schedule_type == '2').all()
            for schedule in schedule_weeklies:
                todo = Todo(item_desc=schedule.schedule_desc, schedule_type='2', create_date=now,
                            expire_date=now.date()+timedelta(days=6), is_completed='0')
                db.session.add(todo)

        # commit
        db.session.commit()


if __name__ == '__main__':
    scheduler.add_job(job_function, 'cron', minute=0, hour=2)
    scheduler.start()
    app.run(host='0.0.0.0')
