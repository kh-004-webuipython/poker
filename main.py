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
                'moderator': 1,
                'current_vote': ''
            },
            {
                'id': 2,
                'name': 'scrum_name',
                'role': 'scrum',
                'moderator': 0,
                'current_vote': ''
            },


        ],
        'issue_list': [
            {
                'id': 1,
                'title': 'Fix Email Notification(Issues change)',
                'description': 'Email notification has to work for: 1) ' +
                               'Employee was assigned to the issue. 2) ' +
                               'Employee that was assigned to the issue, ' +
                               'now is not assigned to the issue. 3) If ' +
                               'issue was changed in any way, it sends to ' +
                               'assigned issue employee. if NOTHING is ' +
                               'changed, do not send anything.',
                'estimation': '',
            },
            {
                'id': 2,
                'title': 'Profile access',
                'description': 'Make access to user profile via dropdown(as it was before) and make it bigger',
                'estimation':'',
            },
            {
                'id': 3,
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
    #Add event to clear room, when no one online


@socketio.on('add_comment')
def handle_add_comment(comment_obj):
    comment_obj['id'] = len(state['room_500']['chat_log']) + 1
    state['room_500']['chat_log'].append(comment_obj)
    emit('add_new_comment', comment_obj, broadcast=True)


@socketio.on('make_vote')
def handle_vote(vote_obj):
    users = state['room_500']['user_list']
    for user in users:
        if user['id'] == int(vote_obj['user_id']):
            user['current_vote'] = vote_obj['card']
    emit('make_vote', users, broadcast=True)


@socketio.on('accept_estimation')
def handle_accept(accept_obj):
    issues = state['room_500']['issue_list']
    # MAKE REST TO DJANGO AND ON success:
        # DELETE ISSUE IN OUR DB
    for issue in issues:
        if issue['id'] == int(accept_obj['issue_id']):
            issue['estimation'] = int(accept_obj['estimation'])

    users = state['room_500']['user_list']
    for user in users:
        user['current_vote'] = ''

    new_users = state['room_500']['user_list']
    new_issues = state['room_500']['issue_list']
    emit('issue_was_estimated', {'users': new_users, 'issues': new_issues}, broadcast=True)


@socketio.on('reset_estimation')
def handle_reset_estimation(vote_obj):
    users = state['room_500']['user_list']
    for user in users:
        user['current_vote'] = ''
    emit('reset_estimation', users, broadcast=True)

@socketio.on('skip_estimation')
def handle_reset_estimation(vote_obj):
    users = state['room_500']['user_list']
    for user in users:
        user['current_vote'] = ''
    emit('skip_estimation', users, broadcast=True)





if __name__ == '__main__':
    socketio.run(app)


