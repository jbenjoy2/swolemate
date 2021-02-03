import os
from unittest import TestCase
from sqlalchemy import exc

from models import User, db, Post, Muscle, PostMuscle

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

        p1 = Post(id=5678, title='testpost1', details='this is a test post',
                  is_private=False, user_id=self.uid, timestamp=None)

        db.session.add(p1)
        db.session.commit()
        self.postid = 5678
        self.post = Post.query.get(5678)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_muscle_model(self):
        """basic functionality of muscle class"""

        m = Muscle(name='testmuscle', body_part='arms')

        db.session.add(m)
        db.session.commit()

        test = Muscle.query.get(m.id)

        self.assertEqual(test.name, 'testmuscle')
        self.assertEqual(test.body_part, 'arms')

    def test_muscle_posts(self):
        """test post to muscle association"""
        m = Muscle(name='testmuscle', body_part='arms')

        db.session.add(m)
        db.session.commit()

        pm = PostMuscle(muscle_id=m.id, post_id=self.postid)
        db.session.add(pm)
        db.session.commit()

        # post.muscles should know have the testmuscle in it, and muscle.posts should have the test post in it
        self.assertEqual(len(self.post.muscles), 1)
        self.assertEqual(len(m.posts), 1)
        self.assertEqual(self.post.muscles[0].name, 'testmuscle')
        self.assertEqual(m.posts[0].title, 'testpost1')
