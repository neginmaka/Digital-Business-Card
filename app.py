from flask import Flask, render_template, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from flask_bootstrap import Bootstrap

import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
Bootstrap(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    return render_template("register.html", form=form)


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return redirect(url_for("home"))


@app.route("/contact")
def contact():
    return redirect(url_for("home"))


@app.route("/<username>/admin")
def admin_view(username):
    return render_template("admin.html")


@app.route("/<username>/profile")
def profile(username):
    return render_template("profile.html")


@app.route("/<username>")
def enduser_view(username):
    return render_template("enduser.html")


if __name__ == "__main__":
    app.run(debug=True)
