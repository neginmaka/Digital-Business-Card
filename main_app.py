import os
import secrets

import flask
import requests
from PIL import Image
from flask import Flask, render_template, redirect, url_for, json, request
from flask_bootstrap import Bootstrap
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user
)
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from forms import AdminForm, PhotoForm
from okta_helpers import is_access_token_valid, is_id_token_valid, config
from sqlalchemy.orm import relationship
from utils import modify_links

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dbc.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = ".\\static\\img\\users"

# Login manager
login_manager = LoginManager()

# Default redirect page for login-required routes
login_manager.login_view = "login"
login_manager.init_app(app)

APP_STATE = 'ApplicationState'
NONCE = secrets.token_hex(16)

# create and initialize the app with the extension
db = SQLAlchemy(app)
db.init_app(app)

# total number of rows for name and url
TOTAL_ROWS = 5


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    profile_pic_url = db.Column(db.String(250), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    links = relationship("Link", back_populates="user")

    def claims(self):
        """Use this method to render all assigned claims on profile page."""
        return {'name': self.name,
                'email': self.email}.items()

    @staticmethod
    def get(user_id):
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def create(name, email, username, id):
        new_user = User(
            name=name,
            email=email,
            username=username,
            id=id)
        db.session.add(new_user)
        db.session.commit()


class Link(db.Model):
    __tablename__ = "links"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="links")
    label = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=False)


# TODO: Re-define this function to work with Okta.
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


def compress_image(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Check the file size
    file_size = os.path.getsize(file_path)
    if file_size > 100000:
        # Compress the image
        image = Image.open(file_path)
        image.save(file_path, optimize=True, quality=50)
        # repeat to ensure that the file size is under 100 Kb
        compress_image(filename)


with app.app_context():
    db.create_all()
    # TODO: Re-define this function to work with Okta.
    # populate_test_data()


@login_manager.user_loader
def load_user(id):
    return User.get(id)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/authorization-code/callback")
def callback():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    code = request.args.get("code")
    if not code:
        return "The code was not returned or is not accessible", 403
    query_params = {'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': request.base_url
                    }
    query_params = requests.compat.urlencode(query_params)
    exchange = requests.post(
        config["token_uri"],
        headers=headers,
        data=query_params,
        auth=(config["client_id"], config["client_secret"]),
    ).json()

    # Get tokens and validate
    if not exchange.get("token_type"):
        return "Unsupported token type. Should be 'Bearer'.", 403
    access_token = exchange["access_token"]
    id_token = exchange["id_token"]

    if not is_access_token_valid(access_token, config["issuer"]):
        return "Access token is invalid", 403

    if not is_id_token_valid(id_token, config["issuer"], config["client_id"], NONCE):
        return "ID token is invalid", 403

    # Authorization flow successful, get userinfo and login user
    userinfo_response = requests.get(config["userinfo_uri"],
                                     headers={'Authorization': f'Bearer {access_token}'}).json()

    user_id = userinfo_response["sub"]
    user_email = userinfo_response["email"]
    user_first_name = userinfo_response["given_name"]
    user_last_name = userinfo_response["family_name"]
    user_full_name = f"{user_first_name} {user_last_name}"
    user_profile_username = userinfo_response["profile_username"]

    user = User(
        name=user_full_name,
        username=user_profile_username,
        email=user_email,
        id=user_id
    )

    if not User.get(user_id):
        User.create(
            name=user.name,
            username=user.username,
            email=user.email,
            id=user.id
        )

    current_user.username = user.username
    login_user(user)
    return redirect(url_for("admin_view", username=user_profile_username))


@app.route("/login/okta")
def login_okta():
    # get request params
    query_params = {'client_id': config["client_id"],
                    'redirect_uri': config["redirect_uri"],
                    'scope': "openid email profile",
                    'state': APP_STATE,
                    'nonce': NONCE,
                    'response_type': 'code',
                    'response_mode': 'query'}

    # build request_uri
    request_uri = "{base_url}?{query_params}".format(
        base_url=config["auth_uri"],
        query_params=requests.compat.urlencode(query_params)
    )

    return redirect(request_uri)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/<username>/admin", methods=["GET", "POST"])
@login_required
def admin_view(username):
    user = User.query.filter_by(username=username).first()
    links = Link.query.filter_by(user_id=user.id).all()
    links = modify_links(links, TOTAL_ROWS)

    admin_form = AdminForm(bio=user.bio, links=links)
    profile_photo_form = PhotoForm()

    error = request.args.get('error')

    if flask.request.method == "POST":
        data = request.form
        bio = data["bio"]
        links_list = []

        if bio != user.bio:
            user.bio = bio
        for i in range(TOTAL_ROWS):
            label = request.form.get(f'links-{i}-label')
            url = request.form.get(f'links-{i}-url')
            if label and url:
                links_list.append({
                    "label": label,
                    "url": url,
                    "user_id": user.id
                })

        db.session.query(Link).filter_by(user_id=user.id).delete()
        db.session.bulk_insert_mappings(Link, links_list)
        db.session.commit()
        return redirect(url_for("enduser_view", username=username))

    return render_template("admin.html",
                           admin_form=admin_form,
                           profile_pic_url=user.profile_pic_url,
                           profile_photo_form=profile_photo_form,
                           username=username,
                           error=error)


@app.route('/<username>/upload', methods=['POST'])
def upload(username):
    # Get the uploaded file
    profile_photo = request.files['photo']
    if profile_photo:
        # Generate the filename using the username
        filename = f'{username}.jpg'
        # Save the file to the server
        profile_pic_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_photo.save(profile_pic_url)
        compress_image(filename)

        # Update the profile_pic_url for the user
        user = User.query.filter_by(username=username).first()
        # Trim the '.' at the beginning of the url
        user.profile_pic_url = profile_pic_url[1:]
        db.session.commit()
        return redirect(url_for("admin_view", username=username))
    return redirect(url_for("admin_view", username=username, error="No file was selected"))


@app.route("/<username>")
def enduser_view(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return "Try a different user, the user doesn't exist."
    links = Link.query.filter_by(user_id=user.id).all()
    return render_template("enduser.html", links=links, user=user)


if __name__ == "__main__":
    app.run(debug=True)
