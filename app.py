'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, session
from flask_socketio import SocketIO
import db
import secrets
from hashlib import sha256
from datetime import timedelta
import ssl
#hiii

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
app.config['SESSION_COOKIE_HTTPONLY'] = True # ensire JavaScript cannot access the session cookie.

socketio = SocketIO(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    if not username.isalnum():
        return "Error: Invalid user"
    
    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    if user.password != password:
        return "Error: Password does not match!"
    
    return url_for('home', username=username)

@app.route("/logout")
def logout():
    session.clear()  # clears session data
    return index()


# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")
    
    if not username.isalnum() or len(username) > 12:
        return "Please only use letters or numbers for your username."
    
    if db.get_user(username) is None:
        db.insert_user(username, password)
        return url_for('home', username=username)
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

@app.route("/fetch_friends")
def fetch_friends(username: str):
    return db.get_friendships(username)

# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    friends = db.get_friendships(request.args.get("username")) # get friends
    requests = db.get_friend_requests(request.args.get("username")) # get friend requests
    return render_template("home.jinja", username=request.args.get("username"), friend_list = friends, requests=requests)


if __name__ == '__main__':
    #socketio.run(app)
    app.run(ssl_context=("localhost+2.pem", "localhost+2-key.pem"))
    

