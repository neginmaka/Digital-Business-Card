from flask import Flask, render_template, redirect, url_for, flash, abort

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

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
    app.run()
