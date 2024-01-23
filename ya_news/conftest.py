import pytest

from datetime import datetime, timedelta
from django.test import Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура создания автора комментария."""
    return django_user_model.objects.create(username='Кама Пуля')


@pytest.fixture
def author_client(author):
    """Фикстура логина автора комментария."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
@pytest.mark.django_db
def news():
    """Фикстура создания новости."""
    return News.objects.create(
        title='Заголовок к статье № 1',
        text='Текст к статье № 1',
    )


@pytest.fixture
def comment(author, news):
    """Фикстура создания комментария."""
    return Comment.objects.create(
        text='Коммент к статье № 1',
        author=author,
        news=news,
    )


@pytest.fixture
def id_for_url(news):
    """Фикстура id для страницы новости."""
    return (news.pk,)


@pytest.fixture
@pytest.mark.django_db
def many_news():
    """Фикстура создания новостей с разными датами."""
    today = datetime.today()
    return News.objects.bulk_create(News(
        title=f'Заголовок № {i}',
        text=f'Текст к статье № {i}',
        date=today - timedelta(days=i),
    ) for i in range(1, settings.NEWS_COUNT_ON_HOME_PAGE + 2))


@pytest.fixture
@pytest.mark.django_db
def comments_with_other_dates(news, author):
    """Фикстура создания комментариев с разными датами."""
    now = timezone.now()
    for i in range(1, 11):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст к комментарию № {i}',
        )
        comment.created = now + timedelta(days=i)
        comment.save()


@pytest.fixture
def detail_url(news):
    """Фикстура урла для одной новости."""
    return reverse(
        'news:detail',
        kwargs={'pk': news.pk, }
    )


@pytest.fixture
def delete_url(comment):
    """Фикстура урла удаления комментария."""
    return reverse(
        'news:delete',
        kwargs={'pk': comment.pk, }
    )


@pytest.fixture
def update_url(comment):
    """Фикстура урла изменения комментария."""
    return reverse(
        'news:edit',
        kwargs={'pk': comment.pk, }
    )


@pytest.fixture
def form_data():
    """Фикстура данных для формы."""
    return {
        'text': 'Комментарий 1'
    }
