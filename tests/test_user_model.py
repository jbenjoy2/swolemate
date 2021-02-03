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

        u1 = User.signup("test1@test.com", 'testpass',
                         'testuser1', 'Test', 'User', None, None)
        u1id = 1111
        u1.id = u1id

        u2 = User.signup("test2@test.com", "testpass",
                         "testuser2", "Test", "User2", None, None)

        u2id = 2222
        u2.id = u2id

        db.session.commit()

        u1 = User.query.get(u1id)
        u2 = User.query.get(u2id)

        self.u1 = u1
        self.u1id = u1id

        self.u2 = u2
        self.u2id = u2id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """test basic functioanlity of user model"""
        u = User(email='test3@test.com', password='testpass',
                 username='testuser3', first_name='Test', last_name='User3')

        db.session.add(u)
        db.session.commit()
        user = User.query.get(self.u1id)
        self.assertEqual(len(u.likes), 0)
        self.assertEqual(str(user),
                         f'<User #{user.id}: {user.email} - {user.username}>')

    # -------registration tests------

    def test_valid_signup(self):
        user_test = User.signup('test3@test.com', 'testpass',
                                'testuser3', 'Test', 'User3', None, None)

        uid = 3333333
        user_test.id = uid
        db.session.commit()

        user_test = User.query.get(uid)
        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.email, 'test3@test.com')
        self.assertEqual(user_test.username, 'testuser3')
        self.assertEqual(user_test.first_name, 'Test')
        # test that bcrypt worked
        self.assertNotEqual(user_test.password, 'testpass')
        self.assertTrue(user_test.password.startswith("$2b$"))

    def test_invalid_email(self):
        user_test = User.signup(None, 'testpass',
                                'testuser3', 'Test', 'User3', None, None)

        uid = 33333333
        user_test.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_username(self):
        user_test = User.signup('test3@test.com', 'testpass',
                                None, 'Test', 'User3', None, None)
        uid = 33333333
        user_test.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_first_name(self):
        user_test = User.signup('test3@test.com', 'testpass',
                                'testuser3', None, 'User3', None, None)
        uid = 33333333
        user_test.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_last_name(self):
        user_test = User.signup('test3@test.com', 'testpass',
                                'testuser3', 'Test', None, None, None)
        uid = 33333333
        user_test.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password(self):
        with self.assertRaises(ValueError) as context:
            User.signup('test3@test.com', None,
                        'testuser3', 'Test', 'User3', None, None)
        with self.assertRaises(ValueError) as context:
            User.signup('test3@test.com', '',
                        'testuser3', 'Test', 'User3', None, None)

    # ---authentication tests-----

    def test_valid_authentication(self):
        user_test = User.authenticate(self.u1.email, 'testpass')

        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.id, self.u1id)

    def test_invalid_email_authentication(self):
        user_test = User.authenticate('test3434@test.com', 'testpass')

        self.assertFalse(user_test)

    def test_invalid_password_authentication(self):
        user_test = User.authenticate(self.u1.email, 'testpasss')

        self.assertEqual(user_test, 'invalid password')

    # info change tests

    def test_valid_change(self):
        User.change_info(self.u1id, 'testuserchange', 'password')

        db.session.commit()

        user = User.query.get(self.u1id)

        self.assertEqual(user.username, 'testuserchange')
        self.assertEqual(user.email, 'test1@test.com')
