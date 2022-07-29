from os.path import join
from pathlib import Path
from wsgiref.util import FileWrapper

from django.db.models import Sum
from django.http import HttpResponse
from foodgram.settings import MEDIA_ROOT
from recipes import models


def create_and_download_cart(request):
    recipes = request.user.shoppingcart.recipe.all()
    amount_of_ingredients = (models.AmountOfIngredient.objects.
                             filter(recipe__in=recipes))
    recipe_ingredients = (amount_of_ingredients.values('ingredient').
                          annotate(ingredient_amount=Sum('amount')))
    shopping_cart = 'Foodgram\n_______________\n'
    for recipe_ingredient in recipe_ingredients:
        ingredient = (models.Ingredient.objects.
                      get(id=recipe_ingredient['ingredient']))
        shopping_cart += (
            '   - ' +
            ingredient.name +
            ' - ' +
            str(recipe_ingredient.get('ingredient_amount')) +
            ' ' +
            ingredient.measurement_unit +
            '\n'
        )
    dir_path = join(MEDIA_ROOT, 'shopping_carts', request.user.username)
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    filename = 'shopping_cart.txt'
    path = join(dir_path, filename)
    f = open(path, 'w')
    f.write(shopping_cart)
    f.close()
    response = HttpResponse(
        FileWrapper(open(path, 'rb')),
        content_type='application/plain'
    )
    return response
