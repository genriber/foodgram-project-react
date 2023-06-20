from django.contrib.auth.validators import UnicodeUsernameValidator
# from django.contrib.auth import get_user_model

from rest_framework.validators import ValidationError

from django.db.models import Q
from .serializers import serializers

from users.models import User


class UsernameValidator(UnicodeUsernameValidator):
    def __call__(self, value) -> None:
        if value == "me":
            raise ValidationError(f"Недопустимое имя: {value}")
        return super().__call__(value)

    User._meta.get_field('username').validators[1].limit_value = 150

    def check_unique_email_and_name(data):
        queryset = User.objects.filter(
            Q(email=data.get("email", ""))
            | Q(username=data.get("username"))
        )
        if queryset.exists():
            raise serializers.ValidationError(
                "Имя и email должны быть уникальными!"
            )
