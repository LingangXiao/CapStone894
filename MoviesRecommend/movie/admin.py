from django.contrib import admin

from movie.models import User, Movie, Genre, Movie_hot, Movie_rating, Movie_similarity

admin.site.site_title = "MovieRecommendationAdministration"
admin.site.site_header = "MovieRecommendationAdministration"
admin.site.index_title = "MovieRecommendation"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'password', 'email']

    search_fields = ['name', 'email']

    # list_filter = ['name']

    list_per_page = 12

    ordering = ['id']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):

    list_display = ['id', 'name']

    search_fields = ['name']

    # list_filter = ['name']

    list_per_page = 12

    ordering = ['id']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'imdb_id', 'time', 'release_time', 'intro', 'director', 'writers', 'actors', ]

    search_fields = ['name', 'intro', 'writers', 'actors']

    # list_filter = ['name', 'writers']

    list_per_page = 6

    ordering = ['id']


@admin.register(Movie_hot)
class Movie_hotAdmin(admin.ModelAdmin):

    list_display = ['id', 'movie', 'rating_number']

    search_fields = ['movie__name']

    # list_filter = ['name', 'writers']

    list_per_page = 6

    ordering = ['-rating_number']


@admin.register(Movie_rating)
class Movie_ratingAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'movie', 'score', 'comment']

    search_fields = ['user__name', 'movie__name']

    # list_filter = ['name', 'writers']

    list_per_page = 6

    ordering = ['-score']


@admin.register(Movie_similarity)
class Movie_similarityAdmin(admin.ModelAdmin):

    list_display = ['id', 'movie_source', 'movie_target', 'similarity']

    search_fields = ['movie_source__name', 'movie_source__name']

    # list_filter = ['name', 'writers']

    list_per_page = 6

    ordering = ['-similarity']
