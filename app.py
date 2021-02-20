import os
import datetime
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
privacy = mongo.db.privacy
terms_conditions = mongo.db.terms_conditions


# Code adapted from CI Task Manager Flask App mini Project
@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html")


# Code adapted from CI Task Manager Flask App mini Project
@app.route("/get_reviews")
def get_reviews():
    reviews = list(book_review.find())
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
            "password": generate_password_hash(request.form.get("password")),
            "date_joined": datetime.datetime.utcnow()
        }
        users.insert_one(sign_up)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("sign-up.html")


# Code adapted from CI Task Manager Flask App mini Project
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
            return redirect(url_for("login"))

    return render_template("login.html")


# Code adapted from CI Task Manager Flask App mini Project
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


# Code adapted from CI Task Manager Flask App mini Project
@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been successfully logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/privacy_policy")
def privacy_policy():
    # render the tprivacy policy accordion text
    privacy_list = list(privacy.find())
    return render_template("privacy.html", privacy=privacy_list)


@app.route("/terms_conditions_list")
def terms_conditions_list():
    # render the terms and conditions accordion text
    terms_conditions_list = list(terms_conditions.find())
    return render_template(
        "terms-and-conditions.html", terms_conditions=terms_conditions_list)


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    if request.method == "POST":
        review = {
            "genre": request.form.get("genre_name"),
            "title": request.form.get("title"),
            "author": request.form.get("author"),
            "image_url": request.form.get("image_url"),
            "number_pages": request.form.get("number_pages"),
            "isbn": request.form.get("isbn"),
            "review": request.form.get("review"),
            "rating": request.form.get("rating"),
            "created_by": session["user"],
            "favourite": "off",
            "count": 0
        }
        book_review.insert_one(review)
        flash("Review Successfully Added")
        return redirect(url_for("get_reviews"))

    genres = genre.find().sort("genre_name", 1)
    return render_template("add-review.html", genres=genres)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
