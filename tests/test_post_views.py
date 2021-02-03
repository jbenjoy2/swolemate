"""Test View Functions of Post pages"""
import os
from unittest import TestCase
from models import db, connect_db, Post, User, Likes, Muscle, Equipment
os.environ['DATABASE_URL'] = 'postgresql:///swolemate-test'
from app import app, CURRENT_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class UserViewTestCase(TestCase):
    """test views for posts"""

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
        p1 = Post(id=5678, title='testpost1', details='this is a test post',
                  is_private=False, user_id=self.testuser_id, timestamp=None)

        db.session.add(p1)
        db.session.commit()

        p1 = Post.query.get(5678)
        self.testuser.likes.append(p1)
        self.testuser_likes = self.testuser.likes
        db.session.commit()
        self.p1 = p1
        self.p1_id = self.p1.id
        db.session.commit()

        biceps = Muscle(name='biceps', body_part='arms')
        triceps = Muscle(name='triceps', body_part='arms')
        deltoids = Muscle(name='deltoids', body_part='shoulders')

        db.session.add_all([biceps, triceps, deltoids])
        db.session.commit()

        barbell = Equipment(name='barbell')
        kettlebell = Equipment(name='kettlebell')
        dumbbells = Equipment(name='dumbbells')

        db.session.add_all([barbell, kettlebell, dumbbells])
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_show_new_post_form(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            resp = c.get(f'/user/{self.testuser_id}/posts/new')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display1 text-center">',
                          resp.get_data(as_text=True))

    def test_show_add_post_unauthenticated(self):
        with self.client as c:
            resp = c.get(f'/user/{self.testuser_id}/posts/new')
            self.assertEqual(resp.status_code, 401)
            self.assertIn('<p class="pt-5">You do not have permission to view this page </p>',
                          resp.get_data(as_text=True))

    def test_show_add_post_unauthorized(self):
        u2 = User.signup(email='test2@test.com', password='testpass', username="testuser2",
                         first_name='Test', last_name='User2', image_url=None, cover_url=None)
        u2.id = 5678
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = u2.id

            resp = c.get(f'/user/{self.testuser_id}/posts/new')
            self.assertEqual(resp.status_code, 401)
            self.assertIn('<p class="pt-5">You do not have permission to view this page </p>',
                          resp.get_data(as_text=True))

    def test_add_post(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id
            data = {
                "title": 'Testpost',
                "details": 'This is a test post',
                "muscles": [1, 2, 3],
                "equipment": [1, 2, 3],
                "is_private": True
            }
            resp = c.post(f'/user/{self.testuser_id}/posts/new',
                          data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                "<p class='text-light'>(CLICK FOR FULL DETAILS)</p>", resp.get_data(as_text=True))

    def test_see_post_details(self):
        p1 = Post(id=1234, title="testpost",
                  details='this is a testpost', timestamp=None, is_private=False, user_id=self.testuser_id)

        db.session.add(p1)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            post = Post.query.get(1234)
            resp = c.get(f'/posts/{post.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(post.details, resp.get_data(as_text=True))

    def test_see_post_unauthenticated(self):
        p1 = Post(id=1234, title="testpost",
                  details='this is a testpost', timestamp=None, is_private=False, user_id=self.testuser_id)

        db.session.add(p1)
        db.session.commit()

        with self.client as c:

            post = Post.query.get(1234)
            resp = c.get(f'/posts/{post.id}')

            self.assertEqual(resp.status_code, 401)
            self.assertIn('<p class="pt-5">You do not have permission to view this page </p>',
                          resp.get_data(as_text=True))

    def test_see_invalid_post(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            resp = c.get('/posts/12345689')
            self.assertEqual(resp.status_code, 404)

    def test_add_like(self):
        p1 = Post(id=1234, title="testpost",
                  details='this is a testpost', timestamp=None, is_private=False, user_id=self.testuser_id)
        db.session.add(p1)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            p = Post.query.get(1234)
            resp = c.post(f'/posts/{p.id}/like', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<i class="fas fa-star liked"></i>',
                          resp.get_data(as_text=True))

    def test_remove_like(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            resp = c.post('/posts/5678/like', follow_redirects=True)
            user = User.query.get(1234)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fas fa-star liked"></i>',
                             resp.get_data(as_text=True))
            self.assertEqual(len(user.likes), 0)

    def test_add_like_unauthenticated(self):
        p1 = Post(id=1234, title="testpost",
                  details='this is a testpost', timestamp=None, is_private=False, user_id=self.testuser_id)
        db.session.add(p1)
        db.session.commit()

        with self.client as c:

            p = Post.query.get(1234)
            resp = c.post(f'/posts/{p.id}/like', follow_redirects=True)

            self.assertEqual(resp.status_code, 401)
            self.assertIn('<p class="pt-5">You do not have permission to view this page </p>',
                          resp.get_data(as_text=True))

    def test_show_liked_posts(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            resp = c.get(f'/user/{self.testuser_id}/likes')
            user = User.query.get(1234)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<i class="fas fa-star liked"></i>',
                          resp.get_data(as_text=True))
            self.assertNotEqual(len(user.likes), 0)

    def test_show_liked_post_unauthenticated(self):
        with self.client as c:

            resp = c.get(f'/user/{self.testuser_id}/likes')

            self.assertEqual(resp.status_code, 401)
            self.assertIn('<p class="pt-5">You do not have permission to view this page </p>',
                          resp.get_data(as_text=True))

    def test_show_edit_page(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            resp = c.get('/posts/5678/edit')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Workout:', resp.get_data(as_text=True))

    def test_edit_post(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id
            data = {
                "title": 'Testpost234',
                "details": 'This is a test post still',
                "muscles": [1, 2],
                "equipment": [1, 2],
                "is_private": False
            }
            resp = c.post(f'/posts/5678/edit',
                          data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                "id='edit-post'>Edit</button>", resp.get_data(as_text=True))

    def test_successful_delete(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            resp = c.post(f'posts/5678/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Post Deleted!', resp.get_data(as_text=True))

    def test_invalid_post_delete(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser_id

            resp = c.post(f'posts/356789/delete')

            self.assertEqual(resp.status_code, 404)

    def test_noauth_delete(self):
        with self.client as c:

            resp = c.post(f'posts/5678/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 401)
            self.assertIn(
                '<p class="pt-5">You do not have permission to view this page </p>', resp.get_data(as_text=True))
