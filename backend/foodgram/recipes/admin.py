from django.contrib import admin

from . import models


# @admin.register(models.User)
# class UserAdmin(admin.ModelAdmin):
#     # list_display = ('pk', 'email', 'first_name', 'last_name', 'bio', 'role')
#     # search_fields = ('first_name', 'last_name')
#     # list_filter = ('role',)
#     # list_editable = ('role',)
#     empty_value_display = '-пусто-'


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    # list_display = ('pk', 'email', 'first_name', 'last_name', 'bio', 'role')
    # search_fields = ('first_name', 'last_name')
    # list_filter = ('role',)
    # list_editable = ('role',)
    empty_value_display = '-пусто-'


@admin.register(models.Ingridient)
class IngridientAdmin(admin.ModelAdmin):
    # list_display = ('pk', 'email', 'first_name', 'last_name', 'bio', 'role')
    # search_fields = ('first_name', 'last_name')
    # list_filter = ('role',)
    # list_editable = ('role',)
    empty_value_display = '-пусто-'


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    # list_display = ('pk', 'email', 'first_name', 'last_name', 'bio', 'role')
    # search_fields = ('first_name', 'last_name')
    # list_filter = ('role',)
    # list_editable = ('role',)
    empty_value_display = '-пусто-'
