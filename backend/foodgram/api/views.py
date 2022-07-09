from rest_framework import viewsets

from . import serializers
from recipes import models


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тэгов"""
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class RecipeViewSet():
    """Вьюсет для рецептов"""


class ShoppingCartViewSet():
    """Вьюсет для списка покупок"""


class FavoriteViewSet():
    """Вьюсет для избранного"""


class SubscriptionViewSet():
    """Вьюсет для подписок"""


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
