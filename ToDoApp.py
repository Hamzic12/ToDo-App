from flask import Flask, render_template, flash, redirect, url_for, request, session
from forms import SignUpForm, LogInForm, TodoForm,  Enter_EmailForm, Reset_PasswordForm
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
import jwt
import datetime

App = Flask(__name__)
App.config["SECRET_KEY"] = "your Secret Key"
App.config["MONGO_DBNAME"]  = "name of your db"
App.config["MONGO_URI"] = "your link to your mongodb"
mongo = PyMongo(App)
user = mongo.db.users #users is a name of collection in my db

App.config['MAIL_SERVER'] = 'smtp.gmail.com'
App.config['MAIL_PORT'] = 465
App.config['MAIL_USERNAME'] = "Your email"
App.config['MAIL_PASSWORD'] = "the password of your email"
App.config['MAIL_USE_TLS'] = False
App.config['MAIL_USE_SSL'] = True
mail = Mail(App)

tasks = []

def update_db(updated_tasks):
    new_tasks = {"$set":{"tasks": updated_tasks}}
    current_user = user.find_one({"username": session["curr_user"]})
    user.update_one(current_user, new_tasks)

def token_gen(email):
    token = jwt.encode({'email': email, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=3)}, App.config["SECRET_KEY"], algorithm="HS256")
    return token

#pages
@App.route("/")
@App.route("/home")
def home():
    if "curr_user" in session:
        return redirect(url_for("Mainpage"))
    else:
        return render_template("HomePage.html")
    
@App.route("/login", methods=["GET","POST"])
def Login():
    form = LogInForm()
    if "curr_user" in session:
        return redirect(url_for("Mainpage"))
    if request.method == "POST":
        lower_username = form.username.data.lower()
        login_user = user.find_one({"username": lower_username})
        if login_user is not None:
            if form.password.data == login_user["password"]:
                session["curr_user"] = lower_username
                if form.checkbox.data is True:
                    session.permanent = True
                else:
                    session.permanent = False
                return redirect(url_for("Mainpage"))
            else:
                flash("Wrong credentials!")
    return render_template("LogIn.html", form = form) 

@App.route("/password_reset", methods=["GET", "POST"])
def enter_email():
    form = Enter_EmailForm()
    if form.email.data is not None:
        lower_email = form.email.data.lower()
        existing_email = user.find_one({"email": lower_email})
    if request.method == "POST" and existing_email is not None:
        temp_link = token_gen(lower_email)
        message = Message("Password change request", sender="NoReply@todoapp.com",recipients=[lower_email]) #sender somehow is the same as the email
        message.html = f'To reset your password, click the following link: <a href="{url_for("change_password", token = temp_link, _external=True)}">Reset Password</a>'
        mail.send(message)
        return redirect(url_for("Login"))
    return render_template("EnterEmail.html", form = form)


@App.route("/change_password/<token>", methods=["GET", "POST"])
def change_password(token):
    form = Reset_PasswordForm()
    if request.method == "POST":
        try:
            current_email = jwt.decode(token, App.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return "<h1> Token has expired </h1>"
        new_password = {"$set":{"password": form.password.data}}
        current_user = user.find_one({"email": current_email["email"]})
        user.update_one(current_user, new_password)
        return redirect(url_for("Login"))
    return render_template("ChangePassword.html", form = form)

@App.route("/signup", methods=["GET", "POST"])
def Signup():
    form = SignUpForm()
    if "curr_user" in session:
        return redirect(url_for("Mainpage"))
    if request.method == "POST":
        lower_email = form.email.data.lower()
        lower_username = form.username.data.lower()
        existing_user = user.find_one({"username": lower_username})
        existing_email = user.find_one({"email": lower_email})
        if existing_user is None and existing_email is None:
            user.insert_one({"username": lower_username , "email": lower_email ,"password": form.password.data, "tasks":tasks})
            flash("Successfully signed up")
            return redirect(url_for("Login"))
        elif existing_user is not None:
            flash("Username already in use!")
        else:
            flash("Email already in use!")
    return render_template("SignUp.html", form = form)

@App.route("/todo")
def Mainpage():
    form = TodoForm()
    if "curr_user" not in session:
        return redirect(url_for("home"))
    logged_user = user.find_one({"username": session["curr_user"]})
    load_tasks = logged_user["tasks"]
    return render_template("Todo.html", form = form ,  tasks = load_tasks)
#pages

#buttons
@App.route("/add", methods=["POST"])
def add():
    form = TodoForm()
    new_task = form.user_input.data
    tasks.append({"task": new_task, "done": False, "priority": 0})
    update_db(tasks)
    return redirect(url_for("Mainpage"))

@App.route("/done/<int:index>")
def done(index):
    task = tasks[index]
    task["done"] = not task["done"]
    update_db(tasks)
    return redirect(url_for("Mainpage"))

@App.route("/edit/<int:index>", methods=["GET", "POST"]) 
def edit(index):
    task = tasks[index]
    form = TodoForm(user_input=task.get("task"))
    if request.method == "POST":
        task["task"] = form.user_input.data
        update_db(tasks)
        return redirect(url_for("Mainpage"))
    else:
        return render_template("edit.html", task = task, index = index, form = form)

@App.route("/delete/<int:index>")
def delete(index):
    del tasks[index]
    update_db(tasks)
    return redirect(url_for("Mainpage"))

@App.route("/priority/<int:index>", methods=["GET", "POST"])
def priority(index):
    form = TodoForm()
    task = tasks[index]
    task["priority"] = form.priority.data
    sorted_tasks = sorted(tasks, key=lambda x: x["priority"], reverse=True)
    tasks[:] = sorted_tasks
    update_db(tasks)
    return redirect(url_for("Mainpage"))

@App.route("/logout")
def logout():
    if "curr_user" in session:
        flash("You have been successfully logged out")
    session.pop("curr_user")
    return redirect(url_for("home"))
#buttons


if __name__ == "__main__":
    App.run(host = "0.0.0.0", port = 5000, debug = True)
    mongo.init_app(App)