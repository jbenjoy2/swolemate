import os
from unittest import TestCase
from sqlalchemy import exc

from models import User, db, Post, Equipment, PostEquipment

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
        """basic functionality of equipment class"""

        e = Equipment(name='hammer')

        db.session.add(e)
        db.session.commit()

        test = Equipment.query.get(e.id)

        self.assertEqual(test.name, 'hammer')

    def test_equipment_posts(self):
        """test post to equipment association"""
        e = Equipment(name='hammer')

        db.session.add(e)
        db.session.commit()

        pe = PostEquipment(equipment_id=e.id, post_id=self.postid)
        db.session.add(pe)
        db.session.commit()

        # post.equipment should know have the hammer in it, and equipment.posts should have the test post in it
        self.assertEqual(len(self.post.equipment), 1)
        self.assertEqual(len(e.posts), 1)
        self.assertEqual(self.post.equipment[0].name, 'hammer')
        self.assertEqual(e.posts[0].title, 'testpost1')
