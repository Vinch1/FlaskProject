import os.path
from flask import Blueprint, render_template, jsonify, redirect, url_for, session, flash
from werkzeug.datastructures import CombinedMultiDict
from PIL import Image
from exts import mail,db
from flask_login import login_user, logout_user, current_user
from flask_mail import Message
from flask import request
import string
import random
from models import EmailCaptchaModel, User
from .forms import RegistrationForm, LoginForm, RequsetResetForm, ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('qa.index'))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("邮箱在数据库中不存在！")
            return redirect(url_for('auth.login'))

        if check_password_hash(user.password, password):
            login_user(user, remember=False)
            next_page = request.args.get('next')
            flash("登录成功", "success")
            return redirect(next_page) if next_page else redirect(url_for("qa.index"))
        else:
            flash("密码错误")
            return redirect(url_for('auth.login'))

    if form.errors:
        flash(form.errors)

    return render_template('login.html', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join('static/images', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if current_user.is_authenticated:
        return redirect(url_for('qa.index'))

    if request.method == 'GET':
        return render_template('register.html', form=form)

    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        avatar = form.avatar.data

        picture_fn = save_picture(avatar)
        save_path = 'images/' + picture_fn

        user = User(email=email, username=username, password=generate_password_hash(password), avatar=save_path)
        db.session.add(user)
        db.session.commit()

        flash('注册成功，请登录。', 'success')
        return redirect(url_for('auth.login'))
    else:
        for error in form.errors.values():
            flash(error[0], 'danger')
        return render_template('register.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('qa.index'))


#默认是get请求
@bp.route('/captcha/email', methods=['GET', 'POST'])
def capture_email():
    email = request.args.get("email")
    source = string.digits*4
    capture = random.sample(source, 4)
    capture = "".join(capture)
    message = Message('flaskProject3注册验证码', recipients=[email],
                      body=f"您的验证码是{capture}")
    mail.send(message)
    #用数据库表的方式存储
    email_captcha = EmailCaptchaModel(email=email, captcha=capture)
    db.session.add(email_captcha)
    db.session.commit()
    #RESTful API
    #{code:200/400/500, message:"", data:{}}
    return jsonify({
        "code": 200,
        "message": "",
        "data": f"{capture}"
    })

# @bp.route('/mail/test')
# def mail_test():
#     message = Message('邮箱测试', recipients=['2370403206@qq.com'], body="this is a test email from Vinchi! HAhahaha A project im working on. miss u! hehe")
#     mail.send(message)
#     return "success sent"

def send_reset_email(user):
    token = user.get_reset_token()
    flash(token)
    msg = Message('Password Reset Request', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('qa.index'))
    form = RequsetResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Check your email for the instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_request.html', form=form, title='Reset Password')


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('qa.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This is an invalid or expired token.', 'warning')
    return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        user.password = generate_password_hash(password)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('auth.login'))
    render_template('reset_token.html', form=form, title='Reset Password')