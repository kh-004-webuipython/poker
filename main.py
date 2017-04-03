# -*- coding: utf-8 -*-
import json

import requests
import sys
from flask import Flask, render_template, request, jsonify, redirect
from flask import Flask, render_template, request, make_response, redirect, \
    session
from flask_socketio import SocketIO, send, emit, join_room, leave_room, \
    disconnect
from flask_pymongo import PyMongo
from random import choice

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'pdb'
app.config['MONGO_URI'] = 'mongodb://admin:adminpass@ds149040.mlab.com:49040' \
                          '/pdb'

app.config['SECRET_KEY'] = 'something unique and secret'
app.config['SESSION_REFRESH_EACH_REQUEST'] = False
app.config.from_envvar('POKER_SETTINGS', silent=True)

room_db = PyMongo(app)
socketio = SocketIO(app)
state = dict()


def create_room_db(issue_json):
    room = room_db.db.rooms
    try:
        q = room.find_one({'project_id': int(issue_json["project_id"])})
    except Exception:
        print("Can't read database")
    else:
        if not q:
            for teammate in issue_json['team']:
                teammate['role'] = ''
                teammate['current_vote'] = ''
            room.insert_one(issue_json)
    return True


def update_state(q):
    state_list = []
    for items in q:
        state_list.append(items)
    return state_list


def read_room_db(project_id):
    room = room_db.db.rooms
    issue = room_db.db.issues
    id = int(project_id)
    global state
    try:
        q_team = room.find_one({'project_id': id}, {'team': 1, '_id': 0})
        q = issue.find({'project_id': id}, {'id': 1, '_id': 0, 'title': 1,
                                            'estimation': 1, 'description': 1})
    except Exception:
        print ("Can't read database")
        disconnect()
    else:
        state[id] = {
            "user_list": q_team['team'],
            "issue_list": update_state(q),
            "chat_log": []
        }
        return True
    return False


# room page
# @app.route('/room/<room_name>/', methods=['GET'])
# def main_room_page(room_name=None, user_id=''):
#     room_name = request.headers.get('room_name')
#     user_id = request.headers.get('user_id')
#     return render_template('index.html', room_name=str(room_name),
#                            user_id=str(user_id))


@app.route('/room/<room_name>/user/<user_id>', methods=['GET'])
def room_page(room_name=None, user_id=''):
    return render_template('index.html', room_name=str(room_name),
                           user_id=str(user_id))


@app.route('/create_room/', methods=['POST'])
def create_room():
    issue_json = request.get_json(force='True')
    create_room_db(issue_json)

    return redirect(request.referrer)


@app.route('/add_issue/', methods=['POST'])
def add_issue():
    issue_json = request.get_json(force='True')
    issue = room_db.db.issues
    for issues in issue_json:
        try:
            q = issue.find_one({'project_id': issues["project_id"],
                                'id': issues['id']})
        except Exception:
            print ("Can't read database")
        else:
            if not q:
                issue.insert_one(issues)
    return redirect(request.referrer)
    # url = '/room/' + str(issue_json[0]["project_id"]) + '/'
    # return redirect(url)


@app.route('/save_issue/<int:issue_id>')
def save_issue(issue_id):
    # get issue
    issues = room_db.db.issues
    try:
        current_issue = issues.find_one({'id': issue_id})
    except:
        print('cant read')
    project_id = current_issue.get('project_id')
    host = 'http://' + request.host.split(':')[
        0] + ':8000/'
    url = host + 'project/' + str(project_id) +'/issue/'+str(issue_id)
    save_url = url + '/save_estimation/'
    # url = 'http://localhost:8000/project/1/issue/12/save_estimation/'
    r = requests.post(save_url, data={'estimation': current_issue.get('estimation')})
    return redirect(url)


@socketio.on('join')
def on_join(data):
    # username = data['username']
    room = int(data['room'])
    # if user in team:
    join_room(room)
    try:
        state[room]
    except Exception:
        state[room] = dict()
        read_room_db(room)
    # drop user on bad DB request
    if not state[room]:
        disconnect()
    emit('start_data', state[room])
    comment = dict()
    comment['id'] = len(state[room]['chat_log']) + 1
    comment['body'] = 'user' + ' has entered the room.'
    comment['user'] = 'Server'
    state[room]['chat_log'].append(comment)
    emit('add_new_comment', comment, room=room)


@socketio.on('leave')
def on_leave(data):
    # Need add event to clear room, when no one online
    # username = data['username']
    room = int(data['room'])
    leave_room(room)
    send('user has left the room.', room=room)


@socketio.on('add_comment')
def handle_add_comment(data):
    room = int(data['room'])
    comment = dict()
    comment['id'] = len(state[room]['chat_log']) + 1
    comment['body'] = data['body']
    comment['user'] = data['user']
    state[room]['chat_log'].append(comment)
    emit('add_new_comment', comment, room=room)


@socketio.on('make_vote')
def handle_vote(data):
    room = int(data['room'])
    users = state[room]['user_list']
    for user in users:
        if user['id'] == int(data['user_id']):
            user['current_vote'] = data['card']
    emit('make_vote', users, room=room)


@socketio.on('accept_estimation')
def handle_accept(data):
    room = int(data['room'])
    issues = state[room]['issue_list']
    # MAKE REST TO DJANGO AND ON success:
    # DELETE ISSUE IN OUR DB
    for issue in issues:
        if issue['id'] == int(data['issue_id']):
            issue['estimation'] = int(data['estimation'])

    users = state[room]['user_list']
    for user in users:
        user['current_vote'] = ''

    new_users = state[room]['user_list']
    new_issues = state[room]['issue_list']
    del (state[room])
    emit('issue_was_estimated', {'users': new_users, 'issues': new_issues},
         room=room)


@socketio.on('reset_estimation')
def handle_reset_estimation(data):
    room = int(data['room'])
    users = state[room]['user_list']
    for user in users:
        user['current_vote'] = ''
    emit('reset_estimation', users, room=room)


@socketio.on('skip_estimation')
def handle_skip_estimation(data):
    room = int(data['room'])
    users = state[room]['user_list']
    for user in users:
        user['current_vote'] = ''
    emit('skip_estimation', users, room=room)


if __name__ == '__main__':
    socketio.run(app)
