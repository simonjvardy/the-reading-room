# Code adapted from Code Institute Course Material
# Task Manager Flask App mini Project

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

# config MongoDB
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html")


@app.route("/get_reviews")
def get_reviews():
    reviews = list(mongo.db.book_review.find())
    return render_template("book-review.html", reviews=reviews)


@app.route("/book_page/<book_id>", methods=["GET", "POST"])
def book_page(book_id):
    # get the book review for the selected _id
    book = mongo.db.book_review.find_one({"_id": ObjectId(book_id)})
    return render_template("book-page.html", book=book)


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists", "orange lighten-3")
            return redirect(url_for("sign_up"))

        # collect the signup form data and write to MongoDB
        sign_up = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "is_admin": "off",
            "is_super_user": "off",
            "date_joined": datetime.datetime.utcnow()
        }
        mongo.db.users.insert_one(sign_up)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!", "teal lighten-2")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("sign-up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()

                # Update Last login date field
                login = {"$set": {"last_login": datetime.datetime.utcnow()}}
                mongo.db.users.update_one({"_id": existing_user["_id"]}, login)

                # Wlecome message and direct to Profile page
                flash("Welcome Back, {}".format(
                    request.form.get("username")), "teal lighten-2")
                return redirect(url_for(
                    "profile", username=session["user"]))

            else:
                # invalid password match
                flash("Incorrect Username and/or Password", "red lighten-3")
                return redirect(url_for("login"))
        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password", "red lighten-3")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})

    # Check for user account type
    if session["user"]:
        if username["is_admin"] == "on":
            account = "Admin"
        elif username["is_super_user"] == "on":
            account = "Superuser"
        else:
            account = "User"

        return render_template(
            "profile.html", username=username, account=account)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been successfully logged out", "light-blue lighten-3")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/privacy_policy")
def privacy_policy():
    # render the privacy policy accordion text
    privacy = list(mongo.db.privacy.find())
    return render_template("privacy.html", privacy=privacy)


@app.route("/terms_conditions_list")
def terms_conditions_list():
    # render the terms and conditions accordion text
    terms_conditions = list(mongo.db.terms_conditions.find())
    return render_template(
        "terms-and-conditions.html", terms_conditions=terms_conditions)


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    if request.method == "POST":
        # collect the add review form data and write to MongoDB
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
            "is_book_of_month": request.form.get("is_book_of_month"),
            "favourite": "off",
            "count": 0
        }
        mongo.db.book_review.insert_one(review)
        flash("Review Successfully Added", "teal lighten-2")
        return redirect(url_for("get_reviews"))

    genres = mongo.db.genre.find().sort("genre_name", 1)
    return render_template("add-review.html", genres=genres)


@app.route("/get_genres")
def get_genres():
    # Get the list of genre names from the db
    genres = list(mongo.db.genre.find().sort("genre_name", 1))
    return render_template("manage-genres.html", genres=genres)


@app.route("/add_genre", methods=["GET", "POST"])
def add_genre():
    if request.method == "POST":
        # collect the add genre form data and write to MongoDB
        new_genre = {
            "genre_name": request.form.get("genre_name")
        }
        mongo.db.genre.insert_one(new_genre)
        flash("New Genre Added", "teal lighten-2")
        return redirect(url_for("get_genres"))

    return render_template("add-genre.html")


@app.route("/edit_genre/<genre_id>", methods=["GET", "POST"])
def edit_genre(genre_id):
    if request.method == "POST":
        # collect the edit genre form data and write to MongoDB
        submit = {
            "genre_name": request.form.get("genre_name")
        }
        mongo.db.genre.update({"_id": ObjectId(genre_id)}, submit)
        flash("Genre Successfully Updated", "teal lighten-2")
        return redirect(url_for("get_genres"))

    genre = mongo.db.genre.find_one({"_id": ObjectId(genre_id)})
    return render_template("edit-genre.html", genre=genre)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
