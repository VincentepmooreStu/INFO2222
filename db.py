'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
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
def inset_friendship(user1: str, user2: str):
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
        exists = session.query(Friendship).filter_by(friendshipID=friendshipID1).first() is not None

# returns all friends for user
def get_friendships(username: str):
    with Session(engine) as session:
        query = f'SELECT friend_2 FROM friendship WHERE friend_1={username}'
        result = session.execute(text(query))
        values = result.fetchall()
        #for friend in values:
            #friend = friend.strip(",()")
        return values