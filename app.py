import secrets

from flask import Flask, render_template, redirect, url_for, json
from flask_bootstrap import Bootstrap
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm, LoginForm
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dbc.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create and initialize the app with the extension
db = SQLAlchemy(app)
db.init_app(app)


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    profile_pic_url = db.Column(db.String(250), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    links = relationship("Link", back_populates="user")


class Link(db.Model):
    __tablename__ = "links"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="links")
    label = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=False)


def populate_test_data():
    """
    If no users/links are in the database, this function populates some default users for testing purposes.
    """
    users = User.query.all()
    if len(users) == 0:
        with open("tests/test_data.json") as test_data_json:
            test_data = json.load(test_data_json)
            users = test_data["users"]
            links = test_data["links"]
            db.session.bulk_insert_mappings(User, users)
            db.session.bulk_insert_mappings(Link, links)
            db.session.commit()


with app.app_context():
    db.create_all()
    populate_test_data()


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
