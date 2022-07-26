from os.path import join
from pathlib import Path

import pdfkit
from django.db.models import Sum
from django.http import FileResponse

from foodgram.settings import MEDIA_ROOT
from recipes import models


def create_and_download_cart(request):
    recipes = request.user.shoppingcart.recipe.all()
    amount_of_ingredients = (models.AmountOfIngredient.objects.
                             filter(recipe__in=recipes))
    recipe_ingredients = (amount_of_ingredients.values('ingredient').
                          annotate(ingredient_amount=Sum('amount')))
    shopping_cart = ('<head><meta charset="utf-8"></head>' +
                     'Foodgram<br>Shopping list:<br>')
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
            '<br>'
        )
    dir_path = join(MEDIA_ROOT, 'shopping_carts', request.user.username)
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    filename = 'shopping_cart.pdf'
    path = join(dir_path, filename)
    pdfkit.from_string(shopping_cart, path)
    response = FileResponse(
        open(path, 'rb'),
        as_attachment=True,
        filename=filename
    )
    return response
