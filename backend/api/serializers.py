from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers
from rest_framework.authtoken.models import Token

from users.models import (
    User,
    Follow
)

from recipes.models import (
    Tag,
    Ingredient,
    RecipeIngredient,
    Recipe,
    Favorite,
    ShoppingCart
)

from api.validators import UsernameValidator


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

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_subscribed",
        )
        extra_kwargs = {
            "password": {
                "required": True,
                "write_only": True,
                "min_length": 4},
            "email": {
                "required": True,
            },
            "username": {
                "required": True,
                "validators": [
                    UsernameValidator(),
                ],
            },
        }
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return user.follower.filter(author=obj).exists()

        return False

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ProfileWRecipesSerializer(serializers.ModelSerializer):
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

# #####################USER##########################


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150, required=True)
    current_password = serializers.CharField(max_length=150, required=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный пароль")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        new_password = validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user


class ObtainTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("password", "email")

    def validate(self, data):
        user = get_object_or_404(User, email=data.get("email", None))
        authenticate_kwargs = {
            "username": user.username,
            "password": data.get("password", None),
        }
        user = authenticate(**authenticate_kwargs)
        if user is None:
            raise exceptions.ValidationError("Неверный email или пароль!")
        token, created = Token.objects.get_or_create(user=user)
        return {
            "auth_token": str(token),
        }


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            "author",
        )

    def get_author(self, obj):
        return ProfileSerializer(
            instance=obj.author, read_only=True, context=self.context
        ).data

# #####################RECIPES##########################


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тега рецепта.
    """

    class Meta:
        fields = ("id", "name", "color", "slug", )
        read_only_fields = ("id", "slug", )
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов."""

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        read_only_fields = (
            "name",
            "measurement_unit",
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер промежуточной таблицы рецепта и ингредиентов."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipesSerializer(serializers.ModelSerializer):
    """Сериалайзер рецептов"""

    image = Base64ImageField(required=True, use_url=False)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingr.all"
    )
    author = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "ingredients",
            "is_in_shopping_cart",
            "is_favorited",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_author(self, obj):
        return ProfileSerializer(
            instance=obj.author, read_only=True, context=self.context
        ).data

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        if request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        else:
            return False

    def get_is_favorited(self, obj):
        request = self.context["request"]
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        else:
            return False


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = (
            "id",
            "user",
            "recipe",
        )


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = (
            "id",
            "user",
            "recipe",
        )
