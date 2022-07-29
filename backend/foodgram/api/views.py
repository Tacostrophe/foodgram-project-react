from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes import models
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from . import pagination, serializers
from .filters import RecipeFilters
from .methods import create_and_download_cart
from .permissions import OwnerOrReadOnly

User = get_user_model()


def to_list(self, request, instance, list):
    exist = list.filter(id=instance.id).exists()
    if request.method == 'POST':
        if (exist):
            raise ValidationError('Already in list')
        list.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        if (not exist):
            raise ValidationError('No such objects in list')
        list.remove(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тэгов"""
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    queryset = models.Recipe.objects.all()
    pagination_class = pagination.CustomPageNumberPagination
    permission_classes = (OwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.RecipePassiveSerializer
        else:
            return serializers.RecipeActiveSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=serializers.RecipePassiveShortSerializer
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(models.Recipe, pk=pk)
        favorite = request.user.favorite.recipe
        return to_list(self, request, recipe, favorite)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=serializers.RecipePassiveShortSerializer
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(models.Recipe, pk=pk)
        shopping_cart = request.user.shoppingcart.recipe
        return to_list(self, request, recipe, shopping_cart)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        return create_and_download_cart(request)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов"""
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        queryset = models.Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__startswith=name)
        return queryset


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователя"""
    pagination_class = pagination.CustomPageNumberPagination

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=serializers.SubscriptionSerializer
    )
    def subscriptions(self, request):
        queryset = request.user.subscription.following.all()
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
        subscription = request.user.subscription.following
        if (request.user == following):
            raise ValidationError('Can\'t interact with yourself')
        return to_list(self, request, following, subscription)
