from flask import Flask, render_template, flash, redirect, url_for, request, session
from forms import SignUpForm, LogInForm, TodoForm
from flask_pymongo import PyMongo

App = Flask(__name__)
App.config["SECRET_KEY"] = "your Secret Key"
App.config["MONGO_DBNAME"]  = "name of your db"
App.config["MONGO_URI"] = "your link to your mongodb"
mongo = PyMongo(App)
user = mongo.db.users #users is a name of collection in my db

tasks = []

def update_db(updated_tasks):
    new_tasks = {"$set":{"tasks": updated_tasks}}
    current_user = user.find_one({"username": session["curr_user"]})
    user.update_one(current_user, new_tasks)


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
    login_user = user.find_one({"username": form.username.data})
    if login_user is not None:
        if form.password.data == login_user["password"]:
            session["curr_user"] = form.username.data
            return redirect(url_for("Mainpage"))
        else:
            flash("Wrong credentials!")
    return render_template("LogIn.html", form = form) 
    
@App.route("/signup", methods=["GET", "POST"])
def Signup():
    form = SignUpForm()
    if "curr_user" in session:
        return redirect(url_for("Mainpage"))
    if form.email.data is not None:
        lower_email = form.email.data.lower()
    if request.method == "POST":
        existing_user = user.find_one({"username": form.username.data})
        existing_email = user.find_one({"email": lower_email})
        if existing_user is None and existing_email is None:
            user.insert({"username": form.username.data , "email": lower_email ,"password": form.password.data, "tasks":tasks})
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
    return render_template("Todo.html", form = form,  tasks = load_tasks)
#pages

#buttons
@App.route("/add", methods=["POST"])
def add():
    form = TodoForm()
    new_task = form.user_input.data
    tasks.append({"task": new_task, "done": False})
    update_db(tasks)
    return redirect(url_for("Mainpage"))

@App.route("/done/<int:index>")
def done(index):
    tasks[index]["done"] = not tasks[index]["done"]
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