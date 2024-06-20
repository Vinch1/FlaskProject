from flask import Flask, session, g
import config
from exts import db, mail, login_manager
from models import User
from blueprints.qa import bp as qa_bp
from blueprints.auth import bp as auth_bp
from blueprints.errors import errors
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

app = Flask(__name__)
#绑定配置文件
app.config.from_object(config)
db.init_app(app)
mail.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
csrf = CSRFProtect(app)

migrate = Migrate(app, db)

app.register_blueprint(qa_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(errors)
# before_request / before_first_request / after_request
# hook

# @app.before_request
# def my_before_request():
#     user_id = session.get('user_id')
#     if user_id:
#         user = User.query.get(user_id)
#         setattr(g, 'user', user)#global variable
#     else:
#         setattr(g, 'user', None)
#
# @app.context_processor #上下文处理器
# def my_context_processor():
#     return {'user': g.user}

if __name__ == '__main__':
    app.run()
