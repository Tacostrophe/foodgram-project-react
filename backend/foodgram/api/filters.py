from django_filters import FilterSet, rest_framework
from recipes import models


class RecipeFilters(FilterSet):
    tags = rest_framework.AllValuesMultipleFilter(field_name='tags__slug')
    # is_favorited = rest_framework.NumberFilter(method=filter_favorit)

    class Meta:
        model = models.Recipe
        fields = ['author', 'tags']
