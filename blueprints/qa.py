from flask import Blueprint, request, render_template, g, redirect, url_for, flash, abort
from .forms import QuestionForm, AnswerForm
from models import QuestionModel, AnswerModel,User
from exts import db
#from decorators import login_required
from flask_login import login_required
from flask_login import current_user

bp = Blueprint('qa', __name__, url_prefix='/')

#http://127.0.0.1:5000
@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    questions = QuestionModel.query.order_by(QuestionModel.create_time.desc()).paginate(page=page, per_page=4)
    return render_template('index.html', questions=questions)

@bp.route('/user/<string:username>')
def user_questions(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    questions = QuestionModel.query.filter_by(author=user).order_by(QuestionModel.create_time.desc()).paginate(page=page, per_page=4)
    return render_template('user_questions.html', questions=questions, user=user)

@bp.route("/qa/public", methods=["GET", "POST"])
@login_required
def public_question():
    form = QuestionForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        question = QuestionModel(title=title, content=content, author=current_user)
        db.session.add(question)
        db.session.commit()
        # 跳转问答的详情页
        return redirect(url_for('qa.index'))
    else:
        #flash(form.errors, 'danger')
        return render_template('public_question.html', legend = '发布问题', title='Public Question', form=form)
        # return redirect(url_for('qa.public_question'))


@bp.route("/qa/detail/<qa_id>", methods=["GET", "POST"])
def detail_question(qa_id):
    form = AnswerForm()
    question = QuestionModel.query.get_or_404(qa_id)
    answer_count = AnswerModel.query.filter_by(question_id=qa_id).count()
    return render_template('detail.html', question=question, answer_count=answer_count, form=form)

@bp.route('qa/detail/<qa_id>/update', methods=["GET", "POST"])
@login_required
def update_post(qa_id):
    question = QuestionModel.query.get_or_404(qa_id)
    if current_user != question.author:
        abort(403)
    form = QuestionForm()
    if form.validate_on_submit():
        question.title = form.title.data
        question.content = form.content.data
        db.session.commit()
        flash('Update Success', 'success')
        return redirect(url_for('qa.detail_question', qa_id=qa_id))
    elif request.method == "GET":
        form.title.data = question.title
        form.content.data = question.content
    else:
        print(form.errors)

    return render_template('public_question.html',legend='更新问题', title='Update Post', form=form)

@bp.route('qa/detail/<qa_id>/delete', methods=["POST"])
@login_required
def delete_question(qa_id):
    question = QuestionModel.query.get_or_404(qa_id)
    if question.author != current_user:
        abort(403)
    db.session.delete(question)
    db.session.commit()
    flash('Delete Success', 'success')
    return redirect(url_for('qa.index'))

#@bp.route('/answer/public', methods=["POST"])
@bp.post('/answer/public')
@login_required
def public_answer():
    form = AnswerForm()
    if form.validate_on_submit():
        content = form.content.data
        question_id = form.question_id.data
        answer = AnswerModel(content=content, question_id=question_id, author_id=current_user.id)
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('qa.detail_question', qa_id=question_id))
    else:
        print(form.errors)
        return redirect(url_for('qa.detail_question', qa_id=request.form.get("question_id")))

@bp.route('/search')
def search():
    # /search?q=str
    q = request.args.get('q')
    questions = QuestionModel.query.filter(QuestionModel.title.contains(q)).order_by(QuestionModel.create_time.desc()).all()
    return render_template('index.html',questions=questions)

