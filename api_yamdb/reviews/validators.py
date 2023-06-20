from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Проверка валидности указываемого года выпуска"""
    if value > timezone.now().year:
        raise ValidationError(
            ('Некорректный год выпуска'),
            params={'value': value},
        )
