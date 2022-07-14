from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes import models
from rest_framework import serializers

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'color', 'slug']
        model = models.Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = models.Ingredient


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            'password',
            'username',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if (request.user.is_authenticated and
            models.Subscription.objects.filter(following=obj,
                                               user=request.user).exists()):
            return True
        return False

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            'username',
            'is_subscribed'
        )


class SubsRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionListSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', None)
        if recipes_limit:
            response = models.Recipe.objects.filter(author=obj)[:int(recipes_limit)]
        else:
            response = models.Recipe.objects.filter(author=obj)
        return response

    def get_recipes_count(self, obj):
        return models.Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            'username',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        depth = 2
