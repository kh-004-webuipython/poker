const USER = 'phobos';
const ROOM = document.querySelector('body').dataset['room'];

let userList = [];
let issueList = [];
let chatLog = [];
let currentIssue = 0;

/*
if (location.pathname.substr(1,4) === 'room') {
    //ROOM = location.pathname.replace(/^\/room\/|\/$/g, '')
}
*/
let socket = io.connect('http://127.0.0.1:5000');
socket.on('connect', () => socket.send('User has connected!') );

socket.on('start_data', (data) => {
    userList = data.user_list;
    issueList = data.issue_list;
    chatLog = data.chat_log;






/*
var socket = io.connect('http://localhost');
socket.on('news', function (data) {
  console.log(data);
  socket.emit('my other event', { my: 'data' });
});


$(document).ready(function() {
	var socket = io.connect('http://127.0.0.1:5000');
	socket.on('connect', function() {
		socket.send('User has connected!');
	});
	socket.on('message', function(msg) {
		$("#messages").append('<li>'+msg+'</li>');
		console.log('Received message');
	});
	$('#sendbutton').on('click', function() {
		socket.send($('#myMessage').val());
		$('#myMessage').val('');
	});
});

*/


let cardList = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, '?', 'coffe'];
// auto
let status = {
    'flip': true,

};


class PokerBox extends React.Component {
    render() {
        return (
            <div>
                <h3>Jiller planning poker service
                    <div className="profile">{USER}</div>
                </h3>
                <IssueBox />
                <UserBox />
                <CommentBox />
            </div>
        );
    }
}


class UserBox extends React.Component {
    render() {
        const users = this._getUsers();
        return (
            <div className="user-box col-md-3 col-sm-2 pull-right">
                <h4 className="user-count">{ userList.filter(x => x.online).length }
                    user online</h4>
                <div className="user-list">
                    { users }
                </div>
            </div> );
    }

    _getUsers() {
        return (userList.map(user => {
                return <User name={user.name} role={user.role}
                             online={user.online} choose={user.choose}
                             key={user.id}/>
            })
        )
    };
}

class User extends React.Component {
    render() {
        return (
            <div className="user">
                <p>{this.props.name}</p>
                <p>{this.props.role}</p>
                <p>{this.props.choose}</p>
            </div> );
    }
}


class IssueBox extends React.Component {
    constructor() {
        super();
        this.state = {

            // TODO Добавить сюда получение данных из сокета  на сокет
            'issueList': issueList
        };
    }


    render() {
        return (
            <div className="main-block col-md-9">
                <div className="info info-striped">
                    <div className="info-row">
                        <div className="info-name">Issue on estimation:</div>
                        <div className="info-value">{this.state.issueList[currentIssue].title}</div>
                    </div>
                    <div className="info-row">
                        <div className="info-name">Description:</div>
                        <div className="info-value">{this.state.issueList[currentIssue].description}</div>
                    </div>
                </div>
                <div className="card-box">
                    <CardBox />
                </div>
                <IssueNavbar />
            </div>
        );
    }
}


class CardBox extends React.Component {
    render() {
        return (<div>
            {
                cardList.map((card, index) => {
                    return <div className="card" key={index}>
                        <div className="card-top-data">{card}</div>
                        <div className="card-center-data">{card}</div>
                        <div className="card-bottom-data">{card}</div>
                    </div>
                })
            }
        </div>)
    }
}

class IssueNavbar extends React.Component {
    render() {
        return (
            <div className="issue-bar">
                <button className="active">Active issue
                </button>
                <button className="completed">Completed issue
                </button>
                <button className="issue-list">All issue list
                </button>
            </div>
        )
    }
}


class CommentBox extends React.Component {

    constructor() {
        super();
        this.state = {
            'comments': chatLog
        };
    };
    componentWillMount() {
        this._addNewComment();
    }

    render() {
        let comments = this._getComments();
        return (
            <div className="col-md-12 col-sm-10">
                <CommentForm addComment={this._sendComment.bind(this)}/>
                <div className="comment-box"> { comments } </div>
            </div>
        );
    }

    _addNewComment() {
        socket.on('addNewComment', newComment => {
            this.setState({comments: this.state.comments.concat([newComment])});
        });

    }
    _sendComment(user, body) {
        const comment = {
            id: this.state.comments.length + 1,
            user,
            body
        };
        socket.emit('addComment', comment);
    }

    _getComments() {
        return this.state.comments.map(comment => {
            return (
                <Comment
                    user={comment.user}
                    body={comment.body}
                    key={comment.id} />
            );
        });
    };

}


class CommentForm extends React.Component {
    render() {
        return (
            <form onSubmit={this._handleSubmit.bind(this)}>
                <div className="input-group">
                    <input className="form-control form-group" placeholder="Type your comment there" ref={(input) => this._body = input} />
                        <div className="input-group-btn">
                            <button className="btn btn-info no-radius" type="submit">Post comment <i className="glyphicon glyphicon-share-alt"></i>
                            </button>
                        </div>
                </div>
            </form>
        );
    }

    _handleSubmit(event) {
        event.preventDefault();
        let body = this._body.value;
        if (body) {
            this.props.addComment(USER, body);
        this._body.value = '';
        }

    }
}


class Comment extends React.Component {
    render() {
        return (
            <div className="comment">
                <p>{this.props.user}</p>
                <p>{this.props.body}</p>
            </div> );
    }
}


ReactDOM.render(
    <PokerBox />, document.getElementById('poker-app')
);

});