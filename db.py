'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, subqueryload
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
def insert_user(username: str, password: str, role):
    with Session(engine) as session:
        user = User(username=username, password=password, role=role, muted=False)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)

def get_muted(username):
    with Session(engine) as session:
        return session.get(User, username).muted

def mute_user(username):
    with Session(engine) as session:
        user = session.query(User).filter(User.username == username).first()
        user.muted = True
        session.commit()

def unmute_user(username):
    with Session(engine) as session:
        user = session.query(User).filter(User.username == username).first()
        user.muted = False
        session.commit()

def get_users():
    with Session(engine) as session:
        users =  session.query(User).all()
        return [{'username': user.username,'role': user.role,'muted': user.muted } for user in users]

def get_role(username):
    with Session(engine) as session:
        user = get_user(username)
        return user.role

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

def edit_post(title, new_content):
    with Session(engine) as session:
        name = get_post_content(title)[1]
        article = session.query(Articles).filter(Articles.article_title == title).first()
        article.article_content = new_content
        session.commit()

# Comment db functions

# Add a comment to an article
def add_comment(article_title, content, poster_name):
    with Session(engine) as session:
        article = session.query(Articles).filter(Articles.article_title == article_title).first()
        comment = Comment(content=content, article_title=article_title, comment_poster=poster_name, poster_role=get_role(poster_name))
        article.comments.append(comment)
        session.add(comment)
        session.commit()

# Remove a comment by its ID
def delete_comment(comment_id):
    with Session(engine) as session:
        comment = session.query(Comment).filter(Comment.id == comment_id).first()
        session.delete(comment)
        session.commit()


# Retrieve all comments for a specific article
def get_comments(article_title):
    with Session(engine) as session:
        article = session.query(Articles).filter(Articles.article_title == article_title).options(subqueryload(Articles.comments)).first()
        comments = [(comment.comment_poster, comment.content, comment.id, comment.poster_role) for comment in article.comments]
        return comments
 