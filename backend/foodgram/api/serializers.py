from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.transaction import atomic
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes import models
from rest_framework import serializers

from . import fields

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
        return (request and request.user.is_authenticated and
                request.user.subscription.following.filter(id=obj.id).exists())

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            'username',
            'is_subscribed'
        )


class RecipePassiveShortSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=1, max_length=200, required=True)
    image = serializers.FileField(required=True)
    cooking_time = serializers.IntegerField(required=True)

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', None)
        if recipes_limit:
            recipes = (models.Recipe.objects.
                       filter(author=obj)[:int(recipes_limit)])
        else:
            recipes = models.Recipe.objects.filter(author=obj)
        return RecipePassiveShortSerializer(recipes, many=True).data

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
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = models.AmountOfIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all(),
        required=True
    )

    class Meta:
        model = models.AmountOfIngredient
        fields = ('id', 'amount')

    def to_representation(self, instance):
        return AmountOfIngredientSerializer(instance)


class RecipePassiveSerializer(RecipePassiveShortSerializer):
    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = AmountOfIngredientSerializer(
        many=True,
    )
    tags = TagSerializer(
        many=True,
    )
    text = serializers.CharField(min_length=1, required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated and
                request.user.favorite.recipe.filter(id=obj.id).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated and
                request.user.shoppingcart.recipe.filter(id=obj.id).exists())

    class Meta:
        model = models.Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time',  'is_favorited', 'is_in_shopping_cart'
        )


class RecipeActiveSerializer(RecipePassiveSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True,
    )
    image = fields.Base64FileField()

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Ensure this value is greater than or equal to 1.'
            )
        return value

    def validate_tags(self, value):
        tags_id_list = []
        for tag in value:
            tag_id = tag.id
            if tag_id in tags_id_list:
                raise serializers.ValidationError(
                    'Ensure tags in list are unique'
                )
            tags_id_list.append(tag_id)
        return value

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(
            **validated_data,
            author=request.user)
        recipe.tags.set(tags)
        try:
            models.AmountOfIngredient.objects.bulk_create(
                models.AmountOfIngredient(
                    ingredient=ingredient['id'],
                    amount=ingredient['amount'],
                    recipe=recipe
                ) for ingredient in ingredients
            )
        except Exception as error_message:
            if('UNIQUE constraint failed' in str(error_message)):
                message = {
                    'ingredients': 'Ensure ingredients in list are unique'
                }
            else:
                message = {'ingredients': error_message}
            raise serializers.ValidationError(message)
        return recipe

    def update(self, instance, validated_date):
        return super().update()

    # def to_representation(self, instance):
    #     return RecipePassiveSerializer(instance, request=self.context.get('request')).data

    #     print('Were in validate')
    #     request = self.context.get('request')
    #     tags_list = request.data.get('tags')
    #     error_dict = dict()
    #     # validate tags
    #     if (not tags_list):
    #         error_dict['tags'] = 'This field is required'
    #     elif not isinstance(tags_list, list):
    #         error_dict['tags'] = (
    #             'Invalid data. ' +
    #             f'Expected a list, but got {type(tags_list)}.'
    #         )
    #     elif ((models.Tag.objects.filter(id__in=tags_list).
    #            count()) != len(tags_list)):
    #         error_dict['tags'] = (
    #             'Ivalid data. ' +
    #             'Tags can\'t repeat and should exist'
    #         )
    #     else:
    #         for tag_id in tags_list:
    #             if not isinstance(tag_id, int):
    #                 error_dict['tags'] = (
    #                     'Invalid data. ' +
    #                     'Expected a list of int,' +
    #                     f'but list contain {type(tag_id)}.'
    #                 )
    #                 break
    #     ingredients_list = request.data.get('ingredients')
    #     # validate ingredients
    #     if (not ingredients_list and request.method == 'POST'):
    #         error_dict['ingredients'] = 'This field is required'
    #     elif (not isinstance(ingredients_list, list)):
    #         error_dict['ingredients'] = (
    #             'Invalid data. ' +
    #             f'Expected a list, but got {type(ingredients_list)}.'
    #         )
    #     else:
    #         ingredient_id_list = []
    #         for ingredient_dict in ingredients_list:
    #             ingredient_id = ingredient_dict.get('id')
    #             ingredient_amount = ingredient_dict.get('amount')
    #             # validate ingredient id
    #             if (not ingredient_id):
    #                 ingredient_error = error_dict.get('ingredient')
    #                 if (not ingredient_error):
    #                     error_dict['ingredients'] = dict()
    #                 error_dict['ingredients']['id'] = (
    #                     'This field is required.'
    #                 )
    #                 break
    #             elif (not isinstance(ingredient_id, int)):
    #                 ingredient_error = error_dict.get('ingredient')
    #                 if (not ingredient_error):
    #                     error_dict['ingredients'] = dict()
    #                 error_dict['ingredients']['id'] = (
    #                     'Invalid data. ' +
    #                     f'Expected a int, but got {type(ingredient_id)}.'
    #                 )
    #                 break
    #             elif (ingredient_id in ingredient_id_list):
    #                 ingredient_error = error_dict.get('ingredient')
    #                 if (not ingredient_error):
    #                     error_dict['ingredients'] = dict()
    #                 error_dict['ingredients']['id'] = (
    #                     'Ingredients can\'t repeat'
    #                 )
    #                 break
    #             else:
    #                 ingredient_id_list.append(ingredient_id)
    #             # validate ingredient amount
    #             if (not ingredient_amount):
    #                 ingredient_error = error_dict.get('ingredient')
    #                 if (not ingredient_error):
    #                     error_dict['ingredients'] = dict()
    #                 error_dict['ingredients']['amount'] = (
    #                     'This field is required.'
    #                 )
    #                 break
    #             elif (not isinstance(ingredient_amount, int)):
    #                 ingredient_error = error_dict.get('ingredient')
    #                 if (not ingredient_error):
    #                     error_dict['ingredients'] = dict()
    #                 error_dict['ingredients']['amount'] = (
    #                     'Invalid data. ' +
    #                     f'Expected a int, but got {type(ingredient_amount)}.'
    #                 )
    #                 break
    #             elif (ingredient_amount < 1):
    #                 ingredient_error = error_dict.get('ingredient')
    #                 if (not ingredient_error):
    #                     error_dict['ingredients'] = dict()
    #                 error_dict['ingredients']['amount'] = (
    #                     'Invalid data. ' +
    #                     'Should be greater or equal 1.'
    #                 )
    #                 break
    #         if ((models.Ingredient.objects.filter(id__in=ingredient_id_list).
    #              count()) != len(ingredient_id_list)):
    #             error_dict['ingredients'] = dict()
    #             error_dict['ingredients']['id'] = (
    #                 'Some of ingredients don\'t exist'
    #             )
    #     if error_dict:
    #         raise serializers.ValidationError(error_dict)
    #     return data
# 
    # def add_tags_and_ingredients(self, request, recipe):
    #     tags_list = request.data.get('tags')
    #     ingredients_list = request.data.get('ingredients')
    #     try:
    #         tags = models.Tag.objects.filter(id__in=tags_list)
    #         recipe.tags.set(tags)
    #     except Exception as error:
    #         if (request.method == 'POST'):
    #             recipe.delete()
    #         raise serializers.ValidationError(
    #             f"Tags caused exception:{error}"
    #         )
    #     try:
    #         for ingredient_dict in ingredients_list:
    #             amountless_ingredient = get_object_or_404(
    #                 models.Ingredient,
    #                 id=ingredient_dict['id']
    #             )
    #             models.AmountOfIngredient.objects.create(
    #                 ingredient=amountless_ingredient,
    #                 recipe=recipe,
    #                 amount=ingredient_dict['amount']
    #             )
    #         recipe_ingredients = (models.AmountOfIngredient.objects.
    #                               filter(recipe=recipe))
    #         recipe.ingredients.set(recipe_ingredients)
    #     except Exception as error:
    #         if (request.method == 'POST'):
    #             recipe.delete()
    #         raise serializers.ValidationError(
    #             f"Ingredients caused exception: {error}"
    #         )
    #     return recipe
# 
    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     author = request.user
    #     recipe = models.Recipe.objects.create(author=author, **validated_data)
    #     recipe = self.add_tags_and_ingredients(request, recipe)
    #     return recipe
# 
    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name')
    #     instance.image = validated_data.get('image')
    #     instance.text = validated_data.get('text')
    #     instance.cooking_time = validated_data.get('cooking_time')
    #     request = self.context.get('request')
    #     old_ingredients = instance.ingredients_amount.all()
    #     ingredients_id_list = []
    #     for ingredient in old_ingredients:
    #         ingredients_id_list.append(ingredient.id)
    #     instance = self.add_tags_and_ingredients(request, instance)
    #     models.AmountOfIngredient.objects.filter(id__in=ingredients_id_list).delete()
    #     instance.save()
    #     return instance
