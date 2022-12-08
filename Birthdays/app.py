import os

from sqlite3 import connect
from flask import Flask, flash, jsonify, redirect, render_template, request, session

database = connect("birthdays.db", check_same_thread=False)
db = database.cursor()

# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database

MONTH = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/remove", methods=["POST"])
def remove():
    id = request.form.get("id")
    if id:
        db.execute("delete from birthdays where id=?", id)
    return redirect("/")



@app.route("/", methods=["GET", "POST"])
def index():
    name = request.form.get("name")
    month = request.form.get("month")
    day = request.form.get("day")

    if request.method == "POST":
        # Add the user's entry into the database
        db.execute("insert into birthdays (name, month, day) values(?, ?, ?)", (name, month, day))
        return redirect("/")

    else:
        # Display the entries in the database on index.html
        birthday = db.execute("select * from birthdays")
        return render_template("index.html", months = MONTH, birthdays = birthday)


