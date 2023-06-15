from django.db import models
from django.contrib.auth import get_user_model

from . validators import validate_year

User = get_user_model()  # временная модель для проверки


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
