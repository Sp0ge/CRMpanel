from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import User, Privileges,System_files_patches, Server_rules
from werkzeug.security import generate_password_hash
import os, shutil
from . import db


admin = Blueprint('admin', __name__)
@admin.route("/admin/user_edit", methods=('GET','POST'))
@login_required
def user_edit():
    if current_user.privilege == "root":
        if request.method == "POST":
            user_id = request.form.get("user_id")
            user = User.query.filter_by(id=user_id).first()
            if user.privilege == "root":
                flash("Нельзя удалить Root пользователя!")
            else:
                User.query.filter(User.id == user_id).delete()
                db.session.commit()

        users = User.query.order_by(User.id).all()
        return render_template("admin/user_edit.html", users=users)
    else:
        flash("У вас не доступа к этой странице!")
        return redirect(url_for('main.index'))

@admin.route("/admin/user_add", methods=('GET','POST'))
@login_required
def user_add():
    if current_user.privilege == "root":
        if request.method == 'POST':
            email = request.form.get('email')
            name = request.form.get('name')
            login = request.form.get('login')
            password = generate_password_hash(request.form.get('password'), method='sha256')
            password2 = generate_password_hash(request.form.get('password'), method='sha256')
            privilege = request.form.get('privilege')
            if password2 is password:
                flash("Пароли не совпадают!")
            else:
                new_user = User(email=email, login=login, privilege=privilege, name=name, password=password)
                if User.query.filter_by(email=email).first() is not None:
                    flash("Такая почта уже есть!")
                else:
                    if User.query.filter_by(login=login).first() is not None:
                        flash("Такой логин уже есть!")
                    else:
                        db.session.add(new_user)
                        db.session.commit()
                        return redirect(url_for("admin.user_edit"))
        privileges = Privileges.query.order_by(Privileges.id).all()
        return render_template("admin/user_add.html", privileges=privileges)

    else:
        flash("У вас не доступа к этой странице!")
        return redirect(url_for('main.index'))

@admin.route("/admin/privileges_edit", methods=('GET','POST'))
@login_required
def privileges_edit():
    if Privileges.query.filter_by(privilege="root").first() is None:
        db.session.add(Privileges(privilege="root"))
        db.session.commit()
    if current_user.privilege == "root":
        if request.method == 'POST':
            privilege = request.form.get('privilege')
            action = request.form.get('action')
            if privilege.strip() == '':
                flash("Значение не может быть пустым")
            else:
                if action == "add":
                    new_privilege = Privileges(privilege=privilege)
                    if Privileges.query.filter_by(privilege=privilege).first() is not None:
                        flash("Такое значение уже есть.")
                    else:
                        db.session.add(new_privilege)
                        db.session.commit()
                if action == "del":
                    if Privileges.query.filter_by(privilege=privilege).first() is not None:
                        if privilege == "root":
                            flash("Не удаляйте Root дання привелегия являеться системной.")
                        else:
                            Privileges.query.filter(Privileges.privilege == privilege).delete()
                            db.session.commit()
                    else:
                        flash("Значение для удаления не найдено.")
        privileges = Privileges.query.all()
        return render_template("admin/privileges_edit.html", privileges=privileges)

    else:
        flash("У вас не доступа к этой странице!")
        return redirect(url_for('main.index'))

@admin.route("/admin/user_edit_info/<int:n>", methods=('GET','POST'))
@login_required
def user_edit_info(n):
    if current_user.privilege == "root":
        if request.method == 'POST':
            target = User.query.filter_by(id=n).first()
            target.email = request.form.get('email')
            target.name = request.form.get('name')
            target.login = request.form.get('login')
            target.password = generate_password_hash(request.form.get('password'), method='sha256')
            target.privilege = request.form.get('privilege')
            db.session.commit()
            return redirect(url_for("admin.user_edit"))
        user = User.query.filter_by(id=n).first()
        privileges = Privileges.query.all()
        return render_template("admin/user_edit_info.html", user=user, privileges=privileges)
    else:
        flash("У вас не доступа к этой странице!")
        return redirect(url_for('main.index'))

@admin.route("/admin/data_pools", methods=('GET','POST'))
@login_required
def data_pools():
    if current_user.privilege == "root":
        pools = System_files_patches.query.all()
        return render_template("admin/data_pools.html", pools=pools)
    else:
        flash("У вас не доступа к этой странице!")
        return redirect(url_for('main.index'))

@admin.route("/admin/data_pools/<int:n>", methods=('POST','GET'))
@login_required
def data_pool_edit(n):
    if request.method == 'POST':
        if current_user.privilege == "root":
            new_path = request.form.get("users_directory")
            if os.path.exists(new_path):
                pool = System_files_patches.query.filter_by(id=n).first()
                pool.path = new_path
                db.session.commit()
            else:
                flash("Не получилось получить доступ к папке.")
            return redirect(url_for('admin.data_pools'))
        else:
            flash("У вас не доступа к этой странице!")
            return redirect(url_for('main.index'))

@admin.route("/admin/ssl_edit", methods=('GET','POST'))
@login_required
def ssl_edit():
    if current_user.privilege == "root":
        if request.method == "POST":

            key = request.files['ssl_key']
            if "" != key:
                key.save("ssl/ssl_cert.crt")

            cert = request.files['ssl_cert']
            if "" != cert:
                cert.save("ssl/ssl_cert.crt")

            else:
                flash("Ошибка формы.")


                flash("Перезагрузите сервер для установки сертификатов.")


                return redirect(url_for("admin.ssl_edit"))

        ssl_files = []
        files = os.listdir("ssl")
        for file in files:
            if ".crt" in file:
                ssl_files.append("Корневой сертификат - "+file)
            if ".key" in file:
                ssl_files.append("Ключ - "+file)
        return render_template("admin/ssl_edit.html", ssl_files=ssl_files)
    else:
        flash("У вас не доступа к этой странице!")
        return redirect(url_for('main.index'))

@admin.route("/admin/ssl_factory", methods=('GET','POST'))
@login_required
def ssl_factory():
    if current_user.privilege == "root":
        os.remove("ssl/ssl_key.key")
        os.remove("ssl/ssl_cert.crt")
        shutil.copy("ssl/default_ssl/ssl_key.key", "ssl/ssl_key.key")
        shutil.copy("ssl/default_ssl/ssl_cert.crt", "ssl/ssl_cert.crt")
        flash("Перезагрузите сервер возврата сертификатов.")
        return redirect(url_for("admin.ssl_edit"))


        files = os.listdir("ssl")
        for file in files:
            ssl_files = []
            if os.path.isfile(file):
                ssl_files.append(file)
        return render_template("admin/ssl_edit.html", ssl_files=ssl_files)
    else:
        flash("У вас не доступа к этой странице!")
        return redirect(url_for('main.index'))

@admin.route("/admin/users_rules", methods=('GET','POST'))
@login_required
def users_rules():
    if current_user.privilege == "root":
        allowed_exten = Server_rules.query.filter_by(name="ALLOWED_EXTENSIONS").first()

        return render_template("admin/users_rules.html",allowed_exten=allowed_exten)
    else:
        flash("У вас не доступа к этой странице!")
        return redirect(url_for('main.index'))

@admin.route("/admin/rule/<int:n>", methods=('POST','GET'))
@login_required
def server_rules_edit(n):
    if request.method == 'POST':
        if current_user.privilege == "root":
            extensions = request.form.get("extensions")
            server_rule = Server_rules.query.filter_by(name="ALLOWED_EXTENSIONS").first()
            server_rule.rule = extensions.lower()
            db.session.commit()
            return redirect(url_for('admin.users_rules'))
        else:
            flash("У вас не доступа к этой странице!")
            return redirect(url_for('main.index'))

