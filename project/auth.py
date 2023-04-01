from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from .models import User

auth = Blueprint('auth', __name__)
@auth.route('/login',methods=('POST','GET'))
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(login=login).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=remember)
        return redirect(url_for("main.index"))
    return render_template('login/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
