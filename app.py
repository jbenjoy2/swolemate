import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from authlib.integrations.flask_client import OAuth
from models import db, connect_db, User
from forms import UserAddForm, UserEditForm, LoginForm, ForcedPasswordResetForm
from sqlalchemy.exc import IntegrityError

CLIENT_ID = '68392004616-tj0jco6efikrqfn9p52b604oc8hn9vql.apps.googleusercontent.com'
CLIENT_SECRET = 'X1M_cmpQDgit6r0rBVFCZt1G'
CURRENT_USER_KEY = 'current_user'
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'itsasecretshhhh')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///swolemate')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

# set up google oauth first
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    # This is only needed if using openId to fetch user info
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},


)

# main login/logout functionality


def do_login(user):
    """helper method to login user upon authentication"""
    session[CURRENT_USER_KEY] = user.id


def do_logout():
    """helper method to log out user"""
    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]

# google oauth routes


@app.route('/login')
def login():
    """google oauth login route. redirects to the google oauth authorize route"""
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    """google oauth authorize route handles google login and also adds user/compares with database and session"""

    google = oauth.create_client('google')  # create the google oauth client
    # Access token from google (needed to get user info)
    token = google.authorize_access_token()
    # userinfo contains stuff u specificed in the scrope
    resp = google.get('userinfo')
    user_info = resp.json()
    email = user_info['email']
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google

    # compare with database;
    user = User.query.filter_by(email=email).first()
    print(user)

    if not user:
        user = User.signup(email=email, password='password1',
                           image_url=User.image_url.default.arg)
        db.session.commit()
        do_login(user)
        return redirect(f'/user/{user.id}/force-password-reset')
    else:
        do_login(user)
        return redirect('/')


@app.route('/sign-in', methods=['GET', 'POST'])
def show_login_page():
    """route to sign in user through database directly, not through google oauth"""

    # don't let logged in users see this screen
    if CURRENT_USER_KEY in session:
        return redirect('/')

    # create login form instance
    login_form = LoginForm()
    # create register form instance to go in modal
    register_form = UserAddForm()

    # handle login form validation
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data

        user = User.authenticate(email, password)

        # handle use case for a user being returned with valid password entered
        if user and user != 'invalid password':
            do_login(user)
            if user.username:
                flash(f'Hello, {user.username}!', 'warning')
            else:
                flash(f'Hello, {user.email}!', 'warning')
            return redirect('/')
        # handle invalid password entry
        elif user == 'invalid password':
            login_form.password.errors = ["Incorrect Password."]
            return render_template('signin.html', form=form)
        # handle user being not found
        else:
            login_form.email.errors = [
                'Invalid Credentials. Please check email/password and try again']

    return render_template('signin.html', login_form=login_form, register_form=register_form)


@app.route('/')
def show_home_page():
    """route to show main welcome page...may delete or alter later"""
    if CURRENT_USER_KEY in session:
        user = User.query.get(session[CURRENT_USER_KEY])
        return render_template('index.html', user=user)
    # redirect to sign in page if no user is logged in
    return redirect('/sign-in')


@app.route('/logout', methods=['POST'])
def logout():
    do_logout()
    return redirect('/')


@app.route('/user/<int:user_id>/force-password-reset', methods=['GET', 'POST'])
def force_reset_password(user_id):
    if CURRENT_USER_KEY not in session or session[CURRENT_USER_KEY] != user_id:
        do_logout()
        return redirect('/sign-in')

    user = User.query.get_or_404(user_id)
    form = ForcedPasswordResetForm()

    if form.validate_on_submit():
        User.change_password(user_id=user_id, password=form.password.data)
        db.session.commit()
        flash('Password successfully changed!', 'success')
        return redirect('/')
    return render_template('/forced_reset.html', form=form, user=user)


@app.route('/register', methods=['POST'])
def register_new_user():
    if CURRENT_USER_KEY in session:
        return redirect('/')
    register_form = UserAddForm()
    login_form = LoginForm()

    if register_form.validate_on_submit():
        try:
            user = User.signup(
                email=register_form.email.data,
                password=register_form.password.data,
                image_url=register_form.image_url.data or User.image_url.default.arg
            )
            db.session.commit()
        except IntegrityError:
            flash("Email already registered! Please log in or try again", 'danger')
            return render_tamplate('signin.html', register_form=register_form, login_form=login_form)

        do_login(user)
        return redirect('/')
    else:
        return render_template('signin.html', register_form=register_form)
