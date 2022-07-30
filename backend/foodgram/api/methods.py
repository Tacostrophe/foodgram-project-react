from os.path import join
from pathlib import Path

from django.db.models import Sum
from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas

from foodgram.settings import BASE_DIR, MEDIA_ROOT
from recipes import models


def create_and_download_cart(request):
    recipes = request.user.shoppingcart.recipe.all()
    amount_of_ingredients = (models.AmountOfIngredient.objects.
                             filter(recipe__in=recipes))
    recipe_ingredients = (amount_of_ingredients.values('ingredient').
                          annotate(ingredient_amount=Sum('amount')))
    dir_path = join(MEDIA_ROOT, 'shopping_carts', request.user.username)
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    filename = 'shopping_cart.pdf'
    file_path = join(dir_path, filename)
    shopping_cart = canvas.Canvas(file_path)
    font_path = join(BASE_DIR, 'fonts', 'FreeSans.ttf')
    pdfmetrics.registerFont(ttfonts.TTFont('FreeSans', font_path))
    shopping_cart.setFont('FreeSans', 12)
    text = shopping_cart.beginText(40, 780)
    text.textLine('Foodgram')
    text.textLine('_______________')
    text.textLine('Список покупок:')
    for recipe_ingredient in recipe_ingredients:
        ingredient = (models.Ingredient.objects.
                      get(id=recipe_ingredient['ingredient']))
        ingredient_line = (
            '   - ' +
            ingredient.name +
            ' - ' +
            str(recipe_ingredient.get('ingredient_amount')) +
            ' ' +
            ingredient.measurement_unit
        )
        text.textLine(ingredient_line)
    shopping_cart.drawText(text)
    shopping_cart.save()
    return FileResponse(open(file_path, 'rb'),
                        as_attachment=True,
                        filename=filename
                        )
