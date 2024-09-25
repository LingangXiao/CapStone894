# Generated by Django 3.2.16 on 2023-11-26 06:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Genre',
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='电影名')),
                ('imdb_id', models.IntegerField()),
                ('time', models.CharField(blank=True, max_length=256)),
                ('release_time', models.CharField(blank=True, max_length=256)),
                ('intro', models.TextField(blank=True)),
                ('director', models.CharField(blank=True, max_length=256)),
                ('writers', models.CharField(blank=True, max_length=256)),
                ('actors', models.CharField(blank=True, max_length=512)),
                ('genre', models.ManyToManyField(to='movie.Genre')),
            ],
            options={
                'db_table': 'Movie',
            },
        ),
        migrations.CreateModel(
            name='Movie_rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('comment', models.TextField(blank=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie.movie')),
            ],
            options={
                'db_table': 'Movie_rating',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('password', models.CharField(max_length=256)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('rating_movies', models.ManyToManyField(through='movie.Movie_rating', to='movie.Movie')),
            ],
            options={
                'db_table': 'User',
            },
        ),
        migrations.CreateModel(
            name='Movie_similarity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity', models.FloatField()),
                ('movie_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movie_source', to='movie.movie')),
                ('movie_target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movie_target', to='movie.movie')),
            ],
            options={
                'ordering': ['-similarity'],
            },
        ),
        migrations.AddField(
            model_name='movie_rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie.user'),
        ),
        migrations.CreateModel(
            name='Movie_hot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_number', models.IntegerField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie.movie')),
            ],
            options={
                'db_table': 'Movie_hot',
                'ordering': ['-rating_number'],
            },
        ),
        migrations.AddField(
            model_name='movie',
            name='movie_similarity',
            field=models.ManyToManyField(through='movie.Movie_similarity', to='movie.Movie'),
        ),
    ]