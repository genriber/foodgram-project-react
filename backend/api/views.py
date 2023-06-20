from rest_framework import generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from api.permissions import IsOwnerOrReadOnly

from users.models import (
    User,
    Follow
)
from recipes.models import (
    Tag,
    Ingredient,
    # RecipeIngredient,
    Recipe,
    Favorite,
    ShoppingCart
)
from api.serializers import (
    ProfileSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipesSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    PasswordChangeSerializer,
    ObtainTokenSerializer,
    FollowSerializer
)


class UsersViewSet(
    generics.ListCreateAPIView,
    generics.RetrieveAPIView,
    viewsets.GenericViewSet,
):
    """Вьюсет профиля пользователя"""

    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.all()

    @action(
        detail=False,
        methods=["GET"],
        url_path="me",
        permission_classes=[IsAuthenticated],
        pagination_class=LimitOffsetPagination,
    )
    def me(self, request):
        return Response(
            self.serializer_class(
                self.request.user, context={"request": request}
            ).data
        )

    @action(
        detail=False,
        methods=["POST"],
        url_path="set_password",
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET"],
        url_path="subscriptions",
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        if self.paginate_queryset(queryset) is not None:
            serializer = ProfileSerializer(
                self.paginate_queryset(queryset),
                context={"request": request},
                many=True
            )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk):
        if request.method == "POST":
            author = get_object_or_404(User, pk=pk)
            serializer = FollowSerializer(
                data={
                    "author": author.pk,
                    "user": request.user.pk,
                },
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "DELETE":
            author = get_object_or_404(User, pk=pk)
            follow = get_object_or_404(
                Follow,
                author=author,
                user=request.user)
            if follow:
                follow.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ObtainTokenView(views.APIView):
    """Генерирет Acceess_token при получении email и password"""

    serializer_class = ObtainTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"token": serializer.validated_data.get("auth_token")},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteTokenView(views.APIView):
    """Генерирет Acceess_token при получении email и password"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.auth
        if token:
            token.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

# #####################RECIPES##########################


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
