# news/tests/test_content.py
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка', text='Просто текст.',
            author=cls.author, slug='test_slug2'
        )
        cls.detail_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_anonymous_client_has_no_access(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
