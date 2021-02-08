from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Напишите,чем вы хотите поделиться с миром'
        )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Укажите дату'
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name='Автор',
        help_text='Укажите автора'
        )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name='Сообщество',
        help_text='Укажите сообщество'
        )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название сообщества',
        help_text='Придумайте название сообщества'
        )
    slug = models.SlugField(
        unique=True,
        verbose_name='Метка',
        help_text='Метка вашего сообщества'
        )
    description = models.TextField(
        verbose_name='Описание сообщества',
        help_text='Опишите для кого или для чего ваше сообщество'
        )

    def __str__(self):
        return self.title
