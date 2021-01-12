import os
from flask import Flask, render_template, request, redirect, session, url_for
from authlib.integrations.flask_client import OAuth
from models import db, connect_db, User

CLIENT_ID = '68392004616-tj0jco6efikrqfn9p52b604oc8hn9vql.apps.googleusercontent.com'
CLIENT_SECRET = 'X1M_cmpQDgit6r0rBVFCZt1G'
CURRENT_USER_KEY = 'current_user'
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'itsasecretshhhh')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///swolemate')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
appp.config['SQLALCHEMY_ECHO'] = True

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
    session[CURRENT_USER_KEY] = user.id


def do_logout():
    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]


@app.route('/sign-in')
def show_login_page():
    if CURRENT_USER_KEY in session:
        return redirect('/')

    return render_template('signin.html')


@app.route('/')
def show_home_page():
    if CURRENT_USER_KEY in session:
        user = User.query.get(session[CURRENT_USER_KEY])
        return render_template('index.html', user=user)
    return redirect('/sign-in')


@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
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
    user = User.query.filter_by(User.email=email).first()

    if not user:
        User.signup(email=email, password='password1',
                    image_url=User.image_url.default.arg)
        db.session.commit()
        do_login(user)
        return redirect('/password-reset')
    else:
        do_login(user)
        return redirect('/')


@app.route('/logout', methods=['post'])
def logout():
    do_logout()
    return redirect('/')
