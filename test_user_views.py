"""Test View Functions of User pages"""
import os
from unittest import TestCase
from models import db, connect_db, Post, User, Likes
os.environ['DATABASE_URL'] = 'postgresql:///swolemate-test'
from app import app, CURRENT_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class UserViewTestCase(TestCase):
    """test views for user"""

    def setUp(self):
        """create test client, add sample data"""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(email='test@test.com', password="testpass",
                                    username='testuser1', first_name='Test', last_name='User', image_url=User.image_url.default.arg, cover_url=User.cover_url.default.arg)
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id

        db.session.commit()

        self.test_post_public = Post(title='public', details='Public Test Post', is_private=False,
                                     timestamp=Post.timestamp.default.arg, user_id=self.testuser_id)

        self.test_post_private = Post(title='private', details='Private Test Post',
                                      is_private=True, timestamp=Post.timestamp.default.arg, user_id=self.testuser_id)

        db.session.add_all([self.test_post_public, self.test_post_private])
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_register_user(self):
        with self.client as c:
            data = {
                "new_email": 'test2@test.com',
                "new_password": 'testpass',
                "confirm": 'testpass',
                "new_username": 'testuser2',
                "first_name": 'test',
                "last_name": 'user2',
                "image_url": None,
                "cover_url": None
            }
            resp = c.post('/register', data=data)
            self.assertEqual(resp.status_code, 302)
            user = User.query.filter_by(username='testuser2').first()
            self.assertEqual(user.last_name, 'User2')

    def test_login_user(self):
        with self.client as c:
            data = {"email": "test@test.com", "password": 'testpass'}
            resp = c.post('/', data=data)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="card user-card mb-3">', html)

    def test_anon_homepage(self):
        with self.client as c:
            resp = c.get('/')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                'Swolemate is a way for people to both share their own workouts', html)

    def test_auth_homepage(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            resp = c.get('/')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<div class="card user-card mb-3">', html)

    def test_show_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser.id

            user = User.query.get(self.testuser_id)
            resp = c.get(f"/user/{self.testuser_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f'<h4 id="sidebar-username">@{user.username}</h4>', html)

    def test_show_user_unauthorized(self):
        with self.client as c:
            resp = c.get(f"/user/{self.testuser_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 401)
            self.assertIn(
                '<p class="pt-5">You do not have permission to view this page </p>', html)

    def test_show_user_edit(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id
            user = User.query.get(self.testuser_id)
            resp = c.get(f"/user/{self.testuser_id}/edit",
                         follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<a href="/" class="btn btn-lg btn-danger col-5 form-control">Cancel</a>', html)

    def test_show_user_edit_no_authentication(self):
        with self.client as c:
            resp = c.get(f"/user/{self.testuser_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 401)
            self.assertIn(
                '<p class="pt-5">You do not have permission to view this page </p>', html)

    def test_show_user_edit_unauthorized(self):
        u2 = User.signup(email='test2@test.com', password='testpass', username="testuser2",
                         first_name='Test', last_name='User2', image_url=None, cover_url=None)
        u2.id = 5678
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = u2.id

            resp = c.get(f"/user/{self.testuser_id}/edit",
                         follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 401)
            self.assertIn(
                '<p class="pt-5">You do not have permission to view this page </p>', html)

    def test_user_logout(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            resp = c.post(
                f'/user/{self.testuser_id}/logout', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                'Swolemate is a way for people to both share their own workouts', resp.get_data(as_text=True))

    def test_user_logout_unauthenticated(self):
        with self.client as c:
            resp = c.post(
                f'/user/{self.testuser_id}/logout', follow_redirects=True)

            self.assertEqual(resp.status_code, 401)
            self.assertIn(
                '<p class="pt-5">You do not have permission to view this page </p>', resp.get_data(as_text=True))

    def test_user_logout_unauthorized(self):
        u2 = User.signup(email='test2@test.com', password='testpass', username="testuser2",
                         first_name='Test', last_name='User2', image_url=None, cover_url=None)

        u2.id = 5678
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = u2.id
            resp = c.post(
                f'/user/{self.testuser_id}/logout', follow_redirects=True)

            self.assertEqual(resp.status_code, 401)
            self.assertIn(
                '<p class="pt-5">You do not have permission to view this page </p>', resp.get_data(as_text=True))
