from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import datetime


db = SQLAlchemy()


class User(db.Model):
    __tablename__  = 'user'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)  
    password = db.Column(db.String, nullable=False)   
    rel_list = db.relationship("List")
    
    
class List(db.Model):
    __tablename__ = 'list'
    lid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("user.uid"), nullable=False)
    cards = db.relationship("Card",cascade="all, delete")

    
class Card(db.Model):
    __tablename__ = 'card'
    cid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_title =  db.Column(db.String , nullable = False)
    content = db.Column(db.String(120),  nullable=False)
    deadline = db.Column(db.String, server_default=func.now())
    flag = db.Column(db.String)
    list_id = db.Column(db.Integer, db.ForeignKey("list.lid"), nullable=False)
    last_change=db.Column(db.String, onupdate=datetime.datetime.now())
    card_created=db.Column(db.String, server_default=func.now())

