from django.db import models
from django.db.models import Avg


# 分类信息表
class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name="Genre")

    class Meta:
        db_table = 'Genre'
        verbose_name = 'Genre'
        verbose_name_plural = 'Genre'

    def __str__(self):
        return self.name


# 电影信息表
class Movie(models.Model):
    name = models.CharField(max_length=256, verbose_name="Movie name")
    imdb_id = models.IntegerField(verbose_name="imdb_id")
    time = models.CharField(max_length=256, blank=True, verbose_name="Time")
    genre = models.ManyToManyField(Genre, verbose_name="Genre")
    release_time = models.CharField(max_length=256, blank=True, verbose_name="Release Date")
    intro = models.TextField(blank=True, verbose_name="Intro")
    director = models.CharField(max_length=256, blank=True, verbose_name="Director")
    writers = models.CharField(max_length=256, blank=True, verbose_name="Writer")
    actors = models.CharField(max_length=512, blank=True, verbose_name="Actor")
    # 电影和电影之间的相似度,A和B的相似度与B和A的相似度是一致的，所以symmetrical设置为True
    movie_similarity = models.ManyToManyField("self", through="Movie_similarity", symmetrical=False,
                                              verbose_name="Similar movies")

    class Meta:
        db_table = 'Movie'
        verbose_name = 'Movie'
        verbose_name_plural = 'Movie'

    def __str__(self):
        return self.name

    # 获取平均分的方法
    def get_score(self):
        result_dct = self.movie_rating_set.aggregate(Avg('score'))  # 格式 {'score__avg': 3.125}
        try:
            result = round(result_dct['score__avg'], 1)  # 只保留一位小数
        except TypeError:
            return 0
        else:
            return result

    # 获取用户的打分情况
    def get_user_score(self, user):
        return self.movie_rating_set.filter(user=user).values('score')

    # 整数平均分
    def get_score_int_range(self):
        return range(int(self.get_score()))

    # 获取分类列表
    def get_genre(self):
        genre_dct = self.genre.all().values('name')
        genre_lst = []
        for dct in genre_dct.values():
            genre_lst.append(dct['name'])
        return genre_lst

    # 获取电影的相识度
    def get_similarity(self, k=5):
        # 默认获取5部最相似的电影的id
        similarity_movies = self.movie_similarity.all()[:k]
        return similarity_movies


# 电影相似度
class Movie_similarity(models.Model):
    movie_source = models.ForeignKey(Movie, related_name='movie_source', on_delete=models.CASCADE, verbose_name="来源电影")
    movie_target = models.ForeignKey(Movie, related_name='movie_target', on_delete=models.CASCADE, verbose_name="目标电影")
    similarity = models.FloatField(verbose_name="Similarity")

    class Meta:
        # 按照相似度降序排序
        verbose_name = 'Movie Similarity'
        verbose_name_plural = 'Movie Similarity'


# 用户信息表
class User(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="User")
    password = models.CharField(max_length=256, verbose_name="Password")
    email = models.EmailField(unique=True, verbose_name="Email")
    rating_movies = models.ManyToManyField(Movie, through="Movie_rating")

    def __str__(self):
        return "<USER:( name: {:},password: {:},email: {:} )>".format(self.name, self.password, self.email)

    class Meta:
        db_table = 'User'
        verbose_name = 'User Info'
        verbose_name_plural = 'User Info'


# 电影评分信息表
class Movie_rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, verbose_name="User")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, unique=False, verbose_name="Movie")
    score = models.FloatField(verbose_name="score")
    comment = models.TextField(blank=True, verbose_name="comment")

    class Meta:
        db_table = 'Movie_rating'
        verbose_name = 'Movie_rating'
        verbose_name_plural = 'Movie_rating'


# 最热门的一百部电影
class Movie_hot(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Movie")
    rating_number = models.IntegerField(verbose_name="rating_number")

    class Meta:
        db_table = 'Movie_hot'
        verbose_name = 'Popular_Movie'
        verbose_name_plural = 'Popular_Movie'

# python manage.py makemigrations
# python manage.py migrate
