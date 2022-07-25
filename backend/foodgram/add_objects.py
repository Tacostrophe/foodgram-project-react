import json

from recipes import models

MODELS_DICT = {
    models.Ingredient: ['name', 'measurement_unit'],
    models.Tag: ['name', 'color', 'slug'],
}

for model in MODELS_DICT.keys():
    if model.objects.all().exists():
        print(model.__name__ + 's already exists')
        continue
    else:
        with open(f'../../data/{model.__name__.lower()}s.json') as file:
            data = json.load(file)
            for element in data:
                attrs = []
                for attr in MODELS_DICT[model]:
                    attrs.append(element[attr])
                model.objects.create(**attrs)
        print(model.__name__ + 's added to bd')
