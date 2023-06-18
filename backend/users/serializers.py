from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers
from rest_framework.authtoken.models import Token

from users.models import User, Follow
from api.serializers import ProfileSerializer


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
    # user = serializers.SerializerMethodField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            # "id",
            "author",
        )

    def get_author(self, obj):
        return ProfileSerializer(
            instance=obj.author, read_only=True, context=self.context
        ).data
