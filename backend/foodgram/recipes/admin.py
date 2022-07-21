from django.contrib import admin

from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'email')
    list_filter = ('first_name', 'email',)
    empty_value_display = '-пусто-'


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(models.AmountOfIngredient)
class AmountOfIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredient', 'recipe', 'amount')
    empty_value_display = '-пусто-'


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'author',
        'fans'
        )
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    @admin.display(empty_value='-пусто-')
    def fans(self, obj):
        return obj.favorite.count()


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user',)


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user',)


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', )
