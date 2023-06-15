from django.contrib.auth import get_user_model #<<<---Убрать после добавления модели User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from . validators import validate_year


User = get_user_model()#<<<---Убрать после добавления модели User
LENGTH_TEXT:int = 15


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Категория",
    )
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Жанр",
    )
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Произведение",
        help_text="Проверьте название произведения",
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Год выпуска",
        validators=[validate_year],
    )
    description = models.TextField(verbose_name="Описание")
    genre = models.ManyToManyField(
        Genre,
        related_name="titles",
        blank=True,
        verbose_name="Жанр",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        blank=True,
        null=True,
        verbose_name="Категория",
    )

    class Meta:
        ordering = ["-year"]

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Жанры произведения'
        verbose_name_plural = 'Жанры произведений'

    def __str__(self):
        return f'{self.title} принадлежит жанру {self.genre}'


class Review(models.Model):
    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Aвтор'
    )
    score = models.PositiveIntegerField(
        verbose_name='Oценка',
        validators=[
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
            MaxValueValidator(10, 'Оценка не может быть выше 10'),
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            ),
        )

    def __str__(self):
        return self.text[:LENGTH_TEXT]


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Aвтор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:LENGTH_TEXT]