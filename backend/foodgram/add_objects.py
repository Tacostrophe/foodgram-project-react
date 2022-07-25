import json

from recipes import models

if models.Ingredient.objects.all().exists():
    print('Ingredients already exists')
else:
    with open(f'../../data/ingredients.json') as file:
        data = json.load(file)
        models.Ingredient.objects.bulk_create(
            [models.Ingredient(
                name=element['name'],
                measurement_unit=element['measurement_unit']
            ) for element in data])
    print('Ingredients added to bd')

if models.Tag.objects.all().exists():
    print('Tags already exists')
else:
    with open(f'../../data/tags.json') as file:
        data = json.load(file)
        models.Tag.objects.bulk_create(
            [models.Tag(
                name=element['name'],
                color=element['color'],
                slug=element['slug']
            ) for element in data])
    print('Tags added to bd')
