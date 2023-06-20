from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    """
    Кастомный класс модели User.
    """

    REQUIRED_FIELDS = [
        "email",
        "first_name",
        "last_name",
        "password"
    ]

    email = models.EmailField(
        'email',
        max_length=254,
        unique=True
    )
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(), )
    )
    first_name = models.CharField(
        'имя',
        max_length=150
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150,
    )
    password = models.CharField(
        'пароль',
        max_length=150,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "username"],
                name="unique_email_username_pair",
            ),
        ]
    verbose_name = "Пользователь"
    verbose_name_plural = "Пользователи"
    ordering = ["username", "email"]

    def __str__(self):
        return f"Пользователь {self.username}"

    def clean(self):
        if self.username == "me":
            raise ValidationError(f"Недопустимое имя: {self.username}")

        if len(self.username) <= 150:
            raise ValidationError(f"Слишком длинный юзернейм: {self.username}")

        return super().clean()


class Follow(models.Model):
    """
    Модель подписки юзера на автора рецептов.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"],
                name="unique_follow_pair",
            ),
        ]
        ordering = ["-author"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def clean(self):
        if self.author == self.user:
            raise ValidationError("Нельзя подписываться на самого себя!")

    def __str__(self):
        return f"Подписка {self.user} на {self.author}"
