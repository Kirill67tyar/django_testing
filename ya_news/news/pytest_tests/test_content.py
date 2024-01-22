import pytest
from http import HTTPStatus

from django.urls import reverse
from django.conf import settings


OK = HTTPStatus.OK
HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, many_news):
    """Тест на то, что количество новостей на странице - 10"""
    # action
    response = client.get(HOME_URL)
    # arrange
    news_count = response.context['object_list'].count()
    # assertion
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, many_news):
    """Тест на то, что даты на главной странице отсортированы правильно"""
    # action
    response = client.get(HOME_URL)
    # arrange
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    # assertion
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comment_order(client, news, detail_url, comments_with_other_dates):
    """Тест на то, что комментарии выводятся от старых к новым"""
    # action
    response = client.get(detail_url)
    # assertion
    assert 'news' in response.context
    # arrange
    news = response.context['news']
    comments = news.comment_set.all()
    # assertion
    assert comments[0].created < comments[1].created


@pytest.mark.django_db
def test_authorized_client_has_form(admin_client, detail_url):
    """Тест, что у авторизованного пользователя есть форма."""
    # action
    response = admin_client.get(detail_url)
    # assertion
    assert 'form' in response.context


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    """Тест на то, что у анонимного пользователя нет формы."""
    # action
    response = client.get(detail_url)
    # assertion
    assert 'form' not in response.context
