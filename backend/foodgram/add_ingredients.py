import json
from recipes import models


if (not models.Ingredient.objects.all().exists()):
    with open('../../data/ingredients.json') as file:
        data = json.load(file)
        for ingredient in data:
            models.Ingredient.objects.create(
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit'])
    print('ingredients added to bd')
else:
    print('ingredients already exists')
