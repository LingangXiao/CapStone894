from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import Genre, Movie, User, Movie_rating, Movie_similarity, Movie_hot
import xmlrunner
import unittest
import coverage
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .forms import RegisterForm, LoginForm, CommentForm
import os


def run_tests_with_coverage():
    cov = coverage.Coverage(
        branch=True,
        source=['your_app_name'],
        omit=[
            '*/tests/*',
            '*/migrations/*',
            '*/admin.py',
            '*/apps.py',
            '*/__init__.py',
            '*/views.py',  # Temporarily ignore views.py
        ]
    )
    cov.start()
    test_runner = xmlrunner.XMLTestRunner(output='test-reports')
    test_program = unittest.main(module=None, exit=False, testRunner=test_runner)
    cov.stop()
    cov.save()
    cov.html_report(directory='coverage_reports')
    print("\nCoverage Report:")
    cov.report()


class GenreModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Action")

    def test_genre_creation(self):
        self.assertEqual(self.genre.name, "Action")
        self.assertTrue(isinstance(self.genre, Genre))
        self.assertEqual(str(self.genre), "Action")


class MovieModelTest(TestCase):
    def setUp(self):
        # Create test genres
        self.action = Genre.objects.create(name="Action")
        self.drama = Genre.objects.create(name="Drama")

        # Create test movie
        self.movie = Movie.objects.create(
            name="Test Movie",
            imdb_id=12345,
            time="120 min",
            release_time="2024",
            intro="Test movie introduction",
            director="Test Director",
            writers="Test Writer",
            actors="Actor1, Actor2"
        )
        self.movie.genre.add(self.action, self.drama)

        # Create another movie for similarity testing
        self.similar_movie = Movie.objects.create(
            name="Similar Movie",
            imdb_id=12346,
            time="110 min"
        )

        # Create similarity relationship
        Movie_similarity.objects.create(
            movie_source=self.movie,
            movie_target=self.similar_movie,
            similarity=0.8
        )

    def test_movie_creation(self):
        self.assertEqual(self.movie.name, "Test Movie")
        self.assertEqual(self.movie.imdb_id, 12345)
        self.assertEqual(str(self.movie), "Test Movie")

    def test_movie_genre_relationship(self):
        genres = self.movie.get_genre()
        self.assertEqual(len(genres), 2)
        self.assertIn("Action", genres)
        self.assertIn("Drama", genres)

    def test_movie_similarity(self):
        similar_movies = self.movie.get_similarity(k=1)
        self.assertEqual(similar_movies.count(), 1)
        self.assertEqual(similar_movies[0], self.similar_movie)

    def test_movie_rating(self):
        # Test with no ratings
        self.assertEqual(self.movie.get_score(), 0)

        # Add a rating and test again
        user = User.objects.create(
            name="testuser",
            password="testpass",
            email="test@test.com"
        )
        Movie_rating.objects.create(
            user=user,
            movie=self.movie,
            score=4.5,
            comment="Good movie"
        )
        self.assertEqual(self.movie.get_score(), 4.5)


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="testuser",
            password="testpass",
            email="test@test.com"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.name, "testuser")
        self.assertEqual(self.user.email, "test@test.com")

    def test_unique_username(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(
                name="testuser",  # Duplicate username
                password="testpass2",
                email="test2@test.com"
            )

    def test_unique_email(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(
                name="testuser2",
                password="testpass2",
                email="test@test.com"  # Duplicate email
            )


class MovieRatingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="testuser",
            password="testpass",
            email="test@test.com"
        )
        self.movie = Movie.objects.create(
            name="Test Movie",
            imdb_id=12345
        )
        self.rating = Movie_rating.objects.create(
            user=self.user,
            movie=self.movie,
            score=4.5,
            comment="Great movie!"
        )

    def test_rating_creation(self):
        self.assertEqual(self.rating.score, 4.5)
        self.assertEqual(self.rating.comment, "Great movie!")

    def test_user_movie_rating_relationship(self):
        user_score = self.movie.get_user_score(self.user)
        self.assertEqual(user_score[0]['score'], 4.5)


class MovieHotTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            name="Popular Movie",
            imdb_id=12345
        )
        self.hot_movie = Movie_hot.objects.create(
            movie=self.movie,
            rating_number=1000
        )

    def test_hot_movie_creation(self):
        self.assertEqual(self.hot_movie.rating_number, 1000)
        self.assertEqual(self.hot_movie.movie.name, "Popular Movie")


class ViewsTestCase(TestCase):
    def setUp(self):
        # Create test client
        self.client = Client()

        # Create test user
        self.user = User.objects.create(
            name="testuser",
            password="testpass",
            email="test@test.com"
        )

        # Create test movie data
        self.genre = Genre.objects.create(name="Action")
        self.movie = Movie.objects.create(
            name="Test Movie",
            imdb_id=123,
            time="120 min",
            release_time="2024",
            intro="Test movie introduction",
            director="Test Director"
        )
        self.movie.genre.add(self.genre)

        # Create test rating
        self.rating = Movie_rating.objects.create(
            user=self.user,
            movie=self.movie,
            score=4.5,
            comment="Great movie!"
        )

    def test_index_view(self):
        response = self.client.get(reverse('movie:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/index.html')
        self.assertIn('movies', response.context)
        self.assertIn('paginator', response.context)

    def test_popular_movie_view(self):
        # Create hot movie data
        Movie_hot.objects.create(
            movie=self.movie,
            rating_number=1000
        )
        response = self.client.get(reverse('movie:hot'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/hot.html')
        self.assertIn('movies', response.context)

    def test_tag_view(self):
        # Test without genre parameter
        response = self.client.get(reverse('movie:tag'))
        self.assertEqual(response.status_code, 200)

        # Test with genre parameter
        response = self.client.get(f"{reverse('movie:tag')}?genre=Action")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/tag.html')
        self.assertIn('movies', response.context)

    def test_search_view(self):
        response = self.client.get(f"{reverse('movie:search')}?keyword=Test")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/search.html')
        self.assertIn('movies', response.context)
        self.assertIn('keyword', response.context)

    def test_register_view(self):
        # Test GET request
        response = self.client.get(reverse('movie:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/register.html')

        # Test POST request - valid data
        valid_data = {
            'name': 'newuser',
            'password': 'newpass',
            'password_repeat': 'newpass',
            'email': 'new@test.com'
        }
        response = self.client.post(reverse('movie:register'), valid_data)
        self.assertTrue(User.objects.filter(name='newuser').exists())

        # Test POST request - invalid data (duplicate username)
        invalid_data = {
            'name': 'testuser',
            'password': 'testpass',
            'password_repeat': 'testpass',
            'email': 'another@test.com'
        }
        response = self.client.post(reverse('movie:register'), invalid_data)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already exists' in str(m) for m in messages))

    def test_login_view(self):
        # Test GET request
        response = self.client.get(reverse('movie:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/login.html')

        # Test POST request - valid login
        valid_data = {
            'name': 'testuser',
            'password': 'testpass',
            'remember': True
        }
        response = self.client.post(reverse('movie:login'), valid_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Test POST request - invalid login
        invalid_data = {
            'name': 'testuser',
            'password': 'wrongpass',
            'remember': False
        }
        response = self.client.post(reverse('movie:login'), invalid_data)
        messages = list(get_messages(response.wsgi_request))

    def test_logout_view(self):
        # Login first
        self.client.post(reverse('movie:login'), {
            'name': 'testuser',
            'password': 'testpass'
        })
        # Test logout
        response = self.client.get(reverse('movie:logout'))
        self.assertRedirects(response, reverse('movie:index'))

    def test_movie_detail_view(self):
        # Test without login
        response = self.client.get(reverse('movie:detail', args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/detail.html')
        self.assertFalse(response.context['login'])

        # Test with login
        self.client.post(reverse('movie:login'), {
            'name': 'testuser',
            'password': 'testpass'
        })
        response = self.client.get(reverse('movie:detail', args=[self.movie.id]))
        self.assertTrue(response.context['login'])
        self.assertEqual(response.context['score'], 4.5)

        # Test rating submission
        rating_data = {
            'score': 4.0,
            'comment': 'Updated comment'
        }
        response = self.client.post(reverse('movie:detail', args=[self.movie.id]), rating_data)
        self.assertRedirects(response, reverse('movie:detail', args=[self.movie.id]))
        updated_rating = Movie_rating.objects.get(user=self.user, movie=self.movie)
        self.assertEqual(updated_rating.score, 4.0)

    def test_rating_history_view(self):
        # Login first
        self.client.post(reverse('movie:login'), {
            'name': 'testuser',
            'password': 'testpass'
        })
        response = self.client.get(reverse('movie:history', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/history.html')
        self.assertIn('ratings', response.context)

    def test_recommend_movie_view(self):
        # Login first
        self.client.post(reverse('movie:login'), {
            'name': 'testuser',
            'password': 'testpass'
        })

        # Create test data for recommendations
        other_user = User.objects.create(name="other", password="pass", email="other@test.com")
        other_movie = Movie.objects.create(name="Other Movie", imdb_id=456)
        Movie_rating.objects.create(user=other_user, movie=self.movie, score=4.0)
        Movie_rating.objects.create(user=other_user, movie=other_movie, score=5.0)

        response = self.client.get(reverse('movie:recommend'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/recommend.html')
        self.assertIn('movies', response.context)

    def test_pagination_data(self):
        # Create enough movies to test pagination
        for i in range(20):
            Movie.objects.create(
                name=f"Movie {i}",
                imdb_id=i + 1000
            )

        response = self.client.get(reverse('movie:index'))
        self.assertIn('left_pages', response.context)
        self.assertIn('right_pages', response.context)
        self.assertIn('current_page', response.context)
        self.assertIn('left_has_more', response.context)
        self.assertIn('right_has_more', response.context)


if __name__ == '__main__':
    run_tests_with_coverage()
