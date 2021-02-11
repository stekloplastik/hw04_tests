from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import Post
from posts.models import Group, User


class PostFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user')
        self.user_client = Client()
        self.user_client.force_login(self.user)

        self.test_post = Post.objects.create(
            text='lalalala',
            author=self.user,
        )
        self.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='testgroup',
        )

    def test_add_new_post(self):
        """Форма добавляет новый пост и редиректит на главную страницу."""
        posts_count = Post.objects.count()
        form_data = {'text': 'tratatata', }
        response = self.user_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True)

        expected = posts_count + 1
        msg = 'Форма не добавляет новый пост'
        self.assertEqual(Post.objects.count(), expected, msg)

        response_form_data = response.context['page'].object_list[0]
        form_text = response_form_data.text
        form_author = response_form_data.author

        post = Post.objects.latest('id')

        self.assertEqual(form_text, post.text)
        self.assertEqual(form_author, post.author)

        expected = reverse('index')
        msg = 'Форма после добавления поста не редиректит на главную'
        self.assertRedirects(response, expected, msg_prefix=msg)

    def test_form_edit_post(self):
        """Валидная форма редактирует запись и производит редирект."""
        form_data = {
            'group': self.test_group.id,
            'text': 'modified-post',
        }
        response = self.user_client.post(
            reverse('post_edit', kwargs={'username': self.user,
                                         'post_id': self.test_post.id}),
            data=form_data,
            follow=True
        )
        self.test_post.refresh_from_db()
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={'username': self.user.username,
                                             'post_id': self.test_post.id}))
        self.assertEqual(self.test_post.text, form_data['text'])
