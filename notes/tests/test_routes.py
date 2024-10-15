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
        cls.note = Note.objects.create(title='Война и мир',
                                       text='Дубровский', author=cls.author)
        # Создаём двух пользователей с разными именами:
        # cls.author = User.objects.create(username='Лев Толстой')
        # cls.reader = User.objects.create(username='Читатель простой')
        # # От имени одного пользователя создаём комментарий к новости:
        # cls.comment = Comment.objects.create(
        #     news=cls.news,
        #     author=cls.author,
        #     text='Текст комментария'
        # )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:add', None),
            # ('notes:edit', (self.note.id,)),
            # ('notes:detail', (self.note.id,)),
            # ('notes:delete', (self.note.id,)),
            # ('notes:list', None),
            # ('notes:success', None),
            # ('users:login', None),
            # ('users:logout', None),
            # ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_availability_for_comment_edit_and_delete(self):
    #     users_statuses = (
    #         (self.author, HTTPStatus.OK),
    #         (self.reader, HTTPStatus.NOT_FOUND),
    #     )
    #     for user, status in users_statuses:
    #         # Логиним пользователя в клиенте:
    #         self.client.force_login(user)
    #         # Для каждой пары "пользователь - ожидаемый ответ"
    #         # перебираем имена тестируемых страниц:
    #         for name in ('news:edit', 'news:delete'):  
    #             with self.subTest(user=user, name=name):        
    #                 url = reverse(name, args=(self.comment.id,))
    #                 response = self.client.get(url)
    #                 self.assertEqual(response.status_code, status)
    
    # def test_redirect_for_anonymous_client(self):
    #     # Сохраняем адрес страницы логина:
    #     login_url = reverse('users:login')
    #     # В цикле перебираем имена страниц, с которых ожидаем редирект:
    #     for name in ('news:edit', 'news:delete'):
    #         with self.subTest(name=name):
    #             # Получаем адрес страницы редактирования или удаления комментария:
    #             url = reverse(name, args=(self.comment.id,))
    #             # Получаем ожидаемый адрес страницы логина, 
    #             # на который будет перенаправлен пользователь.
    #             # Учитываем, что в адресе будет параметр next, в котором передаётся
    #             # адрес страницы, с которой пользователь был переадресован.
    #             redirect_url = f'{login_url}?next={url}'
    #             response = self.client.get(url)
    #             # Проверяем, что редирект приведёт именно на указанную ссылку.
    #             self.assertRedirects(response, redirect_url) 