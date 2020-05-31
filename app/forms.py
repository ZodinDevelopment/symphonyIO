from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FileField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from app.models import User, Track


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username already taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("That email is already registered with an account.")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About Me", validators=[Length(min=0, max=256)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()

            if user is not None:
                raise ValidationError("Username already taken.")



class PostForm(FlaskForm):
    post = TextAreaField("Message to your fans", validators=[DataRequired()])
    submit = SubmitField("Post")


class UploadForm(FlaskForm):
    title = StringField("Track Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Length(min=0, max=512)])
    upload = FileField("Audio File", validators=[FileRequired()])
    submit = SubmitField("Upload")

    def validate_title(self, title):
        track = Track.query.filter_by(title=title.data).first()
        if track is not None:
            raise ValidationError('Track name is already being used.')


