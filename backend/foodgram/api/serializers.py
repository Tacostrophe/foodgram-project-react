from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes import models
from rest_framework import serializers

from . import fields
from .validators import tags_list_validator

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
        return (request.user.is_authenticated and
                models.Subscription.objects.filter(following=obj,
                                                   user=request.user).exists())

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


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', None)
        if recipes_limit:
            response = (models.Recipe.objects.
                        filter(author=obj)[:int(recipes_limit)])
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


class AmountOfIngredientSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = models.AmountOfIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = AmountOfIngredientSerializer(
        many=True,
        read_only=True,
        required=False,
    )
    tags = TagSerializer(
        many=True,
        read_only=True,
        required=False,
    )
    image = fields.Base64FileField(required=True, allow_null=False)
    name = serializers.CharField(min_length=1, max_length=200, required=True, )
    text = serializers.CharField(min_length=1, required=True)
    cooking_time = serializers.IntegerField(required=True, )
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    def validate(self, data):
        print('Were in validate')
        request = self.context.get('request')
        tags_list = request.data.get('tags')
        error_dict = dict()
        # validate tags
        if (not tags_list):
            error_dict['tags'] = 'This field is required'
        elif not isinstance(tags_list, list):
            error_dict['tags'] = (
                'Invalid data. ' +
                f'Expected a list, but got {type(tags_list)}.'
            )
        elif ((models.Tag.objects.filter(id__in=tags_list).
               count()) != len(tags_list)):
            error_dict['tags'] = (
                'Ivalid data. ' +
                'Tags can\'t repeat and should exist'
            )
        else:
            for tag_id in tags_list:
                if not isinstance(tag_id, int):
                    error_dict['tags'] = (
                        'Invalid data. ' +
                        'Expected a list of int,' +
                        f'but list contain {type(tag_id)}.'
                    )
                    break
        ingredients_list = request.data.get('ingredients')
        # validate ingredients
        if (not ingredients_list and request.method == 'POST'):
            error_dict['ingredients'] = 'This field is required'
        elif (not isinstance(ingredients_list, list)):
            error_dict['ingredients'] = (
                'Invalid data. ' +
                f'Expected a list, but got {type(ingredients_list)}.'
            )
        else:
            ingredient_id_list = []
            for ingredient_dict in ingredients_list:
                ingredient_id = ingredient_dict.get('id')
                ingredient_amount = ingredient_dict.get('amount')
                # validate ingredient id
                if (not ingredient_id):
                    ingredient_error = error_dict.get('ingredient')
                    if (not ingredient_error):
                        error_dict['ingredients'] = dict()
                    error_dict['ingredients']['id'] = (
                        'This field is required.'
                    )
                    break
                elif (not isinstance(ingredient_id, int)):
                    ingredient_error = error_dict.get('ingredient')
                    if (not ingredient_error):
                        error_dict['ingredients'] = dict()
                    error_dict['ingredients']['id'] = (
                        'Invalid data. ' +
                        f'Expected a int, but got {type(ingredient_id)}.'
                    )
                    break
                elif (ingredient_id in ingredient_id_list):
                    ingredient_error = error_dict.get('ingredient')
                    if (not ingredient_error):
                        error_dict['ingredients'] = dict()
                    error_dict['ingredients']['id'] = (
                        'Ingredients can\'t repeat'
                    )
                    break
                else:
                    ingredient_id_list.append(ingredient_id)
                # validate ingredient amount
                if (not ingredient_amount):
                    ingredient_error = error_dict.get('ingredient')
                    if (not ingredient_error):
                        error_dict['ingredients'] = dict()
                    error_dict['ingredients']['amount'] = (
                        'This field is required.'
                    )
                    break
                elif (not isinstance(ingredient_amount, int)):
                    ingredient_error = error_dict.get('ingredient')
                    if (not ingredient_error):
                        error_dict['ingredients'] = dict()
                    error_dict['ingredients']['amount'] = (
                        'Invalid data. ' +
                        f'Expected a int, but got {type(ingredient_amount)}.'
                    )
                    break
                elif (ingredient_amount < 1):
                    ingredient_error = error_dict.get('ingredient')
                    if (not ingredient_error):
                        error_dict['ingredients'] = dict()
                    error_dict['ingredients']['amount'] = (
                        'Invalid data. ' +
                        'Should be greater or equal 1.'
                    )
                    break
            if ((models.Ingredient.objects.filter(id__in=ingredient_id_list).
                 count()) != len(ingredient_id_list)):
                error_dict['ingredients'] = dict()
                error_dict['ingredients']['id'] = (
                    'Some of ingredients don\'t exist'
                )
        if error_dict:
            raise serializers.ValidationError(error_dict)
        return data

    def add_tags_and_ingredients(self, request, recipe):
        tags_list = request.data.get('tags')
        ingredients_list = request.data.get('ingredients')
        try:
            tags = models.Tag.objects.filter(id__in=tags_list)
            recipe.tags.set(tags)
        except Exception as error:
            if (request.method == 'POST'):
                recipe.delete()
            raise serializers.ValidationError(
                f"Tags caused exception:{error}"
            )
        try:
            for ingredient_dict in ingredients_list:
                amountless_ingredient = get_object_or_404(
                    models.Ingredient,
                    id=ingredient_dict['id']
                )
                models.AmountOfIngredient.objects.create(
                    ingredient=amountless_ingredient,
                    recipe=recipe,
                    amount=ingredient_dict['amount']
                )
            recipe_ingredients = (models.AmountOfIngredient.objects.
                                  filter(recipe=recipe))
            recipe.ingredients.set(recipe_ingredients)
        except Exception as error:
            if (request.method == 'POST'):
                recipe.delete()
            raise serializers.ValidationError(
                f"Ingredients caused exception: {error}"
            )
        return recipe

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        recipe = models.Recipe.objects.create(author=author, **validated_data)
        recipe = self.add_tags_and_ingredients(request, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.image = validated_data.get('image')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        request = self.context.get('request')
        old_ingredients = instance.ingredients_amount.all()
        ingredients_id_list = []
        for ingredient in old_ingredients:
            ingredients_id_list.append(ingredient.id)
        instance = self.add_tags_and_ingredients(request, instance)
        models.AmountOfIngredient.objects.filter(id__in=ingredients_id_list).delete()
        instance.save()
        return instance


    class Meta:
        model = models.Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')
