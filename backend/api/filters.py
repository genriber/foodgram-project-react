from django_filters import rest_framework as filters


class IngredientNameFilter(filters.SearchFilter):
    """
    Кастомный фильтр для Ingredient.
    Осуществляет поиск по полю Name.
    """

    search_param = "name"
