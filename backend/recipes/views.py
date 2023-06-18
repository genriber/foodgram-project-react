from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend


from recipes.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipesSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)
from recipes.models import (
    Tag, Ingredient,
    Recipe, Favorite,
    ShoppingCart
)
from api.permissions import IsOwnerOrReadOnly


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(
    generics.ListAPIView,
    generics.RetrieveAPIView,
    viewsets.GenericViewSet,
):
    """Вьюсет для модели Ingredient"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    search_fields = ("^name",)

    def get_queryset(self):
        return Recipe.objects.all()


class RecipeViewSet(
    generics.ListAPIView,
    generics.ListCreateAPIView,
    generics.RetrieveAPIView,
    viewsets.GenericViewSet,
):
    """Вьюсет для модели Recipe"""

    serializer_class = RecipesSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return Recipe.objects.all()

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        permission_classes=[IsOwnerOrReadOnly],
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = FavoriteSerializer(
                data={
                    "recipe": recipe.pk,
                    "user": request.user.pk,
                },
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "DELETE":
            recipe = get_object_or_404(Recipe, pk=pk)
            fav = get_object_or_404(
                Favorite,
                recipe=recipe,
                user=request.user)
            if fav:
                fav.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = ShoppingCartSerializer(
                data={
                    "recipe": recipe.pk,
                    "user": request.user.pk,
                },
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "DELETE":
            recipe = get_object_or_404(Recipe, pk=pk)
            shoppingcart = get_object_or_404(
                ShoppingCart,
                recipe=recipe,
                user=request.user)
            if shoppingcart:
                shoppingcart.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET"],
        url_path="download_shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request, format=None):

        filename = f"foodgram__{request.user.username}_shopping_cart.txt"

        shopping_cart = ShoppingCart.objects.filter(user=request.user).all()
        # shopping_cart_serializer = ShoppingCartSerializer(shopping_cart)

        response = HttpResponse(
            shopping_cart,
            content_type="text/plain; charset=UTF-8"
        )
        response["Content-Disposition"] = (
            f"attachment;  filename={0}'.{filename}"
        )

        return response
