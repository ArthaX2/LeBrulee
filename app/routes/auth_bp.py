from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from app.forms.loginForm import LoginForm
from app.forms.resetUserForm import ResetUserForm
from app.models.users import User

from app.extensions import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth_bp.route("/reset", methods=["GET", "POST"])
def reset():
    """
    Allow a user to reset their password by username.

    This mirrors the logic you requested:
      - Look up user by username
      - If found, update password and show success flash
      - If not found, show error flash
    """
    form = ResetUserForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            # Use the same pattern as the User model (password_hash field)
            user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("User not found.", "danger")

    return render_template("auth/reset.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    errors = []

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        errors.append("Invalid username or password.")

    return render_template("auth/login.html", form=form, errors=errors)

