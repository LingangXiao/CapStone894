from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Movie, Genre, User, Movie_rating, Movie_hot, Movie_similarity


class GenreModelTest(TestCase):
    def test_genre_creation(self):
        genre = Genre.objects.create(name="Action")
        self.assertEqual(str(genre), "Action")


class MovieModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Drama")
        self.movie = Movie.objects.create(
            name="Test Movie",
            imdb_id=12345,
            time="120 min",
            release_time="2023-01-01",
            intro="A test movie",
            director="Test Director",
            writers="Test Writer",
            actors="Test Actor"
        )
        self.movie.genre.add(self.genre)
        self.user = User.objects.create(name="testuser", password="testpass", email="test@example.com")

    def test_movie_creation(self):
        self.assertEqual(str(self.movie), "Test Movie")

    def test_get_score(self):
        Movie_rating.objects.create(user=self.user, movie=self.movie, score=4.5)
        Movie_rating.objects.create(user=self.user, movie=self.movie, score=3.5)
        self.assertEqual(self.movie.get_score(), 4.0)

    def test_get_genre(self):
        self.assertEqual(self.movie.get_genre(), ["Drama"])

    def test_get_similarity(self):
        similar_movie = Movie.objects.create(name="Similar Movie", imdb_id=67890)
        Movie_similarity.objects.create(movie_source=self.movie, movie_target=similar_movie, similarity=0.9)
        self.assertEqual(list(self.movie.get_similarity(k=1)), [similar_movie])


class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create(name="testuser", password="testpass", email="test@example.com")
        self.assertEqual(str(user), "<USER:( name: testuser,password: testpass,email: test@example.com )>")


class MovieRatingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(name="testuser", password="testpass", email="test@example.com")
        self.movie = Movie.objects.create(name="Test Movie", imdb_id=12345)

    def test_movie_rating_creation(self):
        rating = Movie_rating.objects.create(user=self.user, movie=self.movie, score=4.5, comment="Great movie!")
        self.assertEqual(rating.score, 4.5)
        self.assertEqual(rating.comment, "Great movie!")


class MovieHotModelTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(name="Hot Movie", imdb_id=12345)

    def test_movie_hot_creation(self):
        hot_movie = Movie_hot.objects.create(movie=self.movie, rating_number=1000)
        self.assertEqual(hot_movie.rating_number, 1000)
        self.assertEqual(hot_movie.movie.name, "Hot Movie")
