import pytest
from http import HTTPStatus
from pytest_django.asserts import (
    assertRedirects,
    assertFormError,
)

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    """Тест: незалогиненный пользователь не может создавать комментарии."""
    # action
    client.post(detail_url, data=form_data)
    # arrange
    comment_count = Comment.objects.count()
    # assertion
    assert comment_count == 0


def test_user_can_create_comment(author_client,
                                 news,
                                 author,
                                 detail_url,
                                 form_data):
    """Тест: залогиненный пользователь может создавать комментарии."""
    # action
    response = author_client.post(detail_url, data=form_data)
    # arrange
    comment_count = Comment.objects.count()
    comment = Comment.objects.get()
    # assertion
    assert comment_count == 1
    assertRedirects(response, detail_url + '#comments')
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(author_client, detail_url, form_data):
    """Тест на валидацию сообщения на содержание плохих слов."""
    # arrange
    form_data['text'] = form_data['text'] + ' ' + BAD_WORDS[-1]
    # action
    response = author_client.post(detail_url, data=form_data)
    # assertion
    assertFormError(
        response=response,
        form='form',
        field='text',
        errors=WARNING,
    )
    comment_count = Comment.objects.count()
    assert comment_count == 0


def test_author_can_delete_comment(author_client, detail_url, delete_url):
    """Тест на то, что автор комментария может его удалить"""
    # action
    response = author_client.post(delete_url)
    # assertion
    assertRedirects(response, detail_url + '#comments')
    count_comments = Comment.objects.count()
    assert count_comments == 0


def test_user_cant_delete_comment_of_another_user(admin_client, delete_url):
    """
    Тест на то, что авторизованный пользователь
    не может удалить чужой комментарий.
    """
    # action
    status_code = admin_client.post(delete_url).status_code
    # assertion
    assert status_code == HTTPStatus.NOT_FOUND
    count_comments = Comment.objects.count()
    assert count_comments == 1


def test_author_can_edit_comment(author_client,
                                 comment,
                                 update_url,
                                 detail_url,
                                 form_data):
    """Тест на то, что автор комментария может его изменять."""
    # action
    response = author_client.post(
        update_url,
        data=form_data
    )
    # assertion
    assertRedirects(response, detail_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(admin_client,
                                                comment,
                                                update_url,
                                                form_data):
    """
    Тест на то, что авторизованный пользователь
    не может изменять чужой комментарий.
    """
    # arrange
    comment_text = comment.text
    # action
    status_code = admin_client.post(
        update_url,
        data=form_data
    ).status_code
    # assertion
    assert status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
