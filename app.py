import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)
book_review = mongo.db.book_review
users = mongo.db.users
genre = mongo.db.genre


@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html")


@app.route("/get_reviews")
def get_reviews():
    reviews = book_review.find()
    return render_template("book-review.html", reviews=reviews)


# Code adapted from CI Task Manager Flask App mini Project
@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("sign_up"))

        sign_up = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(
                request.form.get("password"),
                method='pbkdf2:sha256',
                salt_length=8)
        }
        users.insert_one(sign_up)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        # return redirect(url_for("profile", username=session["user"]))

    return render_template("sign-up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))

            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            # return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
