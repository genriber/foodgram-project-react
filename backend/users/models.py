from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError


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
