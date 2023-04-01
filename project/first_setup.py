from flask import Blueprint, render_template, request, flash, url_for, redirect
from werkzeug.security import generate_password_hash
from .models import User, Privileges,System_files_patches, Server_rules
from . import db
import os

first_setup = Blueprint('first_setup', __name__)

@first_setup.route('/setup', methods=('POST','GET'))
def setup():
    error = False
    if Privileges.query.filter_by(privilege="root").first() is None:
        db.session.add(Privileges(privilege="root"))
        db.session.commit()
    if User.query.filter_by(id="1").first():
        return redirect(url_for('auth.login'))
    else:
        if request.method == 'POST':
            users_dir =[]
            email = request.form.get('email')
            name = request.form.get('name')
            login = request.form.get('login')
            password = request.form.get('password')
            password_check = request.form.get('password_check')
            extensions = request.form.get('extensions')
            privilege = "root"
            users_dir.append([request.form.get('users_directory'), "UsersPath"])
            if password != password_check:
                flash("Пароли не совпадают")
            else:
                password = generate_password_hash(request.form.get('password'), method='sha256')
                for data in users_dir:
                    if not os.path.exists(data[0]):
                        flash(f"Не удалось получить доступ к папке:   {data[0]}")
                        error = True
                    else:
                        path = System_files_patches(path=data[0], pool_name=data[1])
                        db.session.add(path)
                if not error:
                    server_rule = Server_rules(name="ALLOWED_EXTENSIONS", rule=extensions.lower())
                    new_user = User(email=email, login=login, privilege=privilege, name=name, password=password)
                    db.session.add(new_user)
                    db.session.add(server_rule)



                    db.session.commit()




            return redirect(url_for('auth.login'))
        return render_template("login/setup.html")