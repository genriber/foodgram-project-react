from django.core import validators
from django.db import models

from users.models import User


class Tag(models.Model):
    """
    Модель тэгов рецепта.
    """

    name = models.CharField("название тега", max_length=150, )
    color = models.CharField("цветовой код", max_length=7, )
    slug = models.SlugField("слаг тега", max_length=150, unique=True, )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return f"Тег {self.name}"


class Ingredient(models.Model):
    """
    Модель ингредиентов для рецепта.
    """

    name = models.CharField("название ингредиента", max_length=250, )
    measurement_unit = models.CharField("единицы измерения", max_length=250, )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        return f"Ингредиент {self.name}"


class Recipe(models.Model):
    """
    Модель рецептов.
    """

    ingredients = models.ManyToManyField(Ingredient,
                                         through="RecipeIngredient"
                                         )
    tags = models.ManyToManyField(Tag)
    image = models.ImageField(
        "картинка",
        upload_to="media/recipes/",
        blank=True
    )
    name = models.CharField("название рецепта", max_length=250, )
    text = models.TextField("описание рецепта", )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    cooking_time = models.IntegerField(
        "время готовки в минутах",
        validators=[
            validators.MinValueValidator(
                1, message="Мин. время приготовления 1 минута"
            ),
        ],
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["name"]

    def __str__(self):
        return f"Рецепт {self.name} под авторством {self.author}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingr",
        verbose_name="рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingr",
        verbose_name="ингредиент",
    )
    amount = models.IntegerField(
        default=1,
        validators=(
            validators.MinValueValidator(
                1,
                message="Мин. количество ингридиентов 1"),
        ),
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Ингридиенты рецепта"
        verbose_name_plural = "Ингридиенты рецептов"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique ingredient"
            )
        ]

    def __str__(self):
        return f"{self.amount}"


class Favorite(models.Model):
    """
    Модель избранных рецептов.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite_pair"
            )
        ]

        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ["user"]

    def __str__(self):
        return f"Избранные рецепты {self.user}"


class ShoppingCart(models.Model):
    """
    Модель списка покупок.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shoppingcart",
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shoppingcart",
        verbose_name="рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shoppingcart_pair"
            )
        ]

        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ["user"]

    def __str__(self):
        return f"Список покупок {self.user}"
