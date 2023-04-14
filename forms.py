from flask_wtf import FlaskForm
from wtforms import DateTimeField, EmailField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditorField


class ContactForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    message = CKEditorField("Message", validators=[DataRequired()])
    submit = SubmitField("Send message")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register", validators=[DataRequired()])


class TaskForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    end_date = DateTimeField("End date (dd-mm-yyyy)", validators=[DataRequired()], format="%d-%m-%Y")
    description = CKEditorField("Description")
    tag = SelectField("Tag", choices=["Birthday", "None", "Personal", "Urgent", "Work"])
    submit = SubmitField("Post task")
