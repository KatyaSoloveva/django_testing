from datetime import timedelta

import pytest
from django.urls import reverse
from django.test.client import Client
from django.conf import settings
from django.utils.timezone import now

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    new = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return new


@pytest.fixture
def all_news():
    return News.objects.bulk_create(
        News(title=f'Новость {index}', text='Просто текст.',
             date=now() - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def comments(author, news):
    for index in range(10):
        comment = Comment.objects.create(news=news, author=author,
                                         text=f'Текст {index}')
        comment.created = now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def pk_for_args(news):
    return (news.pk,)


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def form_data(news, author):
    return {'news': news,
            'author': author,
            'text': 'Новый текст комментария'}
