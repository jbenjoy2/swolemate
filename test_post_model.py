import os
from unittest import TestCase
from sqlalchemy import exc

from models import User, db, Post, Likes

os.environ['DATABASE_URL'] = "postgresql:///swolemate-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """test general model functionality for User model"""

    def setUp(self):
        """add sample data"""
        db.drop_all()
        db.create_all()

        self.uid = 1111
        user = User.signup("test1@test.com", 'testpass',
                           'testuser1', 'Test', 'User', None, None)

        user.id = self.uid

        db.session.commit()

        self.user = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_post_model(self):
        """basic model test"""
        p = Post(title='testpost', details='this is a test post',
                 timestamp=None, user_id=self.uid, is_private=True)

        db.session.add(p)
        db.session.commit()

        self.assertEqual(len(self.user.posts), 1)
        self.assertEqual(self.user.posts[0].title, 'testpost')

    def test_post_like(self):
        p = Post(title='testpost', details='this is a test post',
                 timestamp=None, user_id=self.uid, is_private=True)

        db.session.add(p)
        db.session.commit()

        self.user.likes.append(p)
        db.session.commit()

        l = Likes.query.filter(Likes.user_id == self.uid).all()

        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].post_id, p.id)
