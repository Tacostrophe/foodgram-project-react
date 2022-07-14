from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes import models
from . import serializers, pagination

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тэгов"""
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    # pagination_class = None


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
    # pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователя"""
    pagination_class = pagination.CustomPageNumberPagination

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=serializers.SubscriptionListSerializer
    )
    def subscriptions(self, request):
        subsctiptions_qs = request.user.followings.all()
        queryset = User.objects.filter(followers__in=subsctiptions_qs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
