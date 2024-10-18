from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс комментария.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.not_author = User.objects.create(username='Алексей Толстой')
        cls.note = Note.objects.create(title='Война и мир',
                                       text='... тысячу раз прав этот дуб,',
                                       author=cls.author,
                                       slug='slug01',
                                       )
        cls.client_author = cls.client_class()
        cls.client_author.force_login(cls.author)
        cls.client_not_author = cls.client_class()
        cls.client_not_author.force_login(cls.not_author)

    def test_pages_availability_anonym(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_author(self):
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client_not_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_misc_users(self):
        clients_statuses = (
            (self.client_not_author, HTTPStatus.NOT_FOUND),
            (self.client_author, HTTPStatus.OK),
        )
        for client, status in clients_statuses:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(client=client, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_anonym(self):
        login_url = reverse('users:login')
        urls_args = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        for name, args in urls_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
