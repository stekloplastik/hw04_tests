from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post


class ViewPageContextTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user_model().objects.create_user(username="TestUser")
        Group.objects.create(
            title="Название группы",
            slug="test-slug",
            description="тестовый текст"
        )
        cls.group = Group.objects.get(id=1)
        Post.objects.create(
            text="Тестовый текст",
            author=user,
            group=cls.group
        )

        cls.post = Post.objects.get(id=1)

    def setUp(self):
        self.guest_user = get_user_model().objects.create_user(username="User")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.guest_user)

    def test_index_page_correct_context(self):
        response = self.authorized_client.get(reverse("index"))
        post_title = response.context.get("page")[0].text
        post_author = response.context.get("page")[0].author.username
        post_group = response.context.get("page")[0].group.title

        self.assertEqual(post_title, "Тестовый текст")
        self.assertEqual(post_author, "TestUser")
        self.assertEqual(post_group, "Название группы")

    def test_group_posts_page_correct_context(self):
        response = self.authorized_client.get(reverse(
            "group",
            kwargs={"slug": "test-slug"}))
        group_title = response.context.get("group").title
        group_slug = response.context.get("group").slug
        group_description = response.context.get("group").description
        post_title = response.context.get("page")[0].text
        post_author = response.context.get("page")[0].author.username
        post_group = response.context.get("page")[0].group.title

        self.assertEqual(group_title, "Название группы")
        self.assertEqual(group_slug, "test-slug")
        self.assertEqual(group_description, "тестовый текст")
        self.assertEqual(post_title, "Тестовый текст")
        self.assertEqual(post_author, "TestUser")
        self.assertEqual(post_group, "Название группы")

    def test_form_page_correct_context(self):
        field_forms = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField
        }
        response = self.authorized_client.get(reverse("new_post"))
        for value, expected, in field_forms.items():
            form_field = response.context.get("form").fields.get(value)
            self.assertIsInstance(form_field, expected,
                                  "form.field не того класса.")

    def test_index_page_create_post_correct_context(self):
        new_post = Post.objects.create(
            text="Текст для поста",
            author=self.guest_user,
            group=ViewPageContextTest.group)
        response = self.authorized_client.get(reverse("index"))
        self.assertContains(response, new_post)

    def test_group_posts_page_create_post_correct_context(self):
        new_post = Post.objects.create(
            text="Текст для поста",
            author=self.guest_user,
            group=ViewPageContextTest.group)
        response = self.authorized_client.get(reverse("group", kwargs={"slug": "test-slug"}))
        self.assertContains(response, new_post)


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
