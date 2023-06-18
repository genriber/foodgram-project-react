from django.contrib import admin

from .models import User, Follow


class UserAdminPanel(admin.ModelAdmin):
    """
    Админ-модель для модели User.
    """

    list_display = ("id", "username", "email", "first_name", "last_name", )
    search_fields = ("username", )
    list_filter = ("username", )
    empty_value_display = "-пусто-"


class FollowAdminPanel(admin.ModelAdmin):
    """
    Админ-модель для модели Follow.
    """

    list_display = ("id", "user", "author", )
    search_fields = ("user", "author", )
    list_filter = ("user", "author", )
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdminPanel)
admin.site.register(Follow, FollowAdminPanel)
