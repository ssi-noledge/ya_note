from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from .base_testing_class import TestNotesBase
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNotesForms(TestNotesBase):

    def test_user_can_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.clients['author'].post(self.url_add_note, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author,
                         User.objects.get(username=self.author.username))

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.client.post(self.url_add_note, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.url_add_note}'
        self.assertRedirects(response, expected_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_not_unique_slug(self):
        form_data = self.form_data.copy()
        form_data['slug'] = self.note.slug
        notes_count_before = Note.objects.count()
        response = self.clients['author'].post(self.url_add_note, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_empty_slug(self):
        Note.objects.all().delete()
        form_data = self.form_data.copy()
        form_data.pop('slug')
        notes_count_before = Note.objects.count()
        response = self.clients['author'].post(self.url_add_note, data=form_data)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.clients['author'].post(self.url_edit_note, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.clients['author'].post(self.url_delete_note)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_user_cant_edit_others_note(self):
        original_title = self.other_note.title
        original_text = self.other_note.text
        original_slug = self.other_note.slug
        original_author = self.other_note.author
        response = self.clients['author'].post(
            self.not_edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        other_note_from_db = Note.objects.get(id=self.other_note.id)
        self.assertEqual(other_note_from_db.title, original_title)
        self.assertEqual(other_note_from_db.text, original_text)
        self.assertEqual(other_note_from_db.slug, original_slug)
        self.assertEqual(other_note_from_db.author, original_author)

    def test_user_cant_delete_others_note(self):
        notes_count_before = Note.objects.count()
        response = self.clients['author'].post(self.not_delete_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count_after, notes_count_before)
