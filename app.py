from time import sleep

from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, Length, InputRequired
from flask_bcrypt import Bcrypt

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config["SECRET_KEY"] = "MatthewMichaelMattMurdock"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(
        # validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={
            "placeholder": "Username",
            "class": "form-control mt-3 mb-1"
        })
    password = PasswordField(
        # validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={
            "placeholder": "Password",
            "class": "form-control mt-1 mb-1"
        })
    confirm_password = PasswordField(
        # validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={
            "placeholder": "Confirm password",
            "class": "form-control mt-1 mb-3"
        })
    submit = SubmitField("Register", render_kw={
        "class": "btn btn-dark mt-3 mb-3"
    })

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            flash("Username already in use", "danger")
            raise ValidationError("Username already exists.")


class LoginForm(FlaskForm):
    username = StringField(
        # validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={
            "placeholder": "Username",
            "class": "form-control mt-3 mb-1"
        })
    password = PasswordField(
        # validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={
            "placeholder": "Password",
            "class": "form-control mt-1 mb-3"
        })
    submit = SubmitField("Log in", render_kw={
        "class": "btn btn-dark mt-3 mb-3"
    })


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    else:
        return render_template("home.html")


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    logout_user()
    flash("Logged out", "primary")
    return redirect(url_for("home"))


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        if not form.username.data:
            flash("Missing username", "danger")
            return render_template("login.html", form=form)

        if not form.password.data:
            flash("Missing password", "danger")
            return render_template("login.html", form=form)

        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Logged in successfully", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Incorrect username or password", "danger")
                return render_template("login.html", form=form)
        else:
            flash("Incorrect username or password", "danger")
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if not form.username.data:
            flash("Missing username", "danger")
            return render_template("register.html", form=form)

        if not form.password.data:
            flash("Missing password", "danger")
            return render_template("register.html", form=form)

        if not form.confirm_password.data:
            flash("Missing password confirmation", "danger")
            return render_template("register.html", form=form)

        if form.password.data != form.confirm_password.data:
            flash("Confirmed password doesn't match password", "danger")
            return render_template("register.html", form=form)

        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User()
        new_user.username = form.username.data
        new_user.password = hashed_password
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully', "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
