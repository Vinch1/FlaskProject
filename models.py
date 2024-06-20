from itsdangerous import URLSafeTimedSerializer as Serializer
from exts import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from flask import current_app
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)
    avatar = db.Column(db.String(100), nullable=True)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], 'confirmation')
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, max_age=3600):
        s = Serializer(current_app.config['SECRET_KEY'], 'confirmation')
        try:
            user_id = s.loads(token.encode('utf-8'),max_age=max_age)['user_id']
        except:
            return None
        return User.query.get(user_id)

class EmailCaptchaModel(db.Model):
    __tablename__ = 'email_captcha'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    captcha = db.Column(db.String(100), nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)

class QuestionModel(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)

    #外键
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('questions', lazy='dynamic'))

class AnswerModel(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    #外键
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #关系
    question = db.relationship('QuestionModel', backref=db.backref('answers', order_by=create_time.desc(), lazy='dynamic'))
    author = db.relationship('User', backref='answers')

