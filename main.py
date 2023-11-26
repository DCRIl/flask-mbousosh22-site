import os
import sqlite3
import smtplib

from test import my_email, my_password
from flask import Flask, render_template, request, redirect, url_for, g
from email.message import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.before_request
def global_():
    g.db = sqlite3.connect("all_tables.sqlite")
    g.user = None


@login_manager.user_loader
def load_user(user_login, password):
    g.user = User(user_login, password)
    return g.user


class Us()


class User(UserMixin):
    def __init__(self, username, password, new_user=False):
        self.con = g.db
        self.error = ""
        self.adm = False
        if not new_user:
            up = self.con.cursor().execute(
                f"""SELECT user_id, password FROM users WHERE username='{username}'""").fetchone()
            if up:
                if up[1] == password or check_password_hash(up[1], password):
                    self.user_id = up[0]
                    self.username = username
                    self.password = up[1]
                    if self.con.cursor().execute(f"""SELECT user_id FROM admins WHERE user_id='{up[0]}'""").fetchone():
                        self.adm = True
                else:
                    self.error = "Неверный пароль"
            else:
                self.error = f"Нет пользователя '{username}'"
        else:
            up = self.con.cursor().execute(
                f"""SELECT user_id, password FROM users WHERE username='{username}'""").fetchone()
            if not up:
                self.con.cursor().execute(
                    f"""INSERT INTO users(username, password) VALUES ('{username}', '{generate_password_hash(password)}')""")
                self.con.commit()
                v = self.con.cursor().execute(f"""SELECT user_id FROM users WHERE username='{username}'""").fetchone()
                self.user_id = v[0]
                self.username = username
                self.password = generate_password_hash(password)
            else:
                self.error = f"Пользователь '{username}' уже существует"


class Idea:
    def __init__(self, idea_, user, name, email):
        g.db.cursor().execute(
            f"""INSERT OR REPLACE INTO ideas(idea_text, username, name, email) VALUES ('{idea_}', '{user}', '{name}', '{email}')""")
        g.db.commit()




@app.route('/', methods=["POST", "GET"])
def login():
    error = ""
    if current_user.is_authenticated:
        return redirect('/idea/')
    if request.method == "POST":
        user_login = request.form["user_login"]
        password = request.form["password"]
        if user_login and password:
            if request.form["btn-log-reg"] == "Вход":
                us = User(user_login, password)
                if us.error == "":
                    load_user(user_login, password)
                    return redirect(f"/idea/")
                else:
                    return render_template("login_form.html", error=us.error)
            else:
                us = User(user_login, password, new_user=True)
                if us.error == "":
                    load_user(us.user_id)
                    return redirect(f"/idea/")
                else:
                    return render_template("login_form.html", error=us.error)
        else:
            return render_template("login_form.html", error="Логин и пароль не могут быть пустыми")
    else:
        return render_template("login_form.html", error="")


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/idea/', methods=["POST", "GET"])
# @login_required
def idea():
    # s = g.db.cursor().execute(
    #     f"""SELECT username, password FROM users WHERE user_id = {user_id}""").fetchone()
    # us = User(s[0], s[1])
    print(g.user)
    if request.method == "POST":
        name = request.form["name"]
        email_address = request.form["email_address"]
        idea_text = request.form["idea_text"]
        if name and email_address and idea_text:
            ideaa = Idea(idea_text, current_user.username, name, email_address)
            smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
            smtpObj.starttls()
            smtpObj.login(my_email, my_password)
            mess = f"""<!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" type="text/css" hs-webfonts="true" href="https://fonts.googleapis.com/css?family=Lato|Lato:i,b,bi">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body bgcolor="#F5F8FA" style="width: 100%; font-family:Lato, sans-serif; font-size:18px;">
        <div id="email">
            <table role="presentation" width="100%">
                <tr>
                    <td bgcolor="#00A4BD" align="center" style="color: white;">
                        <h1>Добавлена новая идея!</h1>
                    </td>
            </table>
            <table role="presentation" border="0" cellpadding="0" cellspacing="10px" style="padding: 10px 30px 30px 10px;">
                <tr>
                    <td>
                        <h3>Пользователь: {name}<br><br>С почтой: {email_address}<br><br>Оставил новую идею:<br><br></h3>
                        <p>
                            {idea_text}
                        </p>
                    </td>
                </tr>
            </table>
        </div>
        </body>
        </html>"""
            msg = EmailMessage()
            msg["From"] = my_email
            msg["To"] = my_email
            msg["Subject"] = "Добавили новую идею!"
            msg.set_content(mess, subtype="html")
            smtpObj.send_message(msg)
            smtpObj.quit()

            return redirect(f"/all_ideas/{current_user.user_id}/")
    else:
        # print(g.user.username)
        return render_template("change.html", us=g.user)


@app.route("/all_ideas/<user_id>/", methods=["POST", "GET"])
def all_ideas(user_id):
    s = sqlite3.connect("all_tables.sqlite").cursor().execute(
        f"""SELECT username, password FROM users WHERE user_id = {user_id}""").fetchone()
    us = User(s[0], s[1])
    ideas = sqlite3.connect("all_tables.sqlite").cursor().execute(
        f"""SELECT idea_id, idea_text, username FROM ideas""").fetchall()[::-1]
    if request.method == "POST":
        id = int(request.form["answer"])
        info = sqlite3.connect("all_tables.sqlite").cursor().execute(
            f"""SELECT idea_text, name, email FROM ideas WHERE idea_id = {id}""").fetchone()
        smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
        smtpObj.starttls()
        smtpObj.login(my_email, my_password)
        mess = f"""<!DOCTYPE html>
                <html>
                <head>
                    <link rel="stylesheet" type="text/css" hs-webfonts="true" href="https://fonts.googleapis.com/css?family=Lato|Lato:i,b,bi">
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body bgcolor="#F5F8FA" style="width: 100%; font-family:Lato, sans-serif; font-size:18px;">
                <div id="email">
                    <table role="presentation" width="100%">
                        <tr>
                            <td bgcolor="#00A4BD" align="center" style="color: white;">
                                <h1>Ваша идея не осталась без внимания!</h1>
                            </td>
                    </table>
                    <table role="presentation" border="0" cellpadding="0" cellspacing="10px" style="padding: 10px 30px 30px 10px;">
                        <tr>
                            <td>
                                <h1>Уважаемый {info[1]}</h1>
                                <h3>На вашу идею:</h3>
                                <h4>{info[0]}</h4>
                                <p>
                                    Пришёл ответ.
                                </p>
                                <br>
                                <h4>Ответ:</h4>
                                <p>{request.form[f"ans{id}"]}</p>
                                <br>
                                <br>
                                <p>Если данный ответ как либо задел вас, то прошу напишите и об этом, нас интересует удовлетворённость нашим обслуживанием</p>
                            </td>
                        </tr>
                    </table>
                </div>
                </body>
                </html>"""
        msg = EmailMessage()
        msg["From"] = my_email
        msg["To"] = info[2]
        msg["Subject"] = "Ваша идея не осталась без внимания!"
        msg.set_content(mess, subtype="html")
        smtpObj.send_message(msg)
        smtpObj.quit()
        return render_template("all_ideas.html", ideas=ideas, us=us)
    else:
        return render_template("all_ideas.html", ideas=ideas, us=us)


@app.route("/user_ideas/<user_id>/")
@login_required
def user_ideas(user_id):
    s = sqlite3.connect("all_tables.sqlite").cursor().execute(
        f"""SELECT username, password FROM users WHERE user_id = {user_id}""").fetchone()
    us = User(s[0], s[1])
    ideas = sqlite3.connect("all_tables.sqlite").cursor().execute(
        f"""SELECT idea_text, username FROM ideas WHERE username = (SELECT username FROM users WHERE user_id = {user_id})""").fetchall()[
            ::-1]
    return render_template("user_ideas.html", ideas=ideas, us=us)


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(host="localhost", port=11111, debug=True)
