from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client
from posts.models import Group, Post


class PostsUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user1 = get_user_model().objects.create(username='TestUser1')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user1)
        self.post = Post.objects.create(
            text="test-text",
            author=self.user1,
            pub_date="01.01.2020",
            group=self.group
        )
        self.user2 = get_user_model().objects.create(username='TestUser2')
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user2)

    def test_url_exists_for_users(self):
        pages = [
            [reverse('index'), self.guest_client, 200],
            [reverse('index'), self.authorized_client_author, 200],
            [reverse('group', kwargs={'slug': 'test-slug'}), self.guest_client, 200],
            [reverse('group', kwargs={'slug': 'test-slug'}), self.authorized_client_author, 200],
            [reverse('new_post'), self.guest_client, 302],
            [reverse('new_post'), self.authorized_client_author, 200],
            [reverse('profile', kwargs={'username': 'TestUser1'}), self.guest_client, 200],
            [reverse('profile', kwargs={'username': 'TestUser1'}), self.authorized_client_author, 200],
            [reverse('post', kwargs={
                'username': 'TestUser1',
                'post_id': self.post.id
                }), self.guest_client, 200],
            [reverse('post', kwargs={
                'username': 'TestUser1',
                'post_id': self.post.id
                }), self.authorized_client_author, 200],
            [reverse('post_edit', kwargs={
                'username': 'TestUser1',
                'post_id': self.post.id
            }), self.guest_client, 302],
            [reverse('post_edit', kwargs={
                'username': 'TestUser1',
                'post_id': self.post.id
            }), self.authorized_client_author, 200],
            [reverse('post_edit', kwargs={
                'username': 'TestUser1',
                'post_id': self.post.id
            }), self.authorized_client_not_author, 302],
        ]
        for page, client, code in pages:
            with self.subTest():
                print(page)
                response = client.get(page)
                self.assertEqual(response.status_code, code)

    def test_post_edit_url_redirect(self):
        response = self.guest_client.get(
            reverse('post_edit', kwargs={
                'username': 'TestUser1',
                'post_id': self.post.id
            }), follow=True
            )
        expected_url = reverse('post', kwargs={
                'username': 'TestUser1',
                'post_id': self.post.id
            })
        self.assertRedirects(response, expected_url)

    def test_urls_uses_correct_template(self):
        templates_url_names = [
            [reverse('index'), 'index.html'],
            [reverse('group', kwargs={'slug': 'test-slug'}), 'group.html'],
            [reverse('new_post'), 'new.html'],
            [reverse('post_edit'), 'new_post.html']
        ]
        for url, template in templates_url_names:
            with self.subTest():
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)
