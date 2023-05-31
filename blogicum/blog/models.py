from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class PublishedBaseModel(models.Model):
    """Абстрактная модель. Добавляет флаг is_published и created_at."""
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        blank=False,
        help_text='Снимите галочку, '
                  'чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
        blank=False
    )

    class Meta:
        abstract = True


class Category(PublishedBaseModel):
    """Тематическая категория"""
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
        blank=False
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=False
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        unique=True,
        blank=False,
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, '
                  'цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedBaseModel):
    """Географическая метка"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название места',
        blank=False
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedBaseModel):
    """Публикация"""
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
        blank=False
    )
    text = models.TextField(
        verbose_name='Текст',
        blank=False
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        blank=False,
        help_text='Если установить дату и время в будущем '
                  '— можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор публикации',
        blank=False
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='location',
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='category',
        verbose_name='Категория',
        blank=False
    )
    image = models.ImageField(
        'Фото',
        upload_to='posts_images',
        blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = (
            '-pub_date',
        )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # С помощью функции reverse() возвращаем URL объекта.
        return reverse('blog:profile', kwargs={'username': self.author})


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
