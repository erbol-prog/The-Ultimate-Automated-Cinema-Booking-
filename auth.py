import requests
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import User
from flask_login import login_user, logout_user, current_user, login_required

auth = Blueprint('auth', __name__)


RECAPTCHA_SECRET = "6LdHH5wqAAAAALECaOIJ-hOqh_GIBLE43D4s6epB"


def verify_recaptcha(token, action):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        'secret': RECAPTCHA_SECRET,
        'response': token
    }
    response = requests.post(url, data=data)
    result = response.json()
    if result.get("success") and result.get("action") == action and result.get("score", 0) > 0.5:
        return True
    return Fal

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validation for input fields
        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        # Password matching validation
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("auth.register"))

        # Password complexity validation
        if len(password) < 6 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            flash("Password must be at least 6 characters long, include at least one letter and one number.", "danger")
            return redirect(url_for("auth.register"))

        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists!", "danger")
            return redirect(url_for("auth.register"))

        # Create a new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # Use the model's password hashing method
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'SuperAdmin':
                return redirect(url_for('super_admin_panel'))
            elif user.role == 'Admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('user_panel'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
