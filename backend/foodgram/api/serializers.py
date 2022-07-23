from django.contrib.auth import get_user_model
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
        return (request.user.is_authenticated and
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
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
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


class RecipePassiveSerializer(RecipePassiveShortSerializer):
    author = CustomUserSerializer(
        read_only=True,
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
        return (request.user.is_authenticated and
                request.user.favorite.recipe.filter(id=obj.id).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and
                request.user.shoppingcart.recipe.filter(id=obj.id).exists())

    class Meta:
        model = models.Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time',  'is_favorited', 'is_in_shopping_cart'
        )


class RecipeActiveSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True,
    )
    image = fields.Base64FileField()

    class Meta:
        model = models.Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients',
            'name', 'image',
            'text', 'cooking_time'
        )

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

    def create_recipe_ingredients(self, recipe, ingredients):
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

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(
            **validated_data,
            author=request.user)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(recipe, ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        print(validated_data)
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        new_tags = validated_data.get('tags')
        instance.tags.set(new_tags)
        instance.ingredients.all().delete()
        new_ingredients = validated_data.get('ingredients')
        self.create_recipe_ingredients(instance, new_ingredients)
        instance.image.storage.delete(instance.image.name)
        instance.image = validated_data.get('image')
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipePassiveSerializer(instance=instance,
                                             context={'request': request})
        return serializer.data
