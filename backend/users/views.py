from rest_framework import generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.serializers import (
    ProfileSerializer,
)
from users.models import (
    User,
    Follow
)
from users.serializers import (
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
