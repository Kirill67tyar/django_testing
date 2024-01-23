from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.parametrize(
    argnames=('view_name', 'args',),
    argvalues=(
        ('news:home', None,),
        ('news:detail', pytest.lazy_fixture('id_for_url'),),
        ('users:login', None,),
        ('users:logout', None,),
        ('users:signup', None,),
    ),
)
@pytest.mark.django_db
def test_page_availability(client, view_name, args):
    """
    Тест на доступность главной, одной новости, логина, логаута, регистрации
    страниц для всех пользователей.
    """
    response = client.get(reverse(view_name, args=args))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    argnames='parametrized_client, expected_status',
    argvalues=(
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND,),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK,),
    )
)
@pytest.mark.parametrize(
    argnames='view_name',
    argvalues=(
        'news:edit',
        'news:delete',
    )
)
def test_availability_for_comment_edit_and_delete(view_name,
                                                  parametrized_client,
                                                  expected_status,
                                                  comment):
    """
    Тест на доступность страниц
    редактирования/удаления комментария для его автора.
    """
    url = reverse(view_name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    argnames='view_name',
    argvalues=(
        'news:delete',
        'news:edit',
    ),
)
def test_redirect_for_anonymous_client(client, comment, view_name):
    """
    Тест на не доступность страниц редактирования/удаления
    комментария анонимного пользователя.
    """
    login_url = reverse('users:login')
    url = reverse(view_name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
