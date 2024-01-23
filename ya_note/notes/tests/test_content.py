from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestContent(TestCase):

    NOTES_LIST_URL = reverse('notes:list')

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

    def test_notes_list_for_different_users(self):
        """
        Тест, заметка доступна только её автору,
        и она есть в конексте, в списке object_list.
        """
        users = [
            (self.client_author, self.assertIn),
            (self.client_reader, self.assertNotIn),
        ]
        for client, assertion in users:
            with self.subTest(client=client, assertion=assertion):
                response = client.get(self.NOTES_LIST_URL)
                object_list = response.context['object_list']
                assertion(self.note, object_list)

    def test_pages_contains_form(self):
        """
        Тест, на странице создания и редактирования заметки,
        передаются формы для заметки.
        """
        urls = [
            ('notes:add', None,),
            ('notes:edit', self.note_slug,),
        ]
        for view_name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(view_name=view_name, args=args):
                url = reverse(view_name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
