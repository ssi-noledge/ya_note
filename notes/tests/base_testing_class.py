from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создание пользователей
        cls.author = User.objects.create_user(username='Лев Толстой', password='password')
        cls.not_author = User.objects.create_user(username='Алексей Толстой', password='password')

        # Создание заметок
        cls.note = Note.objects.create(
            title='Война и мир',
            text='... тысячу раз прав этот дуб,',
            author=cls.author,
            slug='author-slug',
        )
        cls.other_note = Note.objects.create(
            title='Упырь',
            text='Как ворон поймал летучую мышь...',
            author=cls.not_author,
            slug='not-author-slug',
        )
        cls.form_data = {
            'title': 'Анна Каренина',
            'text': 'Все счастливые семьи похожи друг на друга...',
            'slug': 'form-slug',
        }

        # Авторизация клиентов
        cls.clients = {
            'author': cls.client_class(),
            'not_author': cls.client_class(),
            'anonymous': cls.client_class(),
        }
        cls.clients['author'].login(username='Лев Толстой', password='password')
        cls.clients['not_author'].login(username='Алексей Толстой', password='password')

        # URL-адреса
        cls.url_list_notes = reverse('notes:list')
        cls.url_add_note = reverse('notes:add')
        cls.url_edit_note = reverse('notes:edit', args=(cls.note.slug,))
        cls.not_edit_url = reverse('notes:edit', args=(cls.other_note.slug,))
        cls.url_delete_note = reverse('notes:delete', args=(cls.note.slug,))
        cls.not_delete_url = reverse(
            'notes:delete', args=(cls.other_note.slug,)
        )
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')