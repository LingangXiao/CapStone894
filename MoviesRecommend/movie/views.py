import os.path
import time

from django.contrib import messages
from django.db.models import Max, Count
from django.shortcuts import render, redirect, reverse
from django.views.generic import View, ListView, DetailView

from .forms import RegisterForm, LoginForm, CommentForm
from .models import User, Movie, Movie_rating, Movie_hot

BASE = os.path.dirname(os.path.abspath(__file__))


# 首页视图
class IndexView(ListView):
    model = Movie
    template_name = 'movie/index.html'
    paginate_by = 15
    context_object_name = 'movies'
    ordering = 'imdb_id'
    page_kwarg = 'p'

    # 返回前1000部电影
    def get_queryset(self):
        return Movie.objects.filter(imdb_id__lte=1000)

    # 获取上下文数据
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(IndexView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')  # 分页器对象
        page_obj = context.get('page_obj')  # 当前页对象
        pagination_data = self.get_pagination_data(paginator, page_obj)  # 获取分页数据
        context.update(pagination_data)  # 返回更新后的上下文数据
        return context

    # 获取分页数据
    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


# 热门电影视图
class PopularMovieView(ListView):
    model = Movie_hot
    template_name = 'movie/hot.html'
    paginate_by = 15
    context_object_name = 'movies'
    page_kwarg = 'p'

    def get_queryset(self):
        # 初始化 计算评分人数最多的100部电影，并保存到数据库中，（不建议每次都运行）
        movies = Movie.objects.annotate(nums=Count('movie_rating__score')).order_by('-nums')[:100]
        for movie in movies:
            record = Movie_hot(movie=movie, rating_number=movie.nums)
            record.save()

        hot_movies = Movie_hot.objects.all().values("movie_id")
        movies = Movie.objects.filter(id__in=hot_movies).annotate(nums=Max('movie_hot__rating_number')).order_by(
            '-nums')
        return movies

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PopularMovieView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


# 电影分类视图
class TagView(ListView):
    model = Movie
    template_name = 'movie/tag.html'
    paginate_by = 15
    context_object_name = 'movies'
    page_kwarg = 'p'

    # 获取数据
    def get_queryset(self):
        # 未选择分类
        if 'genre' not in self.request.GET.dict().keys() or self.request.GET.dict()['genre'] == "":
            movies = Movie.objects.all()
            return movies[100:200]
        # 有分类选择
        else:
            movies = Movie.objects.filter(genre__name=self.request.GET.dict()['genre'])
            print(movies)
            return movies[:100]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TagView, self).get_context_data(*kwargs)
        if 'genre' in self.request.GET.dict().keys():
            genre = self.request.GET.dict()['genre']
            context.update({'genre': genre})
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


# 搜索电影视图
class SearchView(ListView):
    model = Movie
    template_name = 'movie/search.html'
    paginate_by = 15
    context_object_name = 'movies'
    page_kwarg = 'p'

    def get_queryset(self):
        movies = Movie.objects.filter(name__icontains=self.request.GET.dict()['keyword'])
        return movies

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        context.update({'keyword': self.request.GET.dict()['keyword']})
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


# 注册视图
class RegisterView(View):
    def get(self, request):
        return render(request, 'movie/register.html')

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('movie:index'))
        else:
            # 表单验证失败，重定向到注册页面
            errors = form.get_errors()
            for error in errors:
                messages.info(request, error)
            print(form.errors.get_json_data())
            return redirect(reverse('movie:register'))


# 登录视图
class LoginView(View):
    def get(self, request):
        return render(request, 'movie/login.html')

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            pwd = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            user = User.objects.filter(name=name, password=pwd).first()
            if user:
                if remember:
                    # 设置为None，则表示使用全局的过期时间
                    request.session.set_expiry(None)
                else:
                    # 立即过期
                    request.session.set_expiry(0)
                # 登录成功，在session 存储当前用户的id，作为标识
                request.session['user_id'] = user.id
                return redirect(reverse('movie:index'))

            else:
                messages.info(request, '用户名或者密码错误!')
                return redirect(reverse('movie:login'))
        else:
            errors = form.get_errors()
            for error in errors:
                messages.info(request, error)
            return redirect(reverse('movie:login'))


# 登出，立即销毁session停止会话
def UserLogout(request):
    request.session.set_expiry(-1)
    return redirect(reverse('movie:index'))


# 电影详情视图
class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movie/detail.html'
    # 上下文对象的名称
    context_object_name = 'movie'

    # 重写获取上下文方法，增加评分参数
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 判断是否登录用
        login = True
        try:
            user_id = self.request.session['user_id']
        except KeyError as e:
            login = False  # 未登录

        # 获得电影的pk（这里pk就是id）
        pk = self.kwargs['pk']
        movie = Movie.objects.get(pk=pk)

        if login:
            # 已经登录，获取当前用户的历史评分数据
            user = User.objects.get(pk=user_id)

            rating = Movie_rating.objects.filter(user=user, movie=movie).first()
            # 默认值
            score = 0
            comment = ''
            if rating:
                score = rating.score
                comment = rating.comment
            context.update({'score': score, 'comment': comment})

        similarity_movies = movie.get_similarity()
        # 获取与当前电影最相似的电影
        context.update({'similarity_movies': similarity_movies})
        # 判断是否登录，没有登录则不显示评分页面
        context.update({'login': login})

        return context

    # 接受评分表单,pk是当前电影的数据库主键id
    def post(self, request, pk):
        form = CommentForm(request.POST)
        if form.is_valid():
            # 获取分数和评论
            score = form.cleaned_data.get('score')
            comment = form.cleaned_data.get('comment')
            # 获取用户和电影
            user_id = request.session['user_id']
            user = User.objects.get(pk=user_id)
            movie = Movie.objects.get(pk=pk)

            # 更新一条记录
            rating = Movie_rating.objects.filter(user=user, movie=movie).first()
            if rating:
                # 如果存在则更新
                # print(rating)
                rating.score = score
                rating.comment = comment
                rating.save()
            else:
                # 如果不存在则添加
                rating = Movie_rating(user=user, movie=movie, score=score, comment=comment)
                rating.save()
            messages.info(request, "评论成功!")
        else:
            # 表单没有验证通过
            messages.info(request, "评分不能为空!")
        return redirect(reverse('movie:detail', args=(pk,)))


# 历史评分视图
class RatingHistoryView(DetailView):
    model = User
    template_name = 'movie/history.html'
    # 上下文对象的名称
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        # 这里要增加的对象：当前用户打过分的电影历史
        context = super().get_context_data(**kwargs)
        user_id = self.request.session['user_id']
        user = User.objects.get(pk=user_id)
        # 获取ratings即可
        ratings = Movie_rating.objects.filter(user=user).order_by('-score')
        context.update({'ratings': ratings})
        return context


# 删除打分评论数据
def delete_recode(request, pk):
    movie = Movie.objects.get(pk=pk)
    user_id = request.session['user_id']
    user = User.objects.get(pk=user_id)
    rating = Movie_rating.objects.get(user=user, movie=movie)
    rating.delete()
    messages.info(request, f"删除 {movie.name} 评分记录成功！")
    # 跳转回评分历史
    return redirect(reverse('movie:history', args=(user_id,)))


# 推荐电影视图
class RecommendMovieView(ListView):
    model = Movie
    template_name = 'movie/recommend.html'
    paginate_by = 15
    context_object_name = 'movies'
    ordering = 'movie_rating__score'
    page_kwarg = 'p'

    def __init__(self):
        super().__init__()
        # 最相似的20个用户
        self.K = 20
        # 推荐出10本书
        self.N = 10
        # 存放当前用户评分过的电影querySet
        self.cur_user_movie_qs = None

    # 获取用户相似度
    def get_user_sim(self):
        # 用户相似度字典，格式为{ user_id1:val , user_id2:val , ... }
        user_sim_dct = dict()
        '''获取用户之间的相似度,存放在user_sim_dct中'''
        # 获取当前用户
        cur_user_id = self.request.session['user_id']
        cur_user = User.objects.get(pk=cur_user_id)
        # 获取其它用户
        other_users = User.objects.exclude(pk=cur_user_id)  # 除了当前用户外的所有用户

        # 当前用户评分过的电影
        self.cur_user_movie_qs = Movie.objects.filter(user=cur_user)

        # 计算当前用户与其他用户共同评分过的电影交集数
        for user in other_users:
            # 记录感兴趣的数量
            user_sim_dct[user.id] = len(Movie.objects.filter(user=user) & self.cur_user_movie_qs)

        # 按照key排序value，返回K个最相近的用户（共同评分过的电影交集数更多）
        print("user similarity calculated!")
        # 格式 [ (user, value), (user, value), ... ]
        return sorted(user_sim_dct.items(), key=lambda x: -x[1])[:self.K]

    # 获取推荐电影（按照相似用户总得分排序）
    def get_recommend_movie(self, user_lst):
        # 电影兴趣值字典，{ movie:value, movie:value , ...}
        movie_val_dct = dict()
        # 用户，相似度
        for user, _ in user_lst:
            # 获取相似用户评分过的电影，并且不在前用户的评分列表中的，再加上score字段，方便计算兴趣值
            movie_set = Movie.objects.filter(user=user).exclude(id__in=self.cur_user_movie_qs).annotate(
                score=Max('movie_rating__score'))
            for movie in movie_set:
                movie_val_dct.setdefault(movie, 0)
                # 累计用户的评分
                movie_val_dct[movie] += movie.score
        return sorted(movie_val_dct.items(), key=lambda x: -x[1])[:self.N]

    # 获取数据
    def get_queryset(self):
        s = time.time()
        # 获得最相似的K个用户列表
        user_lst = self.get_user_sim()
        # 获得推荐电影的id
        movie_lst = self.get_recommend_movie(user_lst)
        # print(movie_lst)
        result_lst = []
        for movie, _ in movie_lst:
            result_lst.append(movie)
        e = time.time()
        print(f"算法推荐用时:{e - s}秒！")
        return result_lst

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RecommendMovieView, self).get_context_data(*kwargs)
        print(context)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }
