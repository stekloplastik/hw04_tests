import os
import tempfile
import shutil
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post, User


class ViewPageContextTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.mkdir(f'{settings.BASE_DIR}/tmp/')
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=f'{settings.BASE_DIR}/tmp/')

    def setUp(self):
        self.guest_client = Client()

        self.user_one = User.objects.create_user(username='user_one')
        self.user_one_client = Client()
        self.user_one_client.force_login(self.user_one)

        self.user_two = User.objects.create_user(username='user_two')
        self.user_two_client = Client()
        self.user_two_client.force_login(self.user_two)

        self.test_group = Group.objects.create(
            title='Test Group',
            slug='group',
            description='Description',
        )

        self.test_second_group = Group.objects.create(
            title='Test Second Group',
            slug='second-group',
            description='Description',
        )

        self.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                          b'\x01\x00\x80\x00\x00\x00\x00\x00'
                          b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                          b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                          b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                          b'\x0A\x00\x3B')

        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif',
        )

        self.test_post = Post.objects.create(
            text='Test post',
            author=self.user_one,
            group=self.test_group,
            image=self.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(f'{settings.BASE_DIR}/tmp/', ignore_errors=True)
        super().tearDownClass()

    def test_url_templates(self):
        """Соответствие вызываемых шаблонов."""
        user = self.user_one
        post_id = self.test_post.id
        urls = {
            reverse('index'): 'index.html',
            reverse('new_post'): 'new.html',
            reverse('group', args=['group']): 'group.html',
            reverse('group', args=['group']): 'group.html',
            reverse('post_edit', args=[user, post_id]): 'new_post.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for url, expected in urls.items():
            with self.subTest():
                response = self.user_one_client.get(url)
                msg = f'{url} не использует шаблон {expected}'
                self.assertTemplateUsed(response, expected, msg)

    def test_index_context(self):
        """На главной странице существует пост и правильный контекст."""
        response = self.user_one_client.get(reverse('index'))
        expected = self.test_post
        msg = 'На главной странице неправильный context или нет нового поста'
        self.assertEqual(response.context['page'][0], expected, msg)

    def test_group_context(self):
        """На странице группы правильный контекст."""
        url = reverse('group', args=['group'])
        response = self.user_one_client.get(url)
        expected = self.test_group
        msg = 'На странице группы неправильный context'
        self.assertEqual(response.context['group'], expected, msg)

    def test_new_post_context(self):
        """На странице создания поста правильный контекст."""
        fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }

        response = self.user_one_client.get(reverse('new_post'))
        form = response.context['form']

        for field, expected in fields.items():
            with self.subTest(field=field):
                msg = 'На странице создания поста неправильный context'
                self.assertIsInstance(form.fields[field], expected, msg)

    def test_post_edit_context(self):
        """На странице редактирования поста правильный контекст."""
        url = reverse('post_edit', args=[self.user_one, self.test_post.id])
        response = self.user_one_client.get(url)
        form = response.context['form']

        context = {
            'post': self.test_post,
            'is_edit': True,
        }

        for value, expected in context.items():
            with self.subTest(value=value):
                msg = f'{value} контекста не равно {expected}'
                self.assertEqual(response.context[value], expected, msg)

        fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for field, expected in fields.items():
            with self.subTest(field=field):
                msg = 'На странице редактирования поста неправильный context'
                self.assertIsInstance(form.fields[field], expected, msg)

    def test_profile_context(self):
        """На странице автора правильный контекст."""
        user = self.user_one
        url = reverse('profile', args=[user])
        response = self.user_one_client.get(url)

        context = {
            'author': user,
            # 'posts': self.test_post,
        }

        for value, expected in context.items():
            with self.subTest(value=value):
                msg = f'{value} контекста не равно {expected}'
                self.assertEqual(response.context[value], expected, msg)

    def test_post_view_context(self):
        """На странице поста правильный контекст."""
        url = reverse('post', args=[self.user_one, self.test_post.id])
        response = self.user_one_client.get(url)

        context = {
            'post': self.test_post,
            'author': self.user_one,
        }

        for value, expected in context.items():
            with self.subTest(value=value):
                msg = f'{value} контекста не равно {expected}'
                self.assertEqual(response.context[value], expected, msg)

    def test_group_post(self):
        """На странице группы отображается новый пост."""
        response = self.user_one_client.get(
            reverse('group', args=['group']))
        expected = self.test_post
        msg = 'На странице группы не отображается новый пост'
        self.assertEqual(response.context['page'][0], expected, msg)

    def test_another_group_post(self):
        """На странице другой группы не отображается новый пост."""
        path = reverse('group', args=['second-group'])
        response = self.user_one_client.get(path)
        response = response.context['page'].object_list.count()
        expected = 0
        msg = 'На странице другой группы не должен отображаться новый пост'
        self.assertEqual(response, expected, msg)


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Test',
            description='Тестовая группа'
        )
        posts = [Post(author=cls.user, group=cls.group, text=str(i))
                 for i in range(13)]

        Post.objects.bulk_create(posts)

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.

        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
