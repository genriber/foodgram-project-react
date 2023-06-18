from django.contrib import admin

from .models import (Tag, Ingredient, RecipeIngredient,
                     Recipe, ShoppingCart, Favorite
                     )


class RecipeIngredientInline(admin.TabularInline):
    """
    Инлайн для отображения ManyToMany поля ingredient
    в админ-модели RecipeAdminPanel.
    """

    model = RecipeIngredient
    extra = 1


class TagAdminPanel(admin.ModelAdmin):
    """
    Админ-модель для модели Tag.
    """

    list_display = ("id", "name", "color", "slug", )
    search_fields = ("name", "slug", )
    list_filter = ("name", "slug", )
    empty_value_display = "-пусто-"


class IngredientAdminPanel(admin.ModelAdmin):
    """
    Админ-модель для модели Ingredient.
    """

    list_display = ("id", "name", "measurement_unit", )
    search_fields = ("name", "measurement_unit", )
    list_filter = ("name", "measurement_unit", )
    empty_value_display = "-пусто-"


class RecipeAdminPanel(admin.ModelAdmin):
    """
    Админ-модель для модели Ingredient.
    """
    inlines = [RecipeIngredientInline]
    list_display = ("id",
                    "image", "name", "text",
                    "cooking_time", "author",
                    )
    filter_horizontal = ("tags", )
    search_fields = ("name", )
    list_filter = ("name", )
    empty_value_display = "-пусто-"


class ShoppingCartAdminPanel(admin.ModelAdmin):
    """
    Админ-модель для модели ShoppingCart.
    """

    list_display = ("id", "user", "recipe", )
    search_fields = ("user", "recipe", )
    list_filter = ("user", )
    empty_value_display = "-пусто-"


class FavoriteAdminPanel(admin.ModelAdmin):
    """
    Админ-модель для модели Favorite.
    """

    list_display = ("id", "user", "recipe", )
    search_fields = ("user", "recipe", )
    list_filter = ("user", )
    empty_value_display = "-пусто-"


admin.site.register(Tag, TagAdminPanel)
admin.site.register(Ingredient, IngredientAdminPanel)
admin.site.register(Recipe, RecipeAdminPanel)
admin.site.register(ShoppingCart, ShoppingCartAdminPanel)
admin.site.register(Favorite, FavoriteAdminPanel)
