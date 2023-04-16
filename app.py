from flask import flash, Flask, jsonify, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import current_user, LoginManager, login_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from forms import ContactForm, LoginForm, RegisterForm, TaskForm
from datetime import datetime
import os
import smtplib
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import BooleanField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
Bootstrap(app)
ckeditor = CKEditor(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "ad3aadsAAd3d33faDsDF4w3rqdFFASDFQqd3qd3RF4QW"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    class User(UserMixin, db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(250), unique=True, nullable=False)
        password = db.Column(db.String(250), nullable=False)
        name = db.Column(db.String(100), nullable=False)
        tasks = relationship("Task", back_populates="author")

    class Task(db.Model):
        __tablename__ = "tasks"
        id = db.Column(db.Integer, primary_key=True)
        author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
        author = relationship("User", back_populates="tasks")
        task = db.Column(db.String, nullable=False)
        end_date = db.Column(db.DateTime, nullable=False)
        description = db.Column(db.Text)
        tag = db.Column(db.String, nullable=False)


    # The next line can be commented out once the database is created
    # db.create_all()


    @app.route("/")
    def home():
        return render_template("index.html")
    

    @app.route("/register", methods=["GET", "POST"])
    def register():
        register_form = RegisterForm()
        if register_form.validate_on_submit():
            if User.query.filter_by(email=request.form.get("email")).first():
                # This means this user already exists
                flash("You've already signed up with this email. Please log in instead.")
                return redirect(url_for("login"))
            
            hashed_password = generate_password_hash(register_form.password.data, "pbkdf2:sha256", salt_length=8)
            new_user = User(
                email = register_form.email.data,
                password = hashed_password,
                name = register_form.name.data,
                tasks = []
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("dashboard", user_id=new_user.id))
        return render_template("register.html", form=register_form)
    

    @app.route("/login", methods=["GET", "POST"])
    def login():
        login_form = LoginForm()
        if login_form.validate_on_submit():
            email = login_form.email.data
            password = login_form.password.data
            user = User.query.filter_by(email=email).first()
            if not user:
                # Wrong email
                flash("There's no user with that email. Please try again.")
                return redirect(url_for("login"))
            elif not check_password_hash(user.password, password):
                # Wrong password
                flash("Wrong password. Please try again.")
                return redirect(url_for("login"))
            else:
                login_user(user)
                return redirect(url_for("dashboard", user_id=user.id))            
        return render_template("login.html", form=login_form, current_user=current_user)
    

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("home"))
    

    @app.route("/<int:user_id>/dashboard")
    def dashboard(user_id):
        user = User.query.get(user_id)
        tasks = user.tasks
        if not current_user.is_authenticated:
            flash("You need to log in or register to use the app.")
            return redirect(url_for("login"))
        return render_template("dashboard.html", user=user, tasks=tasks, current_user=current_user)


    @app.route("/create_task", methods=["GET", "POST"])
    def create_task():
        task_form = TaskForm()
        if not current_user.is_authenticated:
            flash("You need to log in or register use the app.")
            return redirect(url_for("login"))
        
        if task_form.validate_on_submit():
            new_task = Task(
                author_id = current_user.id,
                task = task_form.task.data,
                end_date = task_form.end_date.data,
                description = task_form.description.data,
                tag = task_form.tag.data
            )
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for("dashboard", user_id=current_user.id))
        return render_template("create_task.html", form=task_form)
    

    @app.route("/edit-task/<int:task_id>", methods=["GET", "POST"])
    def edit_task(task_id):
        if not current_user.is_authenticated:
            flash("You need to log in or register to use the app.")
            return redirect(url_for("login"))
        
        task = Task.query.get(task_id)
        edit_form = TaskForm(
            task = task.task,
            end_date = task.end_date,
            description = task.description,
            tag = task.tag
        )
        if edit_form.validate_on_submit():
            task.task = edit_form.task.data
            task.end_date = edit_form.end_date.data
            task.description = edit_form.description.data
            task.tag = edit_form.tag.data
            db.session.commit()
            return redirect(url_for("dashboard", user_id=current_user.id))
        return render_template("create_task.html", form=edit_form, is_edit=True, current_user=current_user)


    @app.route("/delete/<int:task_id>")
    def delete_task(task_id):
        if not current_user.is_authenticated:
            flash("You need to log in or register to use the app.")
            return redirect(url_for("login"))
        task_to_delete = Task.query.get(task_id)
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for("dashboard", user_id=current_user.id))
    

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        contact_form = ContactForm()
        if contact_form.validate_on_submit():
            with smtplib.SMTP("smtp.gmail.com") as connection:
                my_email = "something@gmail.com"
                password = "somerandomepassword"
                connection.starttls()
                connection.login(user=my_email, password=password)
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs="vlad@vladalbert.tech",
                    msg=f"Subject: {contact_form.email.data}\n\n{contact_form.message.data}"
                )
                if current_user.is_authenticated:
                    return redirect(url_for("dashboard", user_id=current_user.id))
                else:
                    return redirect(url_for("home"))
        return render_template("contact.html", form=contact_form, current_user=current_user)


    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8080)
