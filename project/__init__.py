from flask import Flask, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from project.config import Config
from flask_ckeditor import CKEditor
from flask_login import LoginManager

app = Flask(__name__, static_folder='static/')
app.config.from_object(Config)
db = SQLAlchemy()
ckeditor = CKEditor()
migrate = Migrate(app, db)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = "dgfdhghlmsljdhfksdgkf"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db.init_app(app)
ckeditor.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from .models import User

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint)

from .first_setup import first_setup as firstsetup_blueprint
app.register_blueprint(firstsetup_blueprint)

from .documents import doc as documents_blueprint
app.register_blueprint(documents_blueprint)

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

@app.before_request
def before_request():
    if not User.query.filter_by(id="1").first() and request.path != "/setup":
        return redirect(url_for('first_setup.setup'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))