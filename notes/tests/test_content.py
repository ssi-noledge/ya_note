# Отлично! Но всё ещё остаётся дублирование данных между классами.
# Корректнее выделить основные действия, одинаковые для всех:
# Создание и авторизация автора, читателя и создание записи,
# и вынести их в отдельный родительский класс тестов


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.not_author = User.objects.create(username='Алексей Толстой')
        cls.note = Note.objects.create(
            title='Война и мир',
            text='... тысячу раз прав этот дуб,',
            author=cls.author,
            slug='slug01',
        )
        cls.url_list_notes = reverse('notes:list')
        cls.url_add_note = reverse('notes:add')
        cls.url_edit_note = reverse('notes:edit', args=(cls.note.slug,))

    def setUp(self):
        # Create fresh client instances for each test
        self.author_client = self.client_class()
        self.not_author_client = self.client_class()
        # Log in the users
        self.author_client.force_login(self.author)
        self.not_author_client.force_login(self.not_author)


class TestNotesForms(TestNotesBase):
    def test_notes_list_misc_users(self):
        users_statuses = (
            (self.author_client, True),
            (self.not_author_client, False),
        )

        for client, note_in_list in users_statuses:
            with self.subTest(client=client):
                response = client.get(self.url_list_notes)
                notes = response.context['object_list']
                self.assertEqual((self.note in notes), note_in_list)


class TestNotesPages(TestNotesBase):
    def test_pages_have_form(self):
        urls = (self.url_add_note, self.url_edit_note)
        for url in urls:
            response = self.author_client.get(url)
            with self.subTest(url=url):
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
