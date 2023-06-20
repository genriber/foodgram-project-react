from django.urls import include, path
from rest_framework import routers

from api.views import (
    DeleteTokenView,
    ObtainTokenView,
    UsersViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet
)

app_name = "api"


router = routers.DefaultRouter()
router.register(r"users", UsersViewSet, basename="users")
router.register(r"users/(?P<id>\d+)/subscribe",
                UsersViewSet,
                basename="subscribe"
                )
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"recipes/(?P<id>\d+)/shopping_cart",
                RecipeViewSet,
                basename="shopping_cart"
                )
router.register(r"recipes/download_shopping_cart",
                RecipeViewSet,
                basename="download_shopping_cart"
                )
router.register(r"ingredients", IngredientViewSet, basename="ingredient")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/login/", ObtainTokenView.as_view(), name="login"),
    path("auth/token/logout/", DeleteTokenView.as_view(), name="logout"),
]
