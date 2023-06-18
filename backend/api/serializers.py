from rest_framework import serializers

from users.models import User

from recipes.models import Recipe
from api.fields import Base64ImageField


class ShortRecipesSerializer(serializers.ModelSerializer):
    """Сериалайзер рецептов"""

    image = Base64ImageField(required=True, use_url=False)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = ShortRecipesSerializer(read_only=True, many=True)

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_subscribed",
            "recipes",
        )
        read_only_fields = ("id", "is_subscribed")
        extra_kwargs = {"password": {"write_only": True, "min_length": 4}}
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return user.follower.filter(author=obj).exists()

        return False

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
