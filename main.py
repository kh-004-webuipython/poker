# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room, disconnect
from flask_pymongo import PyMongo
from random import choice


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'pdb'
app.config['MONGO_URI'] = 'mongodb://admin:adminpass@ds149040.mlab.com:49040' \
                          '/pdb'


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


# def update_state(q):
#     issue_list = []
#     for issue in q['issues']:
#         issue_list.append({'id': issue['id'],
#                            'title': issue['title'],
#                            'description': issue['description'],
#                            'estimation': issue['estimation']})
#     user_list = []
#     for teammate in q['team']:
#         user_list.append({'id': teammate['id'],
#                           'name': teammate['name'],
#                           'role': '',
#                           'current_vote': ''})
#     state_dict = {
#         "user_list": user_list,
#         "issue_list": issue_list,
#         "chat_log": []
#     }
#     return state_dict
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
            "issue_list":  update_state(q),
            "chat_log": []
        }
        return True
    return False


# room page
@app.route('/room/<room_name>/', methods=['GET'])
def main_room_page(room_name=None):
    user_id = request.headers.get('user_id')
    # if not user_id:
    #     return redirect('http://localhost:8000/')
    # user_id = json['Authorization']['username']
    return render_template('index.html', room_name=str(room_name),
                           user_id=str(user_id))


@app.route('/create_room/', methods=['POST'])
def create_room():
    # change for url from jiller
    url = 'http:// localhost: 8000/'
    issue_json = request.get_json(force='True')
    create_room_db(issue_json)
    return redirect(url)


'''
    headers = {'Content-Type': 'application/json',
               'user_id': request.session['user_id']}

request.session['user_id'] = str(user.pk)
'''


@app.route('/add_issue/', methods=['POST'])
def add_issue():
    issue_json = request.get_json(force='True')
    issue = room_db.db.issues
    for issues in issue_json:
        try:
            q = issue.find_one({'project_id': int(issues["project_id"]),
                                'id': int(issues['id'])})
        except Exception:
            print ("Can't read database")
        else:
            if not q:
                issue.insert_one(issues)

    url = '/room/' + str(issue_json[0]["project_id"]) + '/'
    return redirect(url)


@socketio.on('join')
def on_join(data):
    #username = data['username']
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
    #username = data['username']
    room = int(data['room'])
    leave_room(room)
    send('user has left the room.', room=room)


# state = {
#     'room_500': {
#         'user_list': [
#             {
#                 'id': 1,
#                 'name': 'phobos',
#                 'role': 'developer',
#                 'current_vote': ''
#             },
#             {
#                 'id': 2,
#                 'name': 'scrum_name',
#                 'role': 'scrum',
#                 'current_vote': ''
#             },
#
#         ],
#         'issue_list': [
#             {
#                 'id': 1,
#                 'title': 'Fix Email Notification(Issues change)',
#                 'description': 'Email notification has to work for: 1) ' +
#                                'Employee was assigned to the issue. 2) ' +
#                                'Employee that was assigned to the issue, ' +
#                                'now is not assigned to the issue. 3) If ' +
#                                'issue was changed in any way, it sends to ' +
#                                'assigned issue employee. if NOTHING is ' +
#                                'changed, do not send anything.',
#                 'estimation': '',
#             },
#             {
#                 'id': 2,
#                 'title': 'Profile access',
#                 'description': 'Make access to user profile via dropdown(as it was before) and make it bigger',
#                 'estimation': 10,
#             },
#             {
#                 'id': 3,
#                 'title': 'title3',
#                 'description': 'description3',
#                 'estimation':'',
#             },
#
#         ],
#         'chat_log': [
#             {
#                 'id': 1,
#                 'user': 'phobos',
#                 'body': ' xxxxxxxxxxxxx'
#             },
#             {
#                 'id': 2,
#                 'user': 'scrum',
#                 'body': 'zzzzzzzz'
#             },
#         ]
#
#     },
# }
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
    del(state[room])
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