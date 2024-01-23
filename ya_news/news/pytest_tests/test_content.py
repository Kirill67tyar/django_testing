import pytest
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, many_news):
    """
    Тест на то, что на главной странице
    количество выводмых новостей - 10.
    """
    response = client.get(HOME_URL)
    assert 'object_list' in response.context
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, many_news):
    """
    Тест на то, что даты на главной странице
    отсортированы от новых к старым.
    """
    response = client.get(HOME_URL)
    assert 'object_list' in response.context
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comment_order(client, news, detail_url, comments_with_other_dates):
    """
    Тест на то, что комментарии на странице одной новости
    выводятся от старых к новым.
    """
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_commets = [comment.created for comment in news.comment_set.all()]
    sorted_comments = sorted(all_commets)
    assert all_commets == sorted_comments


@pytest.mark.django_db
def test_authorized_client_has_form(admin_client, detail_url):
    """
    Тест, что у авторизованного пользователя есть форма
    для отправки комментария на странице отдельной новости.
    """
    response = admin_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    """Тест на то, что у анонимного пользователя нет формы."""
    response = client.get(detail_url)
    assert 'form' not in response.context
