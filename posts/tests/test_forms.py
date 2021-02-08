from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных
        User = get_user_model()
        User.objects.create(
            id=1,
            email='testemail@mail.ru',
            first_name='Test',
            last_name='User'
        )
        cls.user = User.objects.get(id=1)
        Group.objects.create(
            id=1,
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание тестовой группы'
        )
        cls.group = Group.objects.get(id=1)
        Post.objects.create(
            id=1,
            text='Тестовый текст',
            author=User.objects.get(id=1),
            group=Group.objects.get(id=1)
        )

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = get_user_model().objects.create_user(
            username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новый пост"""
        # Подсчитаем количество постов
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Тестовый текст 2',
            'group': 1
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(text='Тестовый текст 2').exists())
