from django_filters import FilterSet, rest_framework

from recipes import models


class RecipeFilters(FilterSet):
    tags = rest_framework.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = rest_framework.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = rest_framework.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if(value == 1):
                return queryset.filter(favorites__user=user)
            elif(value == 0):
                return queryset.exclude(favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if(value == 1):
                return queryset.filter(shoppingcarts__user=user)
            elif(value == 0):
                return queryset.exclude(shoppingcarts__user=user)
        return queryset

    class Meta:
        model = models.Recipe
        fields = ['author', 'tags', 'is_favorited']
