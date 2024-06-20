import wtforms
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import SubmitField
from wtforms.validators import Email, Length, EqualTo, InputRequired, DataRequired
from models import User, EmailCaptchaModel
from exts import db



class RegistrationForm(FlaskForm):
    email = wtforms.StringField(validators=[Email(message='Wrong format.')])
    captcha = wtforms.StringField(validators=[Length(min=4, max=4, message='Wrong Captcha format.')])
    username = wtforms.StringField(validators=[Length(min=3, max=20, message='Wrong username format.')])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message='Wrong password format.')])
    password_confirm = wtforms.StringField(validators=[EqualTo('password', message='Passwords must match.')])
    avatar = wtforms.FileField(validators=[FileRequired(), FileAllowed(['jpg', 'png', 'gif'], message='wrong file format'), ])
    #自定义验证
    #1、邮箱是否已经
    #2、验证码是否正确
    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            raise wtforms.ValidationError(message='Email already registered.')
    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        captcha_model = EmailCaptchaModel.query.filter_by(email=email, captcha = captcha).first()
        if not captcha_model:
            raise wtforms.ValidationError(message='Captcha is not valid.')
        else:
            #验证完删除
            db.session.delete(captcha_model)
            db.session.commit()



class LoginForm(FlaskForm):
    email = wtforms.StringField(validators=[Email(message='Wrong format.')])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message='Wrong password format.')])
    submit = SubmitField('立即登录')
class QuestionForm(FlaskForm):
    title = wtforms.StringField(validators=[Length(min=3, max=100, message='Wrong title.')])
    content = wtforms.StringField(validators=[Length(min=3, message='Wrong content format.')])

class AnswerForm(FlaskForm):
    content = wtforms.StringField(validators=[Length(min=3, message='Wrong content format.')])
    question_id = wtforms.IntegerField(validators=[InputRequired(message='Must input question id')])

class RequsetResetForm(FlaskForm):
    email = wtforms.StringField(validators=[Email(message='Wrong format.')])
    submit = SubmitField('Request Password Reset')
    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user is None:
            raise wtforms.ValidationError(message='No account with that email. You must register first')

class ResetPasswordForm(FlaskForm):
    password = wtforms.StringField(validators=[Length(min=6, max=20, message='Wrong password format.')])
    password_confirm = wtforms.StringField(validators=[EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Reset Password')