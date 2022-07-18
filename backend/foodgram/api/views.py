from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .permissions import OwnerOrReadOnly
from .filters import RecipeFilters
from recipes import models
from . import serializers, pagination

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тэгов"""
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    # pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    serializer_class = serializers.RecipeSerializer
    serializer = serializers.RecipeSerializer(partial=False)
    pagination_class = pagination.CustomPageNumberPagination
    permission_classes = (OwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('author', 'tags')
    filterset_class = RecipeFilters

    def get_queryset(self):
        return models.Recipe.objects.all()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=serializers.SubsRecipesSerializer
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(models.Recipe, pk=pk)
        favorite = models.Favorite.objects.filter(user=request.user,
                                                  recipe=recipe)
        if request.method == 'POST':
            if (favorite.exists()):
                raise ValidationError('Can\'t like it two times')
            models.Favorite(user=request.user, recipe=recipe).save()
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if (not favorite.exists()):
                raise ValidationError('Don\'t like it already')
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet():
    """Вьюсет для списка покупок"""


class FavoriteViewSet():
    """Вьюсет для избранного"""


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
        serializer_class=serializers.SubscriptionSerializer
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

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=serializers.SubscriptionSerializer
    )
    def subscribe(self, request, id=None):
        following = get_object_or_404(User, pk=id)
        subscription = models.Subscription.objects.filter(user=request.user,
                                                          following=following)
        if request.method == 'POST':
            if (request.user == following or subscription.exists()):
                raise ValidationError('Can\'t subscribe to yourself' +
                                      ' or already subscribed')
            models.Subscription(user=request.user, following=following).save()
            serializer = self.get_serializer(following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if (not subscription.exists()):
                raise ValidationError('Not subscribed')
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
