from django.contrib.auth import authenticate, get_user_model
from djoser.compat import get_user_email_field_name
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer
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
