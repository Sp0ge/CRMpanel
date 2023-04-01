from flask import Blueprint, render_template,url_for,redirect
from .models import User
from flask_login import login_required, current_user
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')

