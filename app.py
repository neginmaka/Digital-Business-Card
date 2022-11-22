import secrets

from werkzeug.security import generate_password_hash
from flask import Flask, render_template, redirect, url_for, json, flash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, current_user
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
    profile_pic_url = db.Column(db.String(250), nullable=True)
    bio = db.Column(db.Text, nullable=True)
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
    if form.validate_on_submit():
        email = User.query.filter_by(email=form.email.data).first()
        username = User.query.filter_by(email=form.email.data).first()
        if email:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))

        if username:
            flash(f"{username} is already taken. Let's choose a different username")
            return render_template("register.html", form=form)

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            "pbkdf2:sha256",
            8
        )

        new_user = User(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            password=hash_and_salted_password
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("admin_view", username=form.username.data))
    else:
        form.name.render_kw = {"placeholder": "Enter Your Name"}
        form.email.render_kw = {"placeholder": "Enter Your Email"}
        form.username.render_kw = {"placeholder": "Enter Your Name"}
        form.password.render_kw = {"placeholder": "Enter Your Password"}
        # TODO: Login user after they are signed up
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
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
    # TODO: get user from DB
    user = User(
        email="admin@test.com",
        username="admin",
        password="P@ssw0rd",
        name="Admin Admiani",
        profile_pic_url="https://i.pinimg.com/550x/f1/4e/49/f14e4900a0e245a157bb6ce73b8a06aa.jpg",
        bio="I am the admin of this universe"
    )

    links = [
        Link(
            label="Google",
            url="https://www.google.com"
        ),
        Link(
            label="Linkedin",
            url="https://www.linkedin.com"
        )]
    return render_template("enduser.html", links=links, user=user)


if __name__ == "__main__":
    app.run(debug=True)
