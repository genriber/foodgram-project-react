from rest_framework import serializers

from recipes.models import (
    Tag,
    Ingredient,
    RecipeIngredient,
    Recipe,
    ShoppingCart,
    Favorite
)
from api.serializers import ProfileSerializer
from api.fields import Base64ImageField


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

    def get_is_favorited(self, obj):
        request = self.context["request"]
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()


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
