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
        cls.note = Note.objects.create(title='Война и мир',
                                       text='Да, он прав, тысячу раз прав этот дуб,',
                                       author=cls.author,
                                       slug='slug01',
                                       )
        cls.url_list_notes = reverse('notes:list')
        cls.url_add_note = reverse('notes:add')
        cls.url_edit_note = reverse('notes:edit', args=(cls.note.slug,))
        cls.clients = {
            'author': cls.client_class(),
            'not_author': cls.client_class(),
        }
        cls.clients['author'].force_login(cls.author)
        cls.clients['not_author'].force_login(cls.not_author)


class TestNotesForms(TestNotesBase):

    def test_notes_list_misc_users(self):
        users_statuses = (
            ('author', True),
            ('not_author', False),
        )

        for user_key, note_in_list in users_statuses:
            with self.subTest(user=user_key):
                response = self.clients[user_key].get(self.url_list_notes)
                notes = response.context['object_list']
                self.assertEqual((self.note in notes), note_in_list)


class TestNotesPages(TestNotesBase):

    def test_pages_has_form(self):
        urls = (self.url_add_note, self.url_edit_note)
        for url in urls:
            response = self.clients['author'].get(url)
            with self.subTest(url=url):
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
