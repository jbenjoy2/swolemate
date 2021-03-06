from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, BooleanField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import InputRequired, Email, Length, EqualTo


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class UserAddForm(FlaskForm):
    new_email = StringField(
        'E-Mail', validators=[InputRequired(), Email()], render_kw={"autofocus": True})
    new_password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8)])
    confirm = PasswordField('Confirm Password', validators=[
        InputRequired(), Length(min=8), EqualTo('new_password', message='Passwords must match')])
    new_username = StringField('Username', validators=[
                               InputRequired(), Length(max=30)])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    image_url = StringField('(Optional) Image URL')
    cover_url = StringField('(Optional) Cover Photo URL')


class UserEditForm(FlaskForm):
    email = StringField(
        'E-Mail', validators=[InputRequired(), Email()], render_kw={"autofocus": True})
    username = StringField('Username',
                           validators=[Length(max=25)])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    image_url = StringField('(Optional) Image URL')
    cover_url = StringField('(Optional) Cover Photo URL')
    bio = TextAreaField('(Optional) Tell us about yourself!')


class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8)])


class ForcedResetForm(FlaskForm):
    username = StringField(
        'Create Username*', validators=[InputRequired(), Length(max=25)])
    password = PasswordField('Create Password*', validators=[
        InputRequired(), Length(min=8), EqualTo('confirm', message='Passwords must match')], id='forced')
    confirm = PasswordField('Confirm Password', validators=[
        InputRequired(), Length(min=8)], id='confirm_forced')


class PostForm(FlaskForm):
    title = StringField(
        'Title*', validators=[InputRequired(), Length(min=6, max=50)])
    details = TextAreaField(
        'Workout Details*', validators=[InputRequired()])
    muscles = MultiCheckboxField(
        'Muscles Worked', coerce=int, validators=[InputRequired()])
    equipment = MultiCheckboxField(
        'Equipment used', coerce=int, validators=[InputRequired()])
    is_private = BooleanField('Make this post private')
