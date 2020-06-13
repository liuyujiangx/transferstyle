from datetime import datetime

from app import db



class Spotinf(db.Model):
    __tablename__ = 'spotinf'
    spotid =db.Column(db.Integer,primary_key = True)
    spotname = db.Column(db.String)
    userid = db.Column(db.Integer)

    def __repr__(self):
        return "<Spotinf %r>" % self.spotname

class Articles(db.Model):
    __tablename__ = 'articles'
    articleid =db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    imgurl = db.Column(db.String)
    spotid = db.Column(db.Integer)
    good = db.Column(db.Integer)
    time = db.Column(db.String)
    username = db.Column(db.String)
    userid = db.Column(db.String)


    def __repr__(self):
        return "<Articles %r>" % self.articleid

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    articleid = db.Column(db.Integer)
    commentitem = db.Column(db.String)
    commentid = db.Column(db.Integer)
    commentname = db.Column(db.String)
    time = db.Column(db.String)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))

    def __repr__(self):
        return "<Comment %r>" % self.id

class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)
    userurl = db.Column(db.String)
    comment = db.relationship("Comment", backref='user')
    def __repr__(self):
        return "<Comment %r>" % self.id

class Userarticle(db.Model):
    __tablename__ = 'userarticle'
    userid = db.Column(db.Integer, primary_key=True)
    articleid = db.Column(db.Integer)
    def __repr__(self):
        return "<Userarticle %r>" % self.userid



