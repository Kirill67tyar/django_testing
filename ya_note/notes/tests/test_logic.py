from http import HTTPStatus

from pytils.translit import slugify
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestLogic(TestCase):

    NOTE_TITLE = 'Заметка № 1'
    NOTE_TEXT = 'Текст к заметке'
    NOTE_SLUG = 'zametka-1'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Кама Пуля')
        cls.reader = User.objects.create(username='Мага Лезгин')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Новый текст',
            'slug': 'new-note',
        }
        cls.client_author = Client()
        cls.client_reader = Client()
        cls.client_author.force_login(cls.author)
        cls.client_reader.force_login(cls.reader)
        cls.success_url = reverse('notes:success')
        cls.create_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_user_can_create_note(self):
        """
        Тест на то, что зарегистрированный пользователь может создать заметку,
        его средиректит на страницу 'success'
        и все поля заметки что он создаст - правильные.
        """
        Note.objects.all().delete()
        response = self.client_author.post(
            self.create_url, data=self.form_data)
        note = Note.objects.get(slug=self.form_data['slug'])
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """
        Тест на то, что анонимный пользователь не может создать заметку,
        его средиректит на страницу логина.
        """
        quantity_notes = Note.objects.count()
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.create_url}'
        response = self.client.post(self.create_url, data=self.form_data)
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), quantity_notes)

    def test_not_unique_slug(self):
        """Тест на то, что нельзя создать одинаковый слаг для заметки."""
        quantity_notes = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.client_author.post(
            self.create_url, data=self.form_data)
        self.assertFormError(
            response=response,
            form='form',
            field='slug',
            errors=self.note.slug + WARNING
        )
        self.assertEqual(Note.objects.count(), quantity_notes)

    def test_empty_slug(self):
        """
        Тест на то, что слаг для заметки может создаться автоматически
        и он правильный.
        """
        Note.objects.all().delete()
        del self.form_data['slug']
        response = self.client_author.post(
            self.create_url, data=self.form_data)
        note = Note.objects.order_by('pk').last()
        expexted_slug = slugify(note.title)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(note.slug, expexted_slug)

    def test_author_can_edit_note(self):
        """Тест успешного обновления заметки её автором."""
        response = self.client_author.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertRedirects(response, self.success_url)
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Тест невозможности обновления заметки не её автором."""
        status_code = self.client_reader.post(
            self.edit_url, data=self.form_data).status_code
        self.note.refresh_from_db()
        self.assertEqual(status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        """Тест, что автор может удалить свою заметку."""
        quantity_notes = Note.objects.count() - 1
        response = self.client_author.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), quantity_notes)

    def test_other_user_cant_delete_note(self):
        """Тест, что не автор заметки не может её удалить."""
        quantity_notes = Note.objects.count()
        status_code = self.client_reader.post(self.delete_url).status_code
        self.assertEqual(status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), quantity_notes)
