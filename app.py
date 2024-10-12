from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Optional, Length, Regexp
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from datetime import datetime
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'QWERTYUIOP'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///db.sqlite'

db = SQLAlchemy()
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

db.init_app(app)
app.app_context().push()
db.create_all()

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=10),
        Regexp(r'^[a-zA-Z0-9_]*$', message="Username must only contain letters, numbers, and underscores.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=16),
        Regexp(r'^[a-zA-Z0-9+=-_]*$', message="Password must contain only letters, numbers, and the +=-_ characters.")
    ])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

@app.route('/signup', methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    elif form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('That username is already taken. Please choose a different one.', 'danger')
            return render_template('signup.html', signup_form=form)
        else:
            user = User(username=form.username.data, password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            next_url = request.args.get('next', url_for('index')) 
            return redirect(next_url)
    return render_template('signup.html', signup_form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    elif form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Incorrect username or password. Try again.', 'danger')
            return render_template('login.html', login_form=form)
    return render_template('login.html', login_form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/location')
def location():
    return render_template("location.html")

@app.route('/')
def index():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
