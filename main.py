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
app.config.from_envvar('POKER_SETTINGS', silent=True)

# home page
@app.route('/')
def main_page():
    return render_template('index.html')

# room page
@app.route('/room/<room_name>/')
def main_room_page(room_name=None):
    return render_template('index.html', room_name=room_name)

# add sockets in our app
socketio = SocketIO(app)

state = {
    'room_500': {
        'user_list': [
            {
                'id': 1,
                'name': 'phobos',
                'role': 'developer',
                'current_vote': ''
            },
            {
                'id': 2,
                'name': 'scrum_name',
                'role': 'scrum',
                'current_vote': ''
            },

            {
                'id': 3,
                'name': 'PO',
                'role': 'PO',
                'current_vote': ''
            },

        ],
        'issue_list': [
            {
                'title': 'Fix Email Notification(Issues change)',
                'description': 'Email notification has to work for: 1) ' +
                               'Employee was assigned to the issue. 2) ' +
                               'Employee that was assigned to the issue, ' +
                               'now is not assigned to the issue. 3) If ' +
                               'issue was changed in any way, it sends to ' +
                               'assigned issue employee. if NOTHING is ' +
                               'changed, do not send anything.',
                'estimation': 10,
            },
            {
                'title': 'Profile access',
                'description': 'Make access to user profile via dropdown(as it was before) and make it bigger',
                'estimation':'',
            },
            {
                'title': 'title3',
                'description': 'description3',
                'estimation':'',
            },

        ],
        'chat_log': [
            {
                'id': 1,
                'user': 'phobos',
                'body': ' xxxxxxxxxxxxx'
            },
            {
                'id': 2,
                'user': 'scrum',
                'body': 'zzzzzzzz'
            },
        ]

    },
}

@socketio.on('connect')
def handle_connect():
    emit('start_data', state['room_500'])


@socketio.on('add_comment')
def handle_add_comment(comment_obj):
    comment_obj['id'] = len(state['room_500']['chat_log']) + 1
    state['room_500']['chat_log'].append(comment_obj)
    emit('add_new_comment', comment_obj, broadcast=True)


@socketio.on('make_vote')
def handle_vote(vote_obj):
    users = state['room_500']['user_list']
    for user in users:
        if user['id'] == vote_obj['user_id']:
            user['current_vote'] = vote_obj['card']
            print user['current_vote']
    emit('make_vote', users, broadcast=True)


"""
@socketio.on('chat_event')
def handle_json(json):
    print('received json: ' + str(json))
    room = state[json['room']]
    if room['chat']:
       room['chat'].push(json['message'])
    send(json, json=True, namespace='chat_event', broadcast=True)


@socketio.on('URI_link')
def handle_json(json):
    print('received json: ' + str(json))
    send(json, json=True, namespace='URI_link')


@socketio.on('message')
def hendleMessage(msg):
    print ('Messega: ' + msg)
    send(msg, broadcast=True)


@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

"""





if __name__ == '__main__':
    socketio.run(app)


