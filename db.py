'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from models import *
import string

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)

# inserts friendship into database
def insert_friendship(user1: str, user2: str):
    with Session(engine) as session:
        friendshipID1 = user1 + user2
        friendshipID2 = user2 + user1
        if check_friendship_exists(user1, user2):
            print('Friend already exists')
            return #insert friend already exists msg
        else: 
            friendship1 = Friendship(friendshipID=friendshipID1, friend_1=user1, friend_2=user2)
            friendship2 = Friendship(friendshipID=friendshipID2, friend_1=user2, friend_2=user1)
            session.add(friendship1)
            session.add(friendship2)
            session.commit()

#checks if friendship already exists
def check_friendship_exists(user1: str, user2: str) -> bool:
    with Session(engine) as session:
        friendshipID1 = user1 + user2
        friendshipID2 = user2 + user1
        return session.query(Friendship).filter_by(friendshipID=friendshipID1).first() is not None

# returns all friends for user
def get_friendships(username: str):
    with Session(engine) as session:
        result = session.execute(session.query(Friendship.friend_2).filter_by(friend_1=username))
        values = result.fetchall()
        friend_list = [v[0] for v in values]
        return friend_list

def send_request(requester, requestee):
    with Session(engine) as session:
        if requester == requestee:
            return "You can't invite yourself!"
        request_outwards_ID = requester + requestee
        request_inwards_ID = requestee + requester

        if check_friendship_exists(requester, requestee):
            return 'Already friends!'
        if session.query(Requests).filter_by(requestID=request_outwards_ID).first() is not None:
            return 'Request already sent!'
        
        if session.query(Requests).filter_by(requestID=request_inwards_ID).first() is not None:
            accept_request(requestee, requester)
            return f'Accepting request from {requestee}'
        print(request_outwards_ID)
        request = Requests(requestID=request_outwards_ID, requester=requester, requestee=requestee)
        session.add(request)
        session.commit()

def accept_request(requester, requestee):
    with Session(engine) as session:
        request_ID = requester + requestee
        request_ID2 = requestee + requester
    
        if session.query(Requests).filter_by(requestID=request_ID).first() is None:
            if session.query(Requests).filter_by(requestID=request_ID2).first() is None:
                return 'No request to accept!'

        sql = delete(Requests).where(Requests.requestID == request_ID)
        sql = delete(Requests).where(Requests.requestID == request_ID2)
        session.execute(sql)
        session.commit()
        insert_friendship(requester, requestee)
        return 1
    
def decline_request(requester, requestee):
    with Session(engine) as session:
        request_ID = requester + requestee
        request_ID2 = requestee + requester
    
        if session.query(Requests).filter_by(requestID=request_ID).first() is None:
            if session.query(Requests).filter_by(requestID=request_ID2).first() is None:
                return 'No request to accept!'

        sql = delete(Requests).where(Requests.requestID == request_ID)
        sql = delete(Requests).where(Requests.requestID == request_ID2)
        session.execute(sql)
        session.commit()
        return 1

def get_friend_requests(username):
    with Session(engine) as session:
        result = session.execute(session.query(Requests.requester).filter_by(requestee=username))
        values = result.fetchall()
        request_list = [v[0] for v in values]
        return request_list

#Article db functions
def add_post(username, title, content):
    with Session(engine) as session:
        article = Articles(article_title = title, article_content = content, poster_name = username)
        session.add(article)
        session.commit()
    
def delete_post(title):
    with Session(engine) as session:
        sql = delete(Articles).where(Articles.article_title == title)
        session.execute(sql)
        session.commit()

def get_post_titles():
    with Session(engine) as session:
        result = session.execute(session.query(Articles.article_title))
        values = result.fetchall()
        titles = [v[0] for v in values]
        return titles

def check_title(title):
    with Session(engine) as session:
        return session.query(Articles).filter_by(article_title=title).first() is not None

def get_post_content(title):
    with Session(engine) as session:
        content = session.execute(session.query(Articles.article_content).filter_by(article_title=title)).fetchall()
        name = session.execute(session.query(Articles.poster_name).filter_by(article_title=title)).fetchall()
        content = content[0][0]
        name = name[0][0]
        print(name)
        return (content, name)