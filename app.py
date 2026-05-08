from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import jsonify

from flask_socketio import SocketIO
from flask_socketio import send

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from datetime import datetime

import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'whisperbox_secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whisperbox.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

db = SQLAlchemy(app)

socketio = SocketIO(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'


class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(300),
        nullable=False
    )


class Message(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    text = db.Column(
        db.String(1000),
        nullable=True
    )

    image = db.Column(
        db.String(300),
        nullable=True
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


@app.route('/')
def home():

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        users = {

            'Bubu': 'Anvitha',

            'Dudu': 'Surya'

        }

        if (
            username in users and
            users[username] == password
        ):

            user = User.query.filter_by(
                username=username
            ).first()

            if not user:

                hashed_password = generate_password_hash(
                    password
                )

                user = User(

                    username=username,

                    password=hashed_password

                )

                db.session.add(user)

                db.session.commit()

            login_user(user)

            return redirect(url_for('chat'))

        return 'Invalid username or password'

    return render_template('login.html')


@app.route('/chat')
@login_required
def chat():

    messages = Message.query.order_by(
        Message.timestamp
    ).all()

    return render_template(

        'chat.html',

        messages=messages,

        username=current_user.username

    )


@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('login'))


@app.route(
    '/delete_message/<int:message_id>',
    methods=['POST']
)
@login_required
def delete_message(message_id):

    message = Message.query.get(message_id)

    if message:

        db.session.delete(message)

        db.session.commit()

        return jsonify({
            'success': True
        })

    return jsonify({
        'success': False
    })


@app.route(
    '/upload',
    methods=['POST']
)
@login_required
def upload():

    image = request.files['image']

    text = request.form.get('text')

    filename = image.filename

    image.save(

        os.path.join(

            app.config['UPLOAD_FOLDER'],

            filename

        )
    )

    new_message = Message(

        username=current_user.username,

        text=text,

        image=filename

    )

    db.session.add(new_message)

    db.session.commit()

    return jsonify({
        'success': True
    })


@socketio.on('message')
def handle_message(data):

    username = data['username']

    text = data['text']

    new_message = Message(

        username=username,

        text=text

    )

    db.session.add(new_message)

    db.session.commit()

    send({

        'id': new_message.id,

        'username': username,

        'text': text,

        'time': datetime.now().strftime('%H:%M')

    }, broadcast=True)


@socketio.on('typing')
def typing(data):

    socketio.emit(
        'typing',
        data
    )


if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    socketio.run(

        app,

        host='0.0.0.0',

        port=5000

    )