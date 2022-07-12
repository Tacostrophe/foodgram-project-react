from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters

from recipes import models
from . import serializers

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тэгов"""
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None


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
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


# class CustomUserViewSet(UserViewSet):
#     pagination_class = pagination.PageNumberPagination
#     pagination_class = pagination.CustomPageNumberPagination
#     page_size = 6
