'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None: 
        return
    emit("not_connected")
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))
    leave_room(room_id)
    room.leave_room(username)

# send message event handler
@socketio.on("send")
def send(username, message, hmac, room_id):
    emit("incoming_from_user", (username, message, hmac), to=room_id)
    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

    # if the user is already inside of a room 
    if room_id is not None:
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit only to the sender
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now waiting for {receiver_name} to connect.", "green"), to=room_id)
    return room_id

@socketio.on("check_connected")
def check_connection(room_id):
    if len(room.get_users(room_id)) == 2:
        emit("connected", to=room_id)
        return True
    emit("not_connected", to=room_id)
    return False

#receives A and B from clients and sends to other connected client
@socketio.on("send_pub")
def diffie_exchange_helper(pub, is_B, room_id):
    emit("key_pub", (pub, is_B), to=room_id, include_self=False)

@socketio.on("request_shared_keys")
def send_shared_keys():
    p = 26266879083691988639
    g = 7
    return p, g

@socketio.on("display_connection")
def display_connection(room_id):
    if check_connection(room_id):
        emit("incoming", ("You are now connected!", "green"), to=room_id)

@socketio.on("add")
def send_request(username, new_friend):
    if not new_friend.isalnum():
        return "User does not exist!"

    if db.get_user(new_friend) is None:
        return "User does not exist!"
    return db.send_request(username, new_friend)

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    emit("not_connected", to=room_id)
    leave_room(room_id)
    room.leave_room(username)

@socketio.on("accept")
def accept_request(username, requester):
    res = db.accept_request(username, requester)
    return res

@socketio.on("decline")
def accept_request(username, requester):
    res = db.decline_request(username, requester)
    print(res)
    return res
