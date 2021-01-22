import os
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from authlib.integrations.flask_client import OAuth
from models import db, connect_db, User, Post
from forms import UserAddForm, UserEditForm, LoginForm, ForcedResetForm, PostForm
from google_auth import id, secret
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

CLIENT_ID = id
CLIENT_SECRET = secret
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
    client_id=id,
    client_secret=secret,
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


# custom 404 and 401
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(401)
def show_401(e):
    return render_template('401.html'), 401

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
    print(user_info)
    email = user_info['email']
    first_name = user_info['given_name'].capitalize()
    last_name = user_info['family_name'].capitalize()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google

    # compare with database;
    user = User.query.filter_by(email=email).first()
    print(user)

    if not user:
        user = User.signup(email=email, password='password1', username='temporary',
                           first_name=first_name, last_name=last_name, image_url=User.image_url.default.arg)
        db.session.commit()
        do_login(user)
        return redirect(f'/user/{user.id}/force-reset')
    else:
        do_login(user)
        return redirect('/')


@app.route('/user/<int:user_id>/force-reset', methods=['GET', 'POST'])
def force_reset_password(user_id):
    if CURRENT_USER_KEY not in session or session[CURRENT_USER_KEY] != user_id:
        do_logout()
        return redirect('/sign-in')

    user = User.query.get_or_404(user_id)
    form = ForcedResetForm()

    if form.validate_on_submit():
        User.change_info(
            user_id=user_id, username=form.username.data, password=form.password.data)
        db.session.commit()
        flash('User information successfully changed!', 'success')
        return redirect('/')
    return render_template('/forced_reset.html', form=form, user=user)


# main user routes outside of google oauth

# api routes
@app.route('/api/users/<int:user_id>')
def get_user_info(user_id):
    user = User.query.get(user_id)

    return jsonify(user=user.serialize())


@app.route('/api/posts')
def show_posts():
    page = int(request.args.get('page', 1))
    if CURRENT_USER_KEY in session:
        posts = Post.query.order_by(Post.id.desc()).paginate(
            page=page, per_page=10, error_out=True)
    else:
        posts = Post.query.filter_by(is_private='f').order_by(Post.id.desc()).paginate(
            page=page, per_page=10, error_out=True)

    all_posts = [post.serialize() for post in posts.items]
    return jsonify(has_next=posts.has_next, posts=all_posts)


@ app.route('/register', methods=['POST'])
def register_new_user():
    if CURRENT_USER_KEY in session:
        return redirect('/')
    register_form = UserAddForm()
    login_form = LoginForm()

    if register_form.validate_on_submit():
        try:
            user = User.signup(
                email=register_form.new_email.data,
                password=register_form.new_password.data,
                username=register_form.new_username.data,
                first_name=register_form.first_name.data,
                last_name=register_form.last_name.data,
                image_url=register_form.image_url.data or User.image_url.default.arg
            )
            db.session.commit()

            do_login(user)
            return redirect('/')
        except IntegrityError:
            flash("Email already registered! Please log in or try again", 'danger')
            return render_template('home_anon.html', register_form=register_form, login_form=login_form)

    else:
        return render_template('home_anon.html', register_form=register_form, login_form=login_form)


@ app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user_profile(user_id):
    if CURRENT_USER_KEY not in session or session[CURRENT_USER_KEY] != user_id:
        do_logout()
        return redirect('/')

    user = User.query.get_or_404(user_id)

    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        try:
            user.email = form.email.data
            user.username = form.username.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.image_url = form.image_url.data or User.image_url.default.arg
            user.bio = form.bio.data

            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(
                "Email or Username already taken!! Please try again", 'danger')
            return render_template('edit_profile.html', form=form, user=user, img_src=user.image_url)

        flash('Profile Successfully Updated!', 'success')
        return redirect(url_for('show_user_profile', user_id=user.id))
    return render_template('edit_profile.html', form=form, user=user, img_src=user.image_url)


@ app.route('/', methods=['GET', 'POST'])
def show_home_page():
    """route to show main welcome page...may delete or alter later"""
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
            flash(f'Hello, {user.username}!', 'warning')
            return render_template('home.html', user=user)
        # handle invalid password entry
        elif user == 'invalid password':
            login_form.password.errors = ["Incorrect Password."]
            return render_template('home_anon.html', login_form=login_form, register_form=register_form)
        # handle user being not found
        else:
            login_form.email.errors = [
                'Invalid Credentials. Please check email/password and try again']
            return render_template('home_anon.html', login_form=login_form, register_form=register_form)
    if CURRENT_USER_KEY in session:
        user = User.query.get(session[CURRENT_USER_KEY])
        return render_template('home.html', user=user)
    # redirect to sign in page if no user is logged in
    return render_template('home_anon.html', login_form=login_form, register_form=register_form, img_cls='hidden')


@ app.route('/user/<int:user_id>/logout', methods=['GET', 'POST'])
def logout(user_id):
    """route to log user out of app"""
    if CURRENT_USER_KEY not in session or session[CURRENT_USER_KEY] != user_id:
        raise Unauthorized()
    do_logout()
    return redirect('/')


@ app.route('/user/<int:user_id>')
def show_user_profile(user_id):
    if CURRENT_USER_KEY not in session:
        raise Unauthorized
    user = User.query.get_or_404(user_id)

    return render_template('user_profile.html', user=user)

# route for posting workouts


@ app.route('/user/<int:user_id>/posts/new', methods=['GET', 'POST'])
def create_post(user_id):
    if CURRENT_USER_KEY not in session or session[CURRENT_USER_KEY] != user_id:
        do_logout()
        return redirect('/sign-in')

    user = User.query.get_or_404(user_id)

    form = PostForm()

    if form.validate_on_submit():
        post = Post(details=form.details.data,
                    is_private=form.is_private.data, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        flash('New post created!', 'success')
        return redirect(url_for('show_user_profile', user_id=user_id))
    return render_template('add_post.html', form=form, user=user)


@ app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)
    return render_template('show_post.html', post=post, user=user)