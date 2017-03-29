# -*- coding: utf-8 -*-

import os
import sqlite3

from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from flask_pymongo import PyMongo
from random import choice


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'pocker_db'
app.config['MONGO_URI'] = 'mongodb://admin:pockeradmin@ds139480.mlab.com' \
                          ':39480/pocker_db'

app.config.from_envvar('POKER_SETTINGS', silent=True)


room_db = PyMongo(app)

def create_room_db(issue_json):
    room = room_db.db.rooms
    q = room.find_one({'project_id': issue_json["project_id"]})
    # room.update_one(q, {'$set': issue_json}, upsert=True)
    if not q:
        issue_json['issues'] = []
        #issue_json["link"] = request.url + str(issue_json["project_id"]) + "/"
        room.insert(issue_json)


def read_room_db(project_id):
    room = room_db.db.rooms
    q = room.find_one({'project_id': project_id}, {'issues': 1, '_id': 0})
    global state
    room_name = 'room_500'
    state[room_name] = dict()
    issue_list = []
    for issue in q['issues']:
        issue_list.append({'id': issue['id'],
                           'title': issue['title'],
                           'description': issue['description'],
                           'estimation': issue['estimation']})
    user_list = []
    for teammate in q['team']:
        user_list.append({'id': teammate['id'],
                          'name': teammate['title'],
                          'role': teammate['role'],
                          'current_vote': teammate['current_vote']})
    state = {
        "user_list": user_list,
        "issue_list": issue_list,
        "chat_log": []
    }
    return state

# global room
#@app.route('/')
#def main_page():
#    # change 1 for dynamic id
#    return render_template('index.html')


# room page
@app.route('/room/<room_name>/')
def main_room_page(room_name=None):
    # get name of user from request
    name_list = ['egepsihora', 'gnom', 'irena']
    user_name = choice(name_list)

    return render_template('index.html', room_name=room_name,
                           user_name=user_name)


# add sockets in our app
socketio = SocketIO(app)

"""
@app.route('/create_room/', methods=['POST'])
def create_room():
    issue_json = request.get_json(force='True')
    create_room_db(issue_json)
    room_name = 'room' + issue_json['project_id']
    return redirect('index.html', room_name=room_name)


@app.route('/add_issue/', methods=['POST'])
def add_issue():
    issue_json = request.get_json(force='True')
    room = room_db.db.rooms
    q = room.find_one({'project_id': issue_json["project_id"]})
    room.update_one(q, {'$set': {'issues': issue_json['issues']}}, upsert=True)
    return redirect('index.html')

"""
@socketio.on('join')
def on_join(data):
    #username = data['username']
    room = data['room']
    # if user in team:
    join_room(room)
    emit('start_data', state['room_500'])
    comment = {}
    comment['id'] = len(state['room_500']['chat_log']) + 1
    comment['body'] = 'user' + ' has entered the room.'
    comment['user'] = 'Server'
    state['room_500']['chat_log'].append(comment)
    emit('add_new_comment', comment, room=room)


@socketio.on('leave')
def on_leave(data):
    # Need add event to clear room, when no one online
    #username = data['username']
    room = data['room']
    leave_room(room)
    send('user has left the room.', room=room)


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
                'estimation': 10,
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
#state = dict()

#
# def read_db(project_id):
#     room = room_db.db.rooms
#     q = room.find_one({'project_id': project_id}, {'issues': 1, '_id': 0})
#     global state
#     room_name = 'room_' + str(project_id)
#     state[room_name] = {}
#     issue_list = []
#     for issue in q['issues']:
#         issue_list.append({'id': issue['id'],
#                           'title': issue['title'],
#                           'description': issue['description'],
#                           'estimation': issue['estimation']})
#     user_list = []
#     for teammate in q['team']:
#         user_list.append({'id': teammate['id'],
#                          'name': teammate['title'],
#                          'role': teammate['description'],
#                          'current_vote': teammate['estimation']})
#     state = {
#         "user_list": user_list,
#         "issue_list": issue_list,
#         "chat_log": []
#     }
#     return state

#state = dict()


@socketio.on('add_comment')
def handle_add_comment(data):
    room = data['room']
    comment = {}
    comment['id'] = len(state['room_500']['chat_log']) + 1
    comment['body'] = data['body']
    comment['user'] = data['user']
    state['room_500']['chat_log'].append(comment)
    emit('add_new_comment', comment, room=room)


@socketio.on('make_vote')
def handle_vote(data):
    room = data['room']
    users = state['room_500']['user_list']
    for user in users:
        if user['id'] == int(data['user_id']):
            user['current_vote'] = data['card']
    emit('make_vote', users, room=room)


@socketio.on('accept_estimation')
def handle_accept(data):
    room = data['room']
    issues = state['room_500']['issue_list']
    # MAKE REST TO DJANGO AND ON success:
        # DELETE ISSUE IN OUR DB
    for issue in issues:
        if issue['id'] == int(data['issue_id']):
            issue['estimation'] = int(data['estimation'])

    users = state['room_500']['user_list']
    for user in users:
        user['current_vote'] = ''

    new_users = state['room_500']['user_list']
    new_issues = state['room_500']['issue_list']
    emit('issue_was_estimated', {'users': new_users, 'issues': new_issues}, room=room)


@socketio.on('reset_estimation')
def handle_reset_estimation(data):
    room = data['room']
    users = state['room_500']['user_list']
    for user in users:
        user['current_vote'] = ''
    emit('reset_estimation', users, room=room)


@socketio.on('skip_estimation')
def handle_skip_estimation(data):
    room = data['room']
    users = state['room_500']['user_list']
    for user in users:
        user['current_vote'] = ''
    emit('skip_estimation', users, room=room)

if __name__ == '__main__':
    socketio.run(app)