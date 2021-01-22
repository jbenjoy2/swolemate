from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

# connect database to app


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    """basic user model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, unique=True, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default='/static/default-pic.png')
    bio = db.Column(db.Text)
    # set up relationships
    posts = db.relationship('Post')

    likes = db.relationship('Post', secondary="likes")

    def __repr__(self):
        return f"<User #{self.id}: {self.email} - {self.username}>"

    # signup/authenticate methods
    @classmethod
    def signup(cls, email, password, username, first_name, last_name, image_url):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        new_user = User(
            email=email,
            password=hashed_pwd,
            username=username,
            first_name=first_name,
            last_name=last_name,
            image_url=image_url
        )

        db.session.add(new_user)
        return new_user

    @classmethod
    def authenticate(cls, email, password):
        """authenticate based on email/password; username is for display purposes"""
        user = cls.query.filter_by(email=email).first()

        if user:
            is_authorized = bcrypt.check_password_hash(user.password, password)
            if is_authorized:
                return user
            else:
                return 'invalid password'

        return False

    @classmethod
    def change_info(cls, user_id, username, password):
        user = cls.query.get(user_id)

        new_password = bcrypt.generate_password_hash(password).decode('UTF-8')
        user.username = username
        user.password = new_password
        db.session.add(user)

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'image_url': self.image_url
        }


class Post(db.Model):
    """an individual workout post"""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    details = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    is_private = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User')

    def serialize(self):
        return {
            'id': self.id,
            'details': self.details,
            'timestamp': self.timestamp.strftime('%b %d, %Y'),
            'user_id': self.user_id,
            'is_private': self.is_private
        }


class Likes(db.Model):
    """mapping workout posts to user likes"""
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id', ondelete='CASCADE'), unique=True)
