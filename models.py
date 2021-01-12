from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

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
    username = db.Column(db.Text, unique=True)
    image_url = db.Column(db.Text, default='/static/default-pic.png')
    bio = db.Column(db.Text)
    # set up relationships
    posts = db.relationship('Post')

    likes = db.relationship('Post', secondary="likes")

    def __repr__(self):
        return f"<User #{self.id}: {self.email} - {self.username}>"

    # signup/authenticate methods
    @classmethod
    def signup(cls, email, password, image_url):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        new_user = User(
            email=email,
            password=hashed_pwd,
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
        return False
