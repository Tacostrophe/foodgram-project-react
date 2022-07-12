from django.contrib import admin

from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'email')
    # search_fields = ('first_name', 'last_name')
    list_filter = ('first_name', 'email',)
    # list_editable = ('role',)
    empty_value_display = '-пусто-'


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    # list_display = ('pk', 'email', 'first_name', 'last_name', 'bio', 'role')
    # search_fields = ('first_name', 'last_name')
    # list_filter = ('role',)
    # list_editable = ('role',)
    empty_value_display = '-пусто-'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    # search_fields = ('first_name', 'last_name')
    list_filter = ('name',)
    # list_editable = ('role',)
    empty_value_display = '-пусто-'


@admin.register(models.AmountOfIngridient)
class AmountOfIngridientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingridient', 'recipe', 'amount')
    # search_fields = ('first_name', 'last_name')
    # list_filter = ('name',)
    # list_editable = ('role',)
    empty_value_display = '-пусто-'


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', )
    # search_fields = ('first_name', 'last_name')
    list_filter = ('name', 'author', 'tags')
    # list_editable = ()
    empty_value_display = '-пусто-'


@admin.register(models.Subscribtion)
class SubscribtionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following', )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe', )


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe', )
