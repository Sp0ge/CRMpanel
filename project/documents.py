from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify, send_file
from project.models import User, System_files_patches, Server_rules, UsersFilesAccess
from flask_login import login_required, current_user
import os
import magic
from project import db

doc = Blueprint('documents', __name__)

@doc.route("/user/doc/list", methods=["POST","GET"])
@login_required
def user_file():
    files_in_db = UsersFilesAccess.query.all()
    search=""
    if request.method == "POST":
        search = request.form["search"].strip()
        if search != "":
            files_in_db = UsersFilesAccess.query.like("%search%").all()
    allowed = Server_rules.query.filter_by(name="ALLOWED_EXTENSIONS").first()
    mainpath = System_files_patches.query.filter_by(pool_name="UsersPath").first()
    user_folder = str(mainpath.path) + "DataFolder_User_" + current_user.name + "ID_" + str(current_user.id) + "/"
    if not os.path.exists(user_folder):
        os.mkdir(user_folder)
    for n_file in range(0,len(files_in_db)):
        if not os.path.exists(files_in_db[n_file].path):
            block = UsersFilesAccess.query.get(files_in_db[n_file].id)
            db.session.delete(block)
            db.session.commit()


    return render_template("documents/list.html", fileslist=files_in_db, extensions=str('.' + str(allowed.rule).replace(' ',',.')), UU = User, search_question=search)

def allowed_file(filename):
    allowed = Server_rules.query.filter_by(name="ALLOWED_EXTENSIONS").first()
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in list(str(allowed.rule).split(' '))
@doc.route('/user/doc/upload', methods=["POST"])
@login_required
def upload_file():
    mainpath = System_files_patches.query.filter_by(pool_name="UsersPath").first()
    if mainpath is None:
        return "User path error"
    user_folder =str(mainpath.path) + "DataFolder_User_" + current_user.name + "ID_" + str(current_user.id) + '/'
    uploaded_files = request.files.getlist("file[]")
    error = False
    if request.files['file[]'].filename != '':
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                file.save(os.path.join(user_folder, file.filename))
                name=file.filename
                file_info = UsersFilesAccess(name=name.strip(), path=user_folder+file.filename, owner=current_user.id, can_use="None")
                if UsersFilesAccess.query.filter_by(path = file_info.path) == None:
                    flash(UsersFilesAccess.query.filter_by(path = file_info.path))
                    db.session.add(file_info)
                else:
                    flash(f"{file_info.name} уже существуют!")
            else:
                error = True
            db.session.commit()
    else:
        flash("Вы ничего не отправили")
    if error:
        flash("Некоторые файлы нельзя загрузить на сервер!")
    return redirect(request.referrer)

@doc.route('/user/doc/remove', methods=["GET"])
@login_required
def remove_file():
    id = request.args.get('file')
    file = UsersFilesAccess.query.filter_by(id=id, owner=current_user.id).first()
    if file is None:
        flash("Файл не сущетсвует!")
        return redirect(request.referrer)

    if str(current_user.id) != file.owner:
        flash('Это не ваш документ.')
        return redirect(request.referrer)

    db.session.delete(file)
    if os.path.exists(file.path):
        os.remove(file.path)
    db.session.commit()
    return redirect(request.referrer)

@doc.route('/user/doc/access_settings', methods=["GET","POST"])
@login_required
def access_settings():
    file_id = request.args.get('file')
    file = UsersFilesAccess.query.filter_by(id=file_id).first()
    if file is None:
        flash("Файл не сущетсвует!")
        return redirect(request.referrer)



    if str(current_user.id) != file.owner:
        flash('Это не ваш документ.')
        return redirect(request.referrer)
    if not os.path.exists(file.path):
        db.session.delete(file)
        db.session.commit()
        return redirect(request.referrer)
    users = User.query.all()

    files_share = list(file.can_use)

    if file is None:
        flash("Файл не сущетсвует!")
        return redirect(request.referrer)

    if request.method == "POST":
        can_use="no one"
        check = request.form.getlist("users_to_share")
        file.can_use = str(check)
        db.session.commit()

    return render_template("documents/access_settings.html", file=file, users=users, can_use=files_share, UU = User)


@doc.route('/user/doc/download', methods=["GET"])
@login_required
def download_file():
    file_id = request.args.get('file')
    file = UsersFilesAccess.query.filter_by(id=file_id).first()
    if file is None:
        flash("Файл не сущетсвует!")
        return redirect(request.referrer)
    if not os.path.exists(file.path):
        db.session.delete(file)
        db.session.commit()
        return redirect(request.referrer)
    if file.can_use != 'no one' or int(file.owner) == int(current_user.id):
        if str(current_user.id) in file.can_use or int(file.owner) == int(current_user.id):
            return send_file(file.path, as_attachment=True)
    else:
        flash("У вас нет доступа к этому файлу!")
    return redirect(request.referrer)

@doc.route('/user/doc/open/[str:n]', methods=["GET"])
@login_required
def work_file():
    return render_template("workfiles/text.html")




