from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, EqualTo


class UserAddForm(FlaskForm):
    new_email = StringField('E-Mail', validators=[InputRequired(), Email()])
    new_password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', validators=[
        InputRequired(), Length(min=8)])
    image_url = StringField('(Optional) Image URL')


class UserEditForm(FlaskForm):
    email = StringField('E-Mail', validators=[InputRequired(), Email()])
    username = StringField('(Optional) Username/Display Name',
                           validators=[Length(max=25)])
    image_url = StringField('(Optional) Image URL')
    bio = TextAreaField('(Optional) Tell us about yourself!')


class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8)])


class ForcedPasswordResetForm(FlaskForm):
    password = PasswordField('Create Password*', validators=[
        InputRequired(), Length(min=8), EqualTo('confirm', message='Passwords must match')], id='forced')
    confirm = PasswordField('Confirm Password', validators=[
        InputRequired(), Length(min=8)], id='confirm_forced')
