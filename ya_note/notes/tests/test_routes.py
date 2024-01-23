from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Кама Пуля')
        cls.reader = User.objects.create(username='Мага Лезгин')
        cls.client_author = Client()
        cls.client_reader = Client()
        cls.client_author.force_login(cls.author)
        cls.client_reader.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заметка № 1',
            text='Текст к заметке',
            author=cls.author,
        )
        cls.note_slug = (cls.note.slug,)

    def test_pages_availability_for_anonymous_user(self):
        """
        Тест страницы: главная, авторизации, выхода, регистрации
        доступны анонимному пользователю.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for view_name in urls:
            with self.subTest(view_name=view_name):
                status_code = self.client.get(reverse(view_name)).status_code
                self.assertEqual(
                    status_code,
                    HTTPStatus.OK,
                )

    def test_pages_availability_for_different_users(self):
        """
        Тест страницы: просмотра одной, редактирования, удаления
        заметки доступны только её автору.
        """
        user_status = (
            (self.client_author, HTTPStatus.OK,),
            (self.client_reader, HTTPStatus.NOT_FOUND,),
        )
        urls = [
            ('notes:detail', self.note_slug,),
            ('notes:edit', self.note_slug,),
            ('notes:delete', self.note_slug,),
        ]
        for client, exptected_status_code in user_status:
            for view_name, args in urls:
                with self.subTest(
                        client=client,
                        view_name=view_name,
                        args=args):
                    url = reverse(view_name, args=args)
                    status_code = client.get(url).status_code
                    self.assertEqual(
                        status_code,
                        exptected_status_code,
                    )

    def test_pages_availability_for_auth_user(self):
        """
        Тест страницы: просмотра списка, создания
        заметки доступны авторизованному пользователю.
        """
        urls = [
            'notes:add',
            'notes:list',
            'notes:success',
        ]
        self.client.force_login(self.author)
        for view_name in urls:
            with self.subTest(view_name=view_name):
                status_code = self.client.get(reverse(view_name)).status_code
                self.assertEqual(
                    status_code,
                    HTTPStatus.OK,
                )

    def test_redirects(self):
        """
        Тест редиректа страницы: просмотра списка/одной, создания,
        изменения, удаления, для анонимного пользователю.
        """
        login_url = reverse('users:login')
        urls = [
            ('notes:add', None,),
            ('notes:list', None,),
            ('notes:success', None,),
            ('notes:edit', self.note_slug,),
            ('notes:detail', self.note_slug,),
            ('notes:delete', self.note_slug,),
        ]
        for view_name, args in urls:
            url = reverse(view_name, args=args)
            redirect_url = f'{login_url}?next={url}'
            with self.subTest(view_name=view_name):
                response = self.client.get(url)
                self.assertRedirects(
                    response=response,
                    expected_url=redirect_url,
                )
