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
    cover_url = db.Column(
        db.Text, default='https://images.unsplash.com/photo-1594737625785-a6cbdabd333c?ixid=MXwxMjA3fDF8MHxzZWFyY2h8MXx8Z3ltfGVufDB8fDB8&ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60')
    bio = db.Column(db.Text)
    # set up relationships
    posts = db.relationship('Post', order_by='Post.id.desc()')

    likes = db.relationship('Post', secondary="likes")

    def __repr__(self):
        return f"<User #{self.id}: {self.email} - {self.username}>"

    # signup/authenticate methods
    @classmethod
    def signup(cls, email, password, username, first_name, last_name, image_url, cover_url):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        new_user = User(
            email=email,
            password=hashed_pwd,
            username=username,
            first_name=first_name,
            last_name=last_name,
            image_url=image_url,
            cover_url=cover_url
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
        """method to update username and password after google auth sets temp versions"""
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
            'image_url': self.image_url,
            'cover_url': self.cover_url
        }


class Post(db.Model):
    """an individual workout post"""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    is_private = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User')

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'details': self.details,
            'timestamp': self.timestamp.strftime('%b %d, %Y'),
            'user': self.user.serialize(),
            'is_private': self.is_private,
            'muscles': [muscle.serialize() for muscle in self.muscles],
            'equipment': [equipment.serialize() for equipment in self.equipment]
        }


class Likes(db.Model):
    """mapping workout posts to user likes"""
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id', ondelete='CASCADE'))


class Muscle(db.Model):
    """basic muscle model"""
    __tablename__ = 'muscles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    body_part = db.Column(db.Text, nullable=False)
    # image = db.Column(db.Text, nullable=False)

    posts = db.relationship(
        'Post', secondary='posts_muscles', backref='muscles')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'body_part': self.body_part
        }


class Equipment(db.Model):
    """basic model for piece of workout equipment"""
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    # image = db.Column(db.Text, nullable=False)

    posts = db.relationship(
        'Post', secondary='posts_equipment', backref='equipment')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class PostMuscle(db.Model):
    """linking workout posts to the muscles used"""

    __tablename__ = 'posts_muscles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id', ondelete='CASCADE'), nullable=False)
    muscle_id = db.Column(db.Integer, db.ForeignKey(
        'muscles.id', ondelete='CASCADE'), nullable=False)


class PostEquipment(db.Model):
    """linking workout posts to equipment used"""
    __tablename__ = 'posts_equipment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id', ondelete='CASCADE'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey(
        'equipment.id', ondelete='CASCADE'), nullable=False)
