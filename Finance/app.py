import os

# import re
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

from datetime import datetime, timezone

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

SPECIAL_CHAR = ["!", "<", ">", "@", "#", "$", "%", "^", "&", "*", "?", "_",
                "(", ")", "[", "]", "{", "}", "|", ",", ":", ";", "+", "=", "-", "`", "~"]

# Configure CS50 Library to use SQLite database
database = sqlite3.connect("finance.db")

db = database.cursor()

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""

    # Calling helper function
    owns = owned()
    total = 0

    # Looping through the stocks owned to get the total stocks price and update 'total'
    for symbol, shares in owns.items():
        stocks = lookup(symbol)
        name = stocks["name"]
        price = stocks["price"]
        stock = shares * price
        total += stock
        owns[symbol] = (name, shares, usd(price), usd(total))

    # Fetchign cash from user's profile
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']

    # Add the total again to the cash with user
    total += cash
    return render_template("index.html", owns=owns, cash=usd(cash), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Check for method
    if request.method == "GET":
        return render_template("buy.html")

    symbol = request.form.get("symbol")
    stocks = lookup(symbol)

    # Stocks not found
    if not stocks:
        return render_template("buy.html", invalid=True, symbol=symbol)

    # Initializing variables
    name = stocks["name"]
    price = stocks["price"]
    shares = int(request.form.get("shares"))
    id = session["user_id"]
    user = db.execute("SELECT username FROM users WHERE id = ?", id)[0]['username']
    cash = db.execute("SELECT cash FROM users where id = ?", id)[0]['cash']
    total = price * float(shares)
    on_hand = cash - total

    # Inserting details into temporary table buy
    db.execute("INSERT INTO buy (symbol, name, shares, price, total) VALUES (?, ?, ?, ?, ?)",
               symbol, name, shares, usd(price), usd(total))

    # Displaying how much user spent in total
    buy = db.execute("SELECT * from buy where symbol = ?", symbol)

    # On hand cash lower than total stock price
    if on_hand < total:
        # Delete from temporary table buy
        db.execute("DELETE FROM buy WHERE symbol = ?", symbol)
        # Render unsuccessful message
        return render_template("buy.html", unsuccess=True)

    # On hand cash equal or more than total stock price
    else:
        # Update user's cash after purchase
        db.execute("UPDATE users SET cash = ? WHERE id = ?", on_hand, id)

        # Insert into new table bought for purchase history
        db.execute("INSERT INTO orders (symbol, name, shares, price, total, username, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   symbol, name, shares, usd(price), usd(total), user, time())

        # Delete from temporary table buy
        db.execute("DELETE FROM buy WHERE symbol = ?", symbol)

        # Render success message
        return render_template("buy.html", success=True, buys=buy, name=name, symbol=symbol)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    id = session["user_id"]
    user = db.execute("SELECT username FROM users WHERE id = ?", id)[0]['username']
    orders = db.execute("SELECT symbol, name, shares, price, total, time FROM orders WHERE username = ?", user)
    return render_template("history.html", orders=orders)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        username = request.form.get("username")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        password = request.form.get("password")

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    symbol = request.form.get("symbol")

    # Responding to inputs via POST only
    if request.method == "POST":
        quotes = lookup(symbol)

        # Inserting user input into a new table I created, called quotes
        db.execute("INSERT INTO quotes (symbol, name, price) VALUES (?, ?, ?)",
                   quotes["symbol"], quotes["name"], usd(quotes["price"]))

        # Displaying the quotes for the symbol input by user
        quoted = db.execute("SELECT * FROM quotes WHERE symbol = ?", quotes["symbol"])

        # Deleting data from the table via the input symbol to avoid duplication
        db.execute("DELETE FROM quotes WHERE symbol = ?", quotes["symbol"])
        return render_template("quote.html", quotes=quoted)

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Check for special charactes in username
        for i in range(len(username)):
            for j in range(len(SPECIAL_CHAR)):
                if username[i] == SPECIAL_CHAR[j]:
                    return apology("Username cannot contain special characters!")

        # Check password matching
        if request.form.get("confirmation") != password:
            return apology("Passwords do not match!")

        # Check if password is between 8-16 characters
        if len(password) < 8 or len(password) > 16:
            return apology("Password should have a minimum of 8 characters and maximum of 16!")

        else:
            # Generate hash of password
            hash = generate_password_hash(password, salt_length=8)

            # Insert user's data into the users table
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            return render_template("registered.html")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    own = owned()
    if request.method == "GET":
        # Render list input for user to select from stocks they own
        return render_template("sell.html", owns=own.keys())

    # Initializing variables
    symbol = request.form.get("symbol")
    shares = int(request.form.get("shares"))
    stocks = lookup(symbol)
    id = session["user_id"]
    user = db.execute("SELECT username FROM users WHERE id = ?", id)[0]['username']
    price = stocks["price"]
    name = stocks["name"]
    total = price * float(shares)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", id)[0]['cash']
    on_hand = cash + total

    # Inserting info into temporary table
    db.execute("INSERT INTO sell (symbol, name, shares, price, total) VALUES (?, ?, ?, ?, ?)",
               symbol, name, shares, usd(price), usd(total))

    # Displaying temporary table
    sell = db.execute("SELECT * FROM sell WHERE symbol = ?", symbol)

    # Checking if user owns enough shares of stock
    if own[symbol] < shares:
        # Delete from temporary table
        db.execute("DELETE FROM sell WHERE symbol = ?", symbol)
        # Render invalid message
        return render_template("sell.html", invalid=True, owns=own.keys(), shares=shares, symbol=symbol)

    # Updating user's cash
    db.execute("UPDATE users SET cash = ? WHERE id = ?", on_hand, id)

    # Insert into orders table for history of sales (with negative share values)
    db.execute("INSERT INTO orders (symbol, name, shares, price, total, username, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
               symbol, name, -shares, usd(price), usd(total), user, time())

    # Delete from temporary table
    db.execute("DELETE FROM sell WHERE symbol = ?", symbol)

    # Render success message
    return render_template("sell.html", sells=sell, success=True, name=name, symbol=symbol)


def time():
    # Function to return date and time
    now = datetime.now(timezone.utc)
    return str(now.date()) + ' | ' + now.time().strftime("%H:%M:%S")


def owned():
    # Function to get stock symbol and number of shares user owns in a dictionary {symbol: 'shares'}
    user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']
    owns = {}
    query = db.execute("SELECT symbol, shares FROM orders WHERE username = ?", user)
    for q in query:
        symbol, shares = q["symbol"], q["shares"]
        owns[symbol] = owns.setdefault(symbol, 0) + shares
    owns = {k: v for k, v in owns.items() if v != 0}
    return owns

# db.close()

if __name__ == "__main__":
    app.run(debug=True)