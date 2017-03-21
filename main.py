import os
import sqlite3

from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'poker.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='test'
))
#app.config['SECRET_KEY'] = 'mysecret'
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/link/')
@app.route('/link/<name>')
def main_page1(name=None):
    return render_template('index.html', link=name)

socketio = SocketIO(app)
@socketio.on('message')
def hendleMessage(msg):
    print ('Messega: ' + msg)
    send(msg, broadcast=True)

@socketio.on('URI_link')
def handle_json(json):
    print('received json: ' + str(json))
    send(json, json=True, namespace='URI_link')


@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))



if __name__ == '__main__':
    socketio.run(app)


